#!/bin/bash

# Start uptime monitor
python3 /app/monitor/monitor.py &

# Run security scan every 10 mins
while true
do
  python3 /app/monitor/security_scan.py
  sleep 600
done &

# Start dashboard
node /app/dashboard/server.js