# Data Logger Server

This is a web server to receive data transmissions from OTT netDL data loggers.

[Further documentation is located on Google Drive](https://drive.google.com/drive/folders/1IRdglNE6KCT73QKDvFtLjPB4bubs6hZQ?usp=sharing).

This is a Flask application that receives HTTP POST requests containing XML data in the body (defined by `OTT_Data.xsd`). The HTTP request must have the correct query parameters, as expected to be sent by the data logger. The received data is saved to disk with no pre-processing. A response is sent as defined by `OTT_Response.xsd`.

Files will be written to the disk in a directory specified by `settings.DATA_DIR`. Note that, in order to write to disk atomically (to avoid partial writes) temporary files will also be created in that directory with a file suffix of `settings.TEMP_SUFFIX`.

There are various configuration files in this directory that are useful as a reference when configuring a Linux machine.

The code assumes that all the data loggers are configured identically. The channel numbers should be configured to record the same type of measurement. The order of the channels should also be consistent.

## Overview

The web server will forward web requests via a socket to the web application using the WSGI specification (in this case uWSGI is used). The application is built using the Flask web framework.

See this tutorial: [How To Serve Flask Applications with uWSGI and Nginx on Ubuntu 20.04](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uwsgi-and-nginx-on-ubuntu-20-04)

The web application sits behind a reverse proxy and listens over Hypertext Transfer Protocol Secure (HTTPS) on port 443. You can run a quick check like so. (Optionally, use the `--insecure` option if the SSL certificate isn't configured yet.)

```bash
curl --head  https://ufdlsrv01.shef.ac.uk
```

The server is configured to listen for the transmissions sent by the OTT data loggers, with the appropriate type of encryption and authentication mechanisms.

## Retrieve data

Data are stored in the directories specified in `data_logger_server/settings.py`. The default target directory is `/home/uflo/dlsrv/senddata`. This directory may be configured as a symbolic link to a network mounted volume so that the research data is stored in a separate location and not on the virtual machine running the web server.

This directory is owned by the `uflo` user so you may not have permission to view it without escalating to superuser privileges using `sudo`, or log in as that user:

```bash
sudo su - uflo --shell /bin/bash
```

Run this command to list the contents of this directory:

```bash
ls -l /home/uflo/dlsrv/senddata
```

Data are stored in nested directories, one per day, in the format `<action>/YYYY/MM` where the action is `senddata` for a data transmission, for example `/home/uflo/data/rawData/dlsrv/senddata/2020/10/22`.

To view data files retrieved on a certain day:

```bash
# List data files, sort chronologically
ls -lt /home/uflo/dlsrv/senddata/2020/10/22
total 1980
-rw-------. 1 uflo uflo 44074 Oct 22  2020 0000452891_2020-10-22T00+01+06.209619
-rw-------. 1 uflo uflo 44075 Oct 22  2020 0000452891_2020-10-22T00+16+06.045141
-rw-------. 1 uflo uflo 44075 Oct 22  2020 0000452891_2020-10-22T00+31+02.943406
-rw-------. 1 uflo uflo 44075 Oct 22  2020 0000452891_2020-10-22T00+46+06.192728
```

Columns:
* Data logger device identifier
* Channel number
* Date
* Time
* Measured value

# Installation

See `install.sh`.

The encryption keys will need to be installed in the location specified in the NGINX configuration file.

Ensure the service will run as a non-privileged user and is a member of the specified group.

The configuration, code and socket files must all be pointed to correctly by each configuration file.

To run the installation script:

```bash
cd ~/urban_flows/data_logger_server
sudo sh install.sh

# Restart NGINX (optional)
sudo nginx -s reload
```

## Web server

Run `nginx -t` to check the configuration is valid.

The web server is configured to run as a load balancer and reverse proxy in front of the application. The communication between the two is implemented using WSGI and a Unix socket file.

### Authentication

The NGINX web server uses basic HTTP authentication. See: [Basic Authentication documentation](https://docs.nginx.com/nginx/admin-guide/security-controls/configuring-http-basic-authentication/).

```bash
# Install htpasswd
apt install apache2-utils

# Create a new password file and a first user
# (only use -c the first time to create a new file)
sudo htpasswd -c /etc/nginx/.htpasswd dl001
```

Add a new user or change existing password (omit -c flag)

```bash
sudo htpasswd /etc/nginx/.htpasswd dl002
```

To validate a user's password:

```bash
sudo htpasswd -v /etc/nginx/.htpasswd dl001
```

# Maintenance

* Update OS packages
  * `sudo apt update`
  * `sudo apt upgrade`
* Update Python packages
  * Check for security vulnerabilities using [Safety](https://pyup.io/safety/).
    * Run the dependency check: `/opt/data_logger_server/venv/bin/safety check`
  * Check for updates: `/opt/data_logger_server/venv/bin/pip list --outdated`
* SSL certificate renewal
  * Check expiration date: `cat /etc/nginx/ssl/ufdlsrv01.shef.ac.uk.crt | openssl x509 -noout -enddate`
* Delete old logs
  * `sudo journalctl --vacuum-size=500M`

# Operation

The server is designed to run as a `systemd` service.

## WSGI service

The web application may be controlled via the service using `systemctl` as follows:

```bash
sudo systemctl start data_logger_server
sudo systemctl stop data_logger_server
sudo systemctl restart data_logger_server
```

Monitoring:

```bash
sudo systemctl status data_logger_server
sudo journalctl -u data_logger_server --since "1 hour ago"

# View uWSGI logs
sudo tail /var/log/uwsgi/uwsgi.log
```

It's also possible to run the WSGI service in isolation as follows:

```bash
uwsgi --socket 0.0.0.0:5000 --protocol=http -w wsgi:app
```

## Web server

```bash
systemctl restart nginx
```

View logs:

```bash
tail /var/log/nginx/error.log
# View access logs live
tail --follow /var/log/nginx/access.log
```

### Testing

You can test that the web server is responding like so:

```bash
curl -u <username>:<password> https://ufdlsrv01.shef.ac.uk/server-status
```

This will test the Flask app is responding:

```bash
curl -u <username>:<password> https://ufdlsrv01.shef.ac.uk/ping
```

The following is a command to make a HTTP POST request which sends a file to the server, simulating the action of a real data logger.

```bash
# Send specified file via HTTP POST method
curl -X POST -u username:password -d @transmission_test/senddata.xml "https://ufdlsrv01/ott/?stationid=1234&action=senddata"
```

# Appendix: Generating a self-signed certificate

Digital Ocean [OpenSSL Essentials: Working with SSL Certificates, Private Keys and CSRs](https://www.digitalocean.com/community/tutorials/openssl-essentials-working-with-ssl-certificates-private-keys-and-csrs#generating-ssl-certificates).

This will generate a CSR, private and public keys.

```bash
# Generate Certificate Signing Requests (CSR)
openssl req \
       -newkey rsa:2048 -nodes -keyout ufdlsrv01.shef.ac.uk.key \
       -out ufdlsrv01.shef.ac.uk.csr \
	   -subj "/C=GB/ST=England/L=Sheffield/O=The University of Sheffield/CN=ufdlsrv01.shef.ac.uk"

# Generate a self-signed certificate from private key and CSR
openssl x509 \
       -signkey ufdlsrv01.shef.ac.uk.key \
       -in ufdlsrv01.shef.ac.uk.csr \
       -req -out ufdlsrv01.shef.ac.uk.crt -days 365
```
