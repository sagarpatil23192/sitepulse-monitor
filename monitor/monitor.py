import requests
import time
import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

URL = os.getenv("TARGET_URL")

LOG_FILE = "/app/logs/monitor.log"
STATE_FILE = "/app/monitor/fail_state.txt"
MAX_FAILS = 3
EMAIL = os.getenv("ALERT_EMAIL")
PASSWORD = os.getenv("ALERT_PASSWORD")


def send_alert():
    msg = MIMEText(f"{URL} is DOWN!")
    msg["Subject"] = "Website Monitor Alert"
    msg["From"] = EMAIL
    msg["To"] = EMAIL
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(EMAIL, PASSWORD)
    server.send_message(msg)
    server.quit()


def log_result(status, response_time):
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.now()},{status},{response_time}\n")


def get_fail_count():
    if not os.path.exists(STATE_FILE):
        return 0
    with open(STATE_FILE) as f:
        return int(f.read())


def save_fail_count(count):
    with open(STATE_FILE, "w") as f:
        f.write(str(count))


while True:
    fail_count = get_fail_count()
    try:

        start = time.time()
        r = requests.get(URL, timeout=10)
        response = round(time.time() - start, 3)
        log_result(r.status_code, response)
        if r.status_code == 200:
            fail_count = 0
        else:
            fail_count += 1

    except:
        log_result("ERROR", 0)
        fail_count += 1

    if fail_count >= MAX_FAILS:
        #Set the EMAIL and PASSWORD env and enable the send_alert functionality
        #send_alert()
        fail_count = 0

    save_fail_count(fail_count)
    time.sleep(60)