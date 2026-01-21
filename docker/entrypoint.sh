#!/bin/sh
set -eu

crontab /etc/cron.d/telegram-forwarder

touch /var/log/cron.log

cron

tail -f /var/log/cron.log
