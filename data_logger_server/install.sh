#!/bin/sh

# Urban Flows Observatory
# OTT Data Logger Web Server installation script

# Define target directories
DEST_DIR="/opt/data_logger_server"
VENV_DIR="$DEST_DIR/venv"
DATA_DIR="/home/uflo/data/rawData/dlsrv"

# Install OS packages
apt update
apt-get upgrade --yes
apt-get install --yes nginx python3.9 python3.9-venv python3.9-dev apache2-utils build-essential

echo "Installing web server..."

# Install WGSI as a service
cp wsgi/data_logger_server.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable data_logger_server

# Create a directory to store the socket file
mkdir -p /run/dlsrv
chown www-data:www-data /run/dlsrv
chmod 0660 /run/dlsrv
chmod g+s /run/dlsrv # new files inherit group ownership

# Install application files
mkdir --parents --verbose $DEST_DIR
cp --recursive ./* $DEST_DIR

# Create Python virtual environment
python3.9 -m venv $VENV_DIR
# Install Python packages
$VENV_DIR/bin/pip install -r requirements.txt

# Data destination
mkdir --parents --verbose $DATA_DIR

# Install machine-specific settings
mv --force $DEST_DIR/data_logger_server/settings_prod.py $DEST_DIR/data_logger_server/settings_local.py

# Create a shared directory to store the socket file
echo "Installing WSGI configuration..."
cp wsgi/data_logger_server.conf /etc/tmpfiles.d

# uWSGI log file
mkdir --parents /var/log/uwsgi
chown www-data:root /var/log/uwsgi

# Install NGINX configuration files
echo "Installing NGINX configuration..."
cp --recursive --verbose nginx /etc
