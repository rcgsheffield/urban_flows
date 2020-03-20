#!/bin/bash

SRC_DIR=/home/sa_cs1jsth/data_logger_server
DEST_DIR=/home/uflo/data_logger_server

cd $SRC_DIR

echo "Installing web server..."

# Install WGSI as a service
cp wsgi/data_logger_server.service /etc/systemd/system/
systemctl enable data_logger_server

# Copy files to uflo user home directory
mkdir --parents $DEST_DIR
cp * $DEST_DIR --recursive
chown uflo:uflo $DEST_DIR --recursive

# Install machine-specific settings
mv $DEST_DIR/data_logger_server/settings_prod.py $DEST_DIR/data_logger_server/settings_local.py --force

# Create a shared directory to store the socket file
echo "Installing WSGI configuration..."
cp wsgi/data_logger_server.conf /etc/tmpfiles.d

# uWSGI log file
mkdir --parents /var/log/uwsgi
chown uflo:root /var/log/uwsgi

# Install NGINX configuration files
echo "Installing NGINX configuration..."
cp nginx/nginx.conf /etc/nginx/
cp nginx/ufdlsrv01.shef.ac.uk.conf /etc/nginx/conf.d/

# The web server user must also have access to the WSGI socket
usermod -aG nginx uflo
usermod -aG nginx nginx
