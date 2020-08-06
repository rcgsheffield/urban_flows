cp nginx/sites-available/* nginx/sites-available --verbose
ln -s /etc/nginx/sites-available/sheffsense.uk /etc/nginx/sites-enabled/sheffsense.uk --verbose
cp pm2/pm2-sheffsense.service /etc/systemd/system/pm2-sheffsense.service --verbose
