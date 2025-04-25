#!/bin/bash

# Install system dependencies for OpenCV
apt-get update
apt-get install -y libgl1-mesa-glx libglib2.0-0

# Then start your application
gunicorn -w 4 -b 0.0.0.0:8000 app:app
