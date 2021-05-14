#!/usr/bin/env sh

TARGET_DIR=/opt/awesome
VENV_DIR=$TARGET_DIR/venv

# Exit immediately if a command exits with a non-zero status
set -e

echo "Installing production settings..."
cp --verbose settings_prod.py settings_local.py

echo "Installing Python packages"
python3 -m venv $VENV_DIR
$VENV_DIR/bin/pip install --requirement requirements.txt

echo "Installing data bridge into $TARGET_DIR..."
mkdir --parents --verbose $TARGET_DIR
sudo cp --recursive --verbose * $TARGET_DIR

echo "Installing systemd units..."
cp --verbose systemd/databridge.service /etc/systemd/system/databridge.service
cp --verbose systemd/databridge.timer /etc/systemd/system/databridge.timer
# load any changes to systemd units
systemctl daemon-reload
