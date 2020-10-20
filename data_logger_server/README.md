# Data Logger Server

This is a web server to receive data transmissions from OTT netDL data loggers.

This is a Flask application that receives HTTP POST requests containing XML data in the body (defined by `OTT_Data.xsd`). The HTTP request must have the correct query parameters, as expected to be sent by the data logger. The received data is saved to disk with no pre-processing. A response is sent as defined by `OTT_Response.xsd`.

Files will be written to the disk in a directory specified by `settings.DATA_DIR`. Note that, in order to write to disk atomically (to avoid partial writes) temporary files will also be created in that directory with a file suffix of `settings.TEMP_SUFFIX`.

There are various configuration files in this directory that are useful as a reference when configuring a Linux machine.

The code assumes that all the data loggers are configured identically. The channel numbers should be configured to record the same type of measurement. The order of the channels should also be consistent.

## Overview

The web server will forward web requests via a socket to the web application using the WSGI specification (in this case uWSGI is used). The application is built using the Flask web framework.

# Installation

See `install.sh`.

I followed [this guide](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uswgi-and-nginx-on-ubuntu-18-04). (Assuming NGINX is installed.)

Install the basic required software:

```bash
$ apt update
$ apt install python3-dev python3-venv
$ apt install git
```

Create a virtual environment with the required packages:

```bash
$ git clone <REPO_URL>
$ cd ~/data_logger_server
$ python3 -m venv dl_srv_env
$ source dl_srv_env/bin/activate
$ pip install wheel
$ pip install -r requirements.txt
```

To configure the web server as a service, install the configuration file as follows:

```bash
$ cp data_logger_server.service /etc/systemd/system/
```

Ensure the service will run as a non-privileged user and is a member of the
specified group.

The configuration, code and socket files must all be pointed to correctly by each
configuration file.

## Web server

Install the configuration file and create a symbolic link to enable this virtual host.

```bash
$ cp nginx/ufdlsrv01.shef.ac.uk.conf /etc/nginx/conf.d/

# Enable NGINX site:
#$ ln -s /etc/nginx/sites-available/data_logger_server /etc/nginx/sites-enabled
#$ rm /etc/nginx/sites-enabled/default
```

# Operation

The server is designed to run as a `systemd` service.

## WSGI service

Control the service using `systemctl` as follows:

```bash
$ systemctl start data_logger_server
$ systemctl stop data_logger_server
$ systemctl restart data_logger_server
$ systemctl status data_logger_server
$ journalctl -u data_logger_server

# View uWSGI logs
$ tail /var/log/uwsgi/uwsgi.log
```

It's also possible to run the WSGI service in isolation as follows:

```bash
$ uwsgi --socket 0.0.0.0:5000 --protocol=http -w wsgi:app
```

## Web server

```bash
$ systemctl restart nginx
$ tail /var/log/nginx/error.log
# View access logs live
$ tail -f /var/log/nginx/access.log
```

## Testing

The following is a Curl command for HTTP POST:

```bash
# Send specified file via HTTP POST method
$ curl -X POST -d @test_transmission.xml "http://localhost:80/ott/?stationid=1234&action=senddata"
```

# Authentication

NGINX HTTP [Basic Authentication documentation](https://docs.nginx.com/nginx/admin-guide/security-controls/configuring-http-basic-authentication/).

```bash
# Install htpasswd
$ yum install httpd-tools
# Create a new password file and a first user (only use -c the first time)
$ htpasswd -c /etc/nginx/.htpasswd dl001
# Add a new user (omit -c flag)
$ htpasswd /etc/nginx/.htpasswd dl002
```



# Appendix A: Centos installation

See `install.sh`.

I performed these steps in my own user area then copied the files to `/home/uflo/`.

```bash
$ yum install git nginx python3-devel gcc
$ useradd uflo
# Install /home/uflo/.ssh/authorized_keys
$ cd ~/data_logger_server

# Python virtual environment
$ python3 -m venv dl_srv_env
$ source dl_srv_env/bin/activate
$ pip install --upgrade pip
$ pip install wheel  # requires python3-devel to compile
$ pip install -r requirements.txt

# Install WGSI as a service
$ cp data_logger_server.service /etc/systemd/system/
$ systemctl enable data_logger_server

# Copy files to uflo user home directory
$ cp data_logger_server/ /home/uflo/ --recursive
$ chown uflo:uflo /home/uflo/data_logger_server --recursive

# The web server user must also have access to the WSGI socket
$ usermod -aG nginx uflo
$ usermod -aG nginx nginx

# Create a shared directory to store the socket file
$ mkdir /run/dlsrv
$ chown uflo:nginx /run/dlsrv
$ chmod 770 /run/dlsrv
$ chmod g+s /run/dlsrv # new files inherit group ownership

# Install NGINX configuration files
$ cp nginx/nginx.conf /etc/nginx/
$ cp nginx/ufdlsrv01.shef.ac.uk.conf /etc/nginx/conf.d/
```

Restart services (or reboot) to implement changes.

```bash
$ systemctl restart data_logger_server
$ systemctl restart nginx
```

Useful commands:

```bash
# View NGINX error logs
$ tail /var/log/nginx/error.log
```

# Appendix B: Generating a self-signed certificate

Digital Ocean [OpenSSL Essentials: Working with SSL Certificates, Private Keys and CSRs](https://www.digitalocean.com/community/tutorials/openssl-essentials-working-with-ssl-certificates-private-keys-and-csrs#generating-ssl-certificates).

This will generate a CSR, private and public keys (with the default 30-day expiry time.)

```bash
# Generate Certificate Signing Requests (CSR)
$ openssl req \
       -newkey rsa:2048 -nodes -keyout ufdlsrv01.shef.ac.uk.key \
       -out ufdlsrv01.shef.ac.uk.csr \
	   -subj "/C=GB/ST=England/L=Sheffield/O=The University of Sheffield/CN=ufdlsrv01.shef.ac.uk"

# Generate a self-signed certificate from private key and CSR
$ openssl x509 \
       -signkey ufdlsrv01.shef.ac.uk.key \
       -in ufdlsrv01.shef.ac.uk.csr \
       -req -out ufdlsrv01.shef.ac.uk.crt
```

# Appendix C: File glossary

The following directories and configuration files are present:

* `data_logger_server` contains the Flask application
* `data_logger_server.service` is the `systemd` configuration file
* `requirements.txt`  is the dependencies for this Python package
* `nginx/` contains NGINX configuration files
* `transmission_test` A script to test sending data via HTTP POST to the server (similar to `curl`)

