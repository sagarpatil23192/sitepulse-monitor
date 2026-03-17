import requests
import ssl
import socket
import json
import os
from urllib.parse import urlparse
from datetime import datetime

URL = os.getenv("TARGET_URL")
OUTPUT = "/app/logs/security.json"

# -----------------------------
# 1. Security Headers Check
# -----------------------------
def check_headers():
    try:
        r = requests.get(URL, timeout=10)
        headers = r.headers

        required = {
            "content-security-policy": False,
            "x-frame-options": False,
            "strict-transport-security": False,
            "x-content-type-options": False
        }

        for h in headers.keys():
            key = h.lower()
            if key in required:
                required[key] = True

        return required

    except Exception as e:
        return {"error": str(e)}


# -----------------------------
# 2. SSL Expiry Check
# -----------------------------
def check_ssl():
    try:
        hostname = urlparse(URL).hostname

        ctx = ssl.create_default_context()

        with socket.create_connection((hostname, 443)) as sock:
            with ctx.wrap_socket(sock, server_hostname=hostname) as ssock:

                cert = ssock.getpeercert()

                expiry_date = datetime.strptime(
                    cert['notAfter'],
                    "%b %d %H:%M:%S %Y %Z"
                )

                days_left = (expiry_date - datetime.utcnow()).days

                return {
                    "expires_in_days": days_left
                }

    except Exception as e:
        return {"error": str(e)}


# -----------------------------
# 3. OWASP ZAP Baseline
# -----------------------------
def run_zap_scan():
    try:
        report_file = "/app/logs/zap_report.json"

        cmd = f"""
        docker run --rm \
        -v /app/logs:/zap/wrk \
        owasp/zap2docker-stable \
        zap-baseline.py \
        -t {URL} \
        -J zap_report.json
        """

        os.system(cmd)

        if os.path.exists(report_file):
            with open(report_file) as f:
                return json.load(f)

        return {"status": "No report generated"}

    except Exception as e:
        return {"error": str(e)}


# -----------------------------
# Scoring Logic
# -----------------------------
def calculate_score(headers, ssl_data, zap_data):

    score = 100
    risks = []

    # Header penalties
    for key, value in headers.items():
        if not value:
            score -= 10
            risks.append(f"Missing {key}")

    # SSL penalty
    if "expires_in_days" in ssl_data:
        if ssl_data["expires_in_days"] < 30:
            score -= 20
            risks.append("SSL expiring soon")

    # ZAP alerts
    if isinstance(zap_data, dict) and "site" in zap_data:
        alerts = zap_data.get("site", [{}])[0].get("alerts", [])
        if alerts:
            score -= min(len(alerts) * 5, 30)
            risks.append(f"{len(alerts)} vulnerabilities found")

    return score, risks


# -----------------------------
# Main Runner
# -----------------------------
def run_scan():

    headers = check_headers()
    ssl_data = check_ssl()
    zap_data = run_zap_scan()

    score, risks = calculate_score(headers, ssl_data, zap_data)

    result = {
        "timestamp": str(datetime.utcnow()),
        "headers": headers,
        "ssl": ssl_data,
        "zap": zap_data,
        "score": score,
        "risks": risks
    }

    with open(OUTPUT, "w") as f:
        json.dump(result, f, indent=2)


if __name__ == "__main__":
    run_scan()