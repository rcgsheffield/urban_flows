# DEFRA Air Quality data pipeline

This is a data pipeline to ingest data from the Department for Environment, Food and Rural Affairs (DEFRA)
[Atom Download Services](https://uk-air.defra.gov.uk/data/atom-dls/) into the
[Urban Flows Observatory](https://urbanflows.ac.uk/) data warehouse.

## Overview

### Pipeline overview

These are the steps in the process:

1. `download.py`: Automatically download specified DEFRA data for a particular year and save the source data files to disk.
2. `convert.py`: Extract rows of data from the XML files and convert to CSV format
3. `clean.py`: Remove bad data and parse data types
4. `todb.py`: Aggregate and prepare CSV data, ready to be converted into netCDF format 

Data files are stored subdirectories within the `data` directory, specified in `settings.py`.

The XML resources found by following a trail of links as follows:

  1. Annual ATOM list of resources i.e. data sets for each location.
  2. A specific site e.g. "GB Fixed Observations for Barnsley Gawber (BAR3) in 2020" contains several "Observations".
  3. Data values for that observation for a particular year are stored within an XML document.
  
### Auxiliary code
 
The various utilities used within the pipeline are organised as follows:
 
 * `http_session.py`: A HTTP session to communicate with the web server
 * `parsers`: Module containing XML and ATOM feed parsers to scrape, navigate and extract data
 * `metadata.py`: Used to generate meta-data from downloaded data only
 * `assets.py`: Tools to interface with the Urban Observatory meta-data repository
 * `settings.py`: Configuration parameters, including meta-data options 
 * `run.py`: Execute the entire pipeline for every year available (for testing)
 
 ## Installation
 
 *TODO*
 
 Edit `settings.py` to change the configuration.
 
 ## Usage
 
 The server provides data in yearly collections.
 
 To run the pipeline, run the four scripts in order:
 
```bash
$ python download.py --year 2020
$ python convert.py --year 2020
$ python clean.py --year 2020
$ python todb.py --year 2020
 ```
 
 To generate metadata, run `python metadata.py`.
 This will only extract metadata from already-downloaded data files.