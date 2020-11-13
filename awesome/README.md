# Awesome Portal: Data Bridge

This is a bridge used to put data and metadata from the Urban Flows Observatory into the [Awesome web portal](http://ufportal.shef.ac.uk/api/) via its API (see [Awesome Portal API Docs](https://ufapidocs.clients.builtonawesomeness.co.uk/)).

# Usage

```bash
$ cd awesome
$ python . --help
```

# Air Quality Index

DEFRA [What is the Daily Air Quality Index?](https://uk-air.defra.gov.uk/air-pollution/daqi?view=more-info)

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