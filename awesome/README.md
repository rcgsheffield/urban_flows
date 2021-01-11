# Awesome Portal: Data Bridge

This is a bridge used to put data and metadata from the Urban Flows Observatory into the [Awesome web portal](http://ufportal.shef.ac.uk/) via its API (see [Awesome Portal API Docs](https://ufapidocs.clients.builtonawesomeness.co.uk/)).

# Installation

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

The metadata used to describe the sensor readings on each system is defined by a collection of objects. There are loose mappings between the two metadata systems.

## Urban Flows Observatory

* Site: geographical location
  * Sensor: a collection of detectors that may exist at one site at a time
    * Detector: a data channel with a certain type1 of measurement
* Pair: one sensor at a location for a certain time period

## Awesome Portal

* Location
  * Sensor
* Reading Category: a group of reading types
  * Reading Type: a physical phenomenon

## Maps

* 

# Awesome API

Readings by sensor `/sensors/{id}/readings`