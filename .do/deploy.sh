#!/bin/bash
# Install FFmpeg for DigitalOcean App Platform

echo "-----> Installing FFmpeg"
apt-get update
apt-get install -y ffmpeg
echo "-----> FFmpeg installed successfully"
