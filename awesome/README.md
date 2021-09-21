# Awesome Portal: Data Bridge

This is a bridge used to put data and metadata from the Urban Flows Observatory into the [Awesome web portal](http://portal.sheffield.ac.uk/) via its API (see [Awesome Portal API Docs](https://ufapidocs.clients.builtonawesomeness.co.uk/)).

# Requirements

A relatively modern Linux operating system (such as Ubuntu 18.04 LTS and Python 3.6).

# Installation

Use `install.sh` to copy the relevant files:

```bash
sudo --set-home sh install.sh
```

The service is controlled using `systemd` and is defined in `databridge.service`. To control the timer:

```bash
# load any changes to systemd units
sudo systemctl daemon-reload
# Enable the timer
sudo systemctl enable databridge.timer
sudo systemctl start databridge.timer
```

To monitor:

```bash

# View service status
systemctl status databridge.timer
systemctl status databridge.service
# View all timers (shows next execution time)
systemctl list-timers --all
```

The logs for the `systemd` units are stored using `journalctl`.

```bash
# View logs
journalctl -u databridge.service
# View logs for today
journalctl -u databridge.service --since "$(date -I)"
# Filter logs by time
journalctl -u databridge.service --since "2021-04-26 00:00:00" --until "2021-04-26 01:00:00"
```

By default, the authentication token used to access the Awesome portal API is stored in a text file at `~/configs/awesome_token.txt` as specified in `settings.DEFAULT_TOKEN_PATH`.

# Usage

To view the available commands, run:

```bash
$ python . --help
```

To run the data bridge in verbose mode, execute:

```bash
$ python . -v
```

## Syncing

The purpose of this data bridge is to sync the data and metadata between the Urban Flows Observatory (UFO) system and the Awesome portal system, where the prior is the main, original data to be copied to the latter.

### Metadata

Metadata objects are first translated between UFO objects (sites, sensors, etc.) and their counterparts on the Awesome portal (locations, readings, etc.). Objects in the remote system are either updated, created or deleted to ensure the two systems match up.

### Data

Rows of data retrieved from the UFO database are converted into "readings" (individual measurements or values) and are uploaded in chunks of 100 to the remote system. Each time the data bridge runs it uses a timestamp to determine which point in the source data stream to begin (a point in time.) This "bookmark" timestamp may be retrieved from the remote system (if available) or stored in a local timestamp.

# Air Quality Index

The Air Quality Index (AQI) is calculated by aggregating several metrics over a given averaging time at a location, with thresholds for each of the air quality bands. See: DEFRA [What is the Daily Air Quality Index?](https://uk-air.defra.gov.uk/air-pollution/daqi?view=more-info)

## Unit conversion

The AQI standards are specified in terms of a set of specific pollutants with thresholds in given units (typically ug/m^3). In the AQI code (`aqi.py`) each reading is converted to the appropriate unit by selecting a conversion factor (or ratio) with which to multiply that value. These factors are specified as a map from the source units to the target units, for example in `aqi.daqi.DailyAirQualityIndex.CONVERSION_FACTOR` which is a dictionary with nested keys for the source pollutant and units respectively.

The result is a time-averaged AQI score as a function of time for each location which can be synced to the remote database by the code in `sync.sync_aqi_readings`.

# Glossary

The metadata used to describe the sensor readings on each system is defined by a collection of objects. There are loose mappings between the two metadata systems, where the left-hand side is for the original UFO database and the right-hand side is the new Awesome system.

The code to convert between object types is in `maps.py`.

* Site -> Location: geographical place with positional coordinates
* Sensor -> Sensor: a collection of detectors that may exist at one site at a time
  * Detector -> Reading Type: a data channel with a certain type of measurement such as a physical phenomenon or metric.
  * Family -> Sensor type
* Reading Category: a group of reading types e.g. "Air Quality" or "Atmosphere"
* Pair: a deployment of one sensor at a site for a certain time period

## Acronyms

* UFO = Urban Flows Observatory

# Awesome API

This API consists of Python objects that map to objects on the remote system.

## HTTP session

The remote system is accessed by establishing a HTTP session:

```python
import http_session

session = http_session.PortalSession(token='My API access token')
```

This session is passed to the Python objects that inherit from `objects.AwesomeObject` that represent the classes of object on the remote system. These objects use this system to perform read/write operations on that database. See the Awesome API documentation for more details of these objects.

To list all the objects of a certain type, pass the HTTP session to the `AwesomeObject.list` class method, which will generate an iterable collection of objects.

```python
import objects

for sensor_type in objects.SensorType.list_iter(session):
    pass
```

To retrieve the data for a single object, pass its identifier number into the constructor:

```python
sensor_type = objects.SensorType(1)
data = sensor_type.query(session)
```

Some classes have behaviour specific to that type of object, such as `Sensor.add_sensor_category` etc.

# Development

The default `settings_local.py` in this repository should configure the system to operate in the development environment.

## Virtual environment

You can create a virtual environment to run this code using Conda or another Python virtual environment tool such as `venv`. The instructions to do this may be found online.

```bash
# Create a virtual environment in a directory called awesome
python -m venv awesome

# Activate the environment (commands for Linux or Windows)
#source <venv>/bin/activate
#<venv>\Scripts\activate.bat

# Install packages
pip install -r requirements.txt
```



## Unit tests

To execute the automated unit tests, run this command:

```bash
python -m unittest --failfast --verbose
```

# Maintenance

## Upgrade packages

Generic operating system upgrades should be performed regularly.

```bash
sudo apt update
sudo apt upgrade
```

Check [PyPI](https://pypi.org/) to see if the packages listed in `requirements.txt` are outdated.

## Clear logs

View reboots:

```bash
journalctl --list-boots
```

Clear system logs:

```bash
# View journal disk usage
journalctl --disk-usage
# Retain last 3 days
journalctl --vacuum-time=3d
```

