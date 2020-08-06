cp nginx/sites-available/* nginx/sites-available --verbose
ln -s /etc/nginx/sites-available/sheffsense.uk /etc/nginx/sites-enabled/sheffsense.uk
cp pm2/pm2-sheffsense.service /etc/systemd/service/pm2-sheffsense.service
