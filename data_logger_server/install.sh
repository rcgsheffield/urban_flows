#!/bin/sh

# Urban Flows Observatory
# OTT Data Logger Web Server installation script

# Define target directories
DEST_DIR="/opt/data_logger_server"
VENV_DIR="$DEST_DIR/venv"
DATA_DIR="/home/uflo/data/rawData/dlsrv"
RELEASE=$(lsb_release -sc)
KEY="ABF5BD827BD9BF62"

# Exit immediately if a command exits with a non-zero status
set -e

# Install OS packages
# Get latest stable version of NGINX
# https://www.nginx.com/resources/wiki/start/topics/tutorials/install/#official-debian-ubuntu-packages
echo "deb https://nginx.org/packages/ubuntu/ $RELEASE nginx" > /etc/apt/sources.list.d/nginx.list
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys $KEY
apt update
apt-get install --yes nginx python3.9 python3.9-venv  apache2-utils
# Install build tools to compile uWSGI
apt-get install --yes python3-wheel python3.9-dev build-essential
apt-get upgrade --yes

echo "Installing web server..."

# Install WGSI as a service
cp wsgi/data_logger_server.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable data_logger_server

# Create uflo user and add to nginx group
useradd uflo
usermod -a -G nginx uflo

# Install application files
mkdir --parents --verbose $DEST_DIR
cp --recursive ./data_logger_server/* $DEST_DIR
mkdir -pv /opt/wsgi
cp --recursive ./wsgi/* /opt/wsgi

# Create Python virtual environment
python3.9 -m venv $VENV_DIR
# Update pip
$VENV_DIR/bin/pip install pip --upgrade
# Install Python packages
$VENV_DIR/bin/pip install wheel
$VENV_DIR/bin/pip install -r requirements.txt

# Data destination
mkdir --parents --verbose $DATA_DIR

# Install machine-specific settings
mv --force $DEST_DIR/settings_prod.py $DEST_DIR/settings_local.py

# Install NGINX configuration files
echo "Installing NGINX configuration..."
cp --recursive --verbose nginx /etc

# Data targets
mkdir -pv $DATA_DIR/senddata
mkdir -pv $DATA_DIR/sendalarm
chown -R uflo:nginx $DATA_DIR $DATA_DIR/senddata $DATA_DIR/sendalarm
chmod 775 $DATA_DIR $DATA_DIR/senddata $DATA_DIR/sendalarm
