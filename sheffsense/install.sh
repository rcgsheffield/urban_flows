# Joe Heffer 11/6/2020

# How To Set Up a Node.js Application for Production on Ubuntu 18.04
# https://www.digitalocean.com/community/tutorials/how-to-set-up-a-node-js-application-for-production-on-ubuntu-18-04

# First I installed node.js and NPM.

# Generate CSR
openssl req -new -key shefsense.key -out sheffsense.csr

# Install SheffSense:
git clone https://github.com/dambem/ClimateMonitorV2.git

# Install code into system
sudo cp -rv ClimateMonitorV2/ClimateMonitorV2 /opt/sheffsense

# Create a user that will run the service
sudo useradd sheffsense

# Use PM2 to run the app as a service
sudo npm install pm2@latest -g

# Run the app as the sheffsense user to create the .pm2 configuration
# in /home/sheffsense/.pm2
pm2 start /opt/sheffsense/app.js

# Create a startup script
sudo env PATH=$PATH:/usr/bin pm2 startup systemd -u sheffsense --hp /home/sheffsense

# Save the PM2 process list and corresponding environments:
pm2 save
#[PM2] Saving current process list...
#[PM2] Successfully saved in /home/sheffsense/.pm2/dump.pm2

# View service status:
systemctl status pm2-sheffsense

reboot
# Check it's listening:
lsof -i -P -n | grep sheffsense

# Install web proxy server (NGINX)
sudo apt install nginx

# Web app configuration files
cp nginx/sites-available/* /etc/nginx/sites-available --verbose
ln -s /etc/nginx/sites-available/sheffsense.uk /etc/nginx/sites-enabled/sheffsense.uk --verbose --force
cp pm2/pm2-sheffsense.service /etc/systemd/system/pm2-sheffsense.service --verbose