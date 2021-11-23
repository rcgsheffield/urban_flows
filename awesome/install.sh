#!/usr/bin/env sh

PYTHON_VERSION=python3.9
TARGET_DIR=/opt/awesome
VENV_DIR=$TARGET_DIR/venv
PYTHON_BINARY=$VENV_DIR/bin/$PYTHON_VERSION

# Exit immediately if a command exits with a non-zero status
set -e

# Create Python virtual environment
echo "Installing Python packages"
/usr/bin/$PYTHON_VERSION -m venv $VENV_DIR
# Use this version of Python
$PYTHON_BINARY -m venv $VENV_DIR --upgrade
$PYTHON_BINARY -m pip install --requirement requirements.txt

echo "Installing data bridge into $TARGET_DIR..."
mkdir --parents --verbose $TARGET_DIR
sudo cp --recursive ./* $TARGET_DIR

echo "Installing production settings..."
cp --verbose $TARGET_DIR/settings_prod.py $TARGET_DIR/settings_local.py

echo "Installing systemd units..."
cp --verbose systemd/databridge.service /etc/systemd/system/databridge.service
cp --verbose systemd/databridge.timer /etc/systemd/system/databridge.timer
# load any changes to systemd units
systemctl daemon-reload
