#!/bin/bash
# Update package list
apt-get update

# Install necessary dependencies
apt-get install -y libgl1 libglib2.0-0

# Start the application using gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
