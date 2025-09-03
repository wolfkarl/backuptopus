#!/bin/bash
set +x 

# make sure cron can access current environment
printenv > .env

export TASK="/app/backuptopus/.venv/bin/python /app/backuptopus/main.py"
echo "$CRON $TASK >> /var/log/cron.log 2>&1" > /etc/cron.d/backuptopus
crontab /etc/cron.d/backuptopus
touch /var/log/cron.log

cron && tail -f /var/log/cron.log