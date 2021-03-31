#!/usr/bin/env sh

TARGET_DIR=/opt/awesome

echo "Installing production settings..."
cp --verbose settings_prod.py settings_local.py

echo "Installing data bridge into $TARGET_DIR..."
mkdir -pv $TARGET_DIR
sudo cp -rv * $TARGET_DIR

echo "Installing systemd units..."
cp --verbose databridge.service /etc/systemd/system/databridge.service
cp --verbose databridge.timer /etc/systemd/system/databridge.timer
