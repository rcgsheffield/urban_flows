# SheffSense Climate Monitor

[SheffSense](https://github.com/dambem/ClimateMonitorV2) Sheffield Climate Monitor is a Node.js web application.

# Installation

The service runs on the `ufshefsense.shef.ac.uk` virtual machine and is publicly available at `https://sheffsense.urbanflows.ac.uk`. This is a node.js application managed by the PM2 process manager behind an NGINX reverse proxy. The process runs as the service user `sheffsense`.

See: Digital Ocean [How To Set Up a Node.js Application for Production on Ubuntu 18.04](https://www.digitalocean.com/community/tutorials/how-to-set-up-a-node-js-application-for-production-on-ubuntu-18-04)

## Maintenance

Regular security patches must be applied. See [update.txt](update.txt).

# Usage

## Node app

```bash
# View service status
$ systemctl status pm2-sheffsense

# Check it's listening
$ lsof -i -P -n | grep sheffsense

# Restart service
$ sudo systemctl restart pm2-sheffsense
```

## Web server

NGINX reverse proxy server.

```bash
# Check configuration files
$ sudo nginx -t

# Check service status
$ systemctl status nginx

# View error logs
$ sudo tail /var/log/nginx/error.log

# Restart service
$ sudo systemctl restart nginx
```
