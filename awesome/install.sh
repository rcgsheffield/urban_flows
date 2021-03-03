crontab -u uflo crontab.txt

echo "Installing production settings..."
cp --verbose settings_prod.py settings_local.py

# Install systemd service
cp --verbose databridge.service /etc/systemd/system/databridge.service
cp --verbose databridge.timer /etc/systemd/system/databridge.timer
