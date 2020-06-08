# DEFRA Sensor Observation Service

This is a harvester to retrieve data from the DEFRA UK-AIR [Sensor Observation Service](https://uk-air.defra.gov.uk/data/about_sos) via their API using the key-value pair (KVP) binding.

## Installation

See `settings.py`.

## Usage

To see the usage docs, run

```bash
$ python __main__.py --help
$ python metadata.py --help
```

The code works by initializing a HTTP session with the server and running a query to retrieve data using a temporal filter. The response XML is parsed to get a collection of `Observation` objects, each of which has contains data values for a certain physical location (`Station`) and metric (`SamplingPoint` or observed property).

The data is filtered to a fixed list of `SamplingPoint` items in order to filter geographically. The output columns are fixed to ensure consistent data shape.

The data are loaded into a Pandas data frame to be cleaned and aggregated ready for output. The output is ready for the UFO script which converts into NetCDF format.

### Updating sampling features

Data is retrieved from a fixed list of stations/detectors as defined in `settings.SAMPLING_FEATURES`. To get an updated list of sampling features, run `python metadata.py --features` which will find all sensors within the area specified by `settings.REGION_OF_INTEREST`.

### Retrieving metadata

By running `python metadata.py --met` the code will iterate over the sampling points specified in `settings.SAMPLING_FEATURES` and download the metadata for all the relevant stations. Asset configuration files will be generated in the `assets/` directory.

## Issues

* There seems to be a bug with the SOS API, see: Issue [52North SOS #793](https://github.com/52North/SOS/issues/793). This means we can't do a spatial filter when querying the API. The developers have been informed so this may have been fixed.