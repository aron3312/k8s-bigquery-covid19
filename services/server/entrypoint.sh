#!/bin/sh
/etc/init.d/cron start
gunicorn -b 0.0.0.0:5000 manage:app
