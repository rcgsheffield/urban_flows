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