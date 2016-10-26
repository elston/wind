#!/usr/bin/env bash
FLASK_ENV=PRODUCTION env/bin/gunicorn -b 127.0.0.1:12080 --workers 4 --preload --timeout 1000 webapp:app
