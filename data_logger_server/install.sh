#!/bin/sh

# Urban Flows Observatory
# OTT Data Logger Web Server installation script

# Define target directories
DEST_DIR="/opt/data_logger_server"
VENV_DIR="$DEST_DIR/venv"
DATA_DIR="/home/uflo/data/rawData/dlsrv"

# Exit immediately if a command exits with a non-zero status
set -e

# Install OS packages
apt update
apt-get upgrade --yes
apt-get install --yes nginx python3.9 python3.9-venv  apache2-utils
# Install build tools to compile uWSGI
apt-get install --yes python3-wheel python3.9-dev build-essential

echo "Installing web server..."

# Install WGSI as a service
cp wsgi/data_logger_server.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable data_logger_server

# Create a directory to store the socket file
mkdir -p /run/dlsrv
chown www-data:www-data /run/dlsrv
chmod 770 /run/dlsrv

# Install application files
mkdir --parents --verbose $DEST_DIR
cp --recursive ./data_logger_server/* $DEST_DIR
mkdir -pv /opt/wsgi
cp --recursive ./wsgi/* /opt/wsgi

# Create Python virtual environment
python3.9 -m venv $VENV_DIR
# Install Python packages
$VENV_DIR/bin/pip install wheel
$VENV_DIR/bin/pip install -r requirements.txt

# Data destination
mkdir --parents --verbose $DATA_DIR

# Install machine-specific settings
mv --force $DEST_DIR/settings_prod.py $DEST_DIR/settings_local.py

# Create a shared directory to store the socket file
echo "Installing WSGI configuration..."
cp wsgi/data_logger_server.conf /etc/tmpfiles.d

# Install NGINX configuration files
echo "Installing NGINX configuration..."
cp --recursive --verbose nginx /etc

# Data targets
mkdir -pv $DATA_DIR/senddata
mkdir -pv $DATA_DIR/sendalarm
