# DEFRA Sensor Observation Service Harvester

This is a harvester module to ingest air pollution measurements from the [DEFRA UK-AIR Sensor Observation Services](https://uk-air.defra.gov.uk/data/about_sos) (SOS) for the [Urban Flow Observatory](https://uk-air.defra.gov.uk/data/about_sos) at The University of Sheffield.

## Installation

See `environment.yml`.

## Usage

See `python pipeline.py --help`.

The following example call the module with parameters specified by inline arguments: 

```bash
$ python pipeline.py -d 2020-02-15 -od test.csv
```

## Tests

Tests are located in the `tests` module.

To run the tests, execute `python -m unittest tests`.

## Metadata

The metadata objects are:

* Air quality monitoring Stations: A facility with one or more sampling points measuring ambient air quality pollutant concentrations e.g. [Sheffield Devonshire Green ](https://uk-air.defra.gov.uk/data/so/Station_GB1027A)
	- There are several `station` objects for each geographical location, each contains one measurement e.g. PM10.
	- The 52deg North REST API doesn't map to the DEFRA [Spatial Objects Register](https://uk-air.defra.gov.uk/data/so/about).
* Time series
