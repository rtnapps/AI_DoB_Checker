#!/bin/bash
apt-get update
apt-get install -y libgl1
gunicorn -w 4 -b 0.0.0.0:8000 app:app
