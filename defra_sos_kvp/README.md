# DEFRA Sensor Observation Service

This is a harvester to retrieve data from the DEFRA UK-AIR [Sensor Observation Service](https://uk-air.defra.gov.uk/data/about_sos) via their API using the key-value pair (KVP) binding.

## Installation

See `settings.py` for configuration.

## Usage

To see the usage docs, run

```bash
$ python . --help
$ python metadata.py --help
```

### Data query

The code works by initializing a HTTP session with the server and running a query to retrieve data using a temporal filter.  The `GetObservation` API endpoint is called with the date and the sampling feature as a parameter.

The response XML is parsed to get a collection of `Observation` objects, each of which has contains data values for a certain physical location (`Station`) and metric (`SamplingFeature` or observed property). For more information about these objects, see the DEFRA [Spatial Object Register](https://uk-air.defra.gov.uk/data/so/about/).

The data are filtered to a fixed list of `SamplingFeature` items in order to filter geographically. The output columns are fixed to ensure consistent data shape.

The data are cleaned and aggregated ready for output. The output is ready for the UFO script which converts into NetCDF format.

### Updating sampling features

Data are retrieved from a fixed list of stations/detectors as defined in `settings.SAMPLING_FEATURES`. To get an updated list of sampling features, run `python metadata.py --features` which will find all sensors within the area specified by `settings.REGION_OF_INTEREST`.

### Retrieving metadata

By running `python metadata.py --meta` the code will iterate over the sampling points using a geographical filter and download the metadata for all the relevant stations. Asset configuration files will be generated in the `assets/` directory.

### Spatial filtering

The bounding box used for spatial filtering is defined using a GeoJSON object specified in `settings.BOUNDING_BOX`. This should contain a GeoJSON polygon definition for a rectangle covering the region of interest.

## Issues

* There seems to be a bug with the SOS API, see: Issue [52North SOS #793](https://github.com/52North/SOS/issues/793). This means we can't do a spatial filter when querying the API. The developers have been informed so this may have been fixed. See `docs/DEFRA UK-AIR SOS spatial filter issue.eml`.