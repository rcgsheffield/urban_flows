# The Things Network Data Pipeline

This is a pipeline to ingest data from [The Things Network](https://www.thethingsnetwork.org/) which may store data in
its [Data Storage integration](https://www.thethingsnetwork.org/docs/applications/storage/) usiong a database, where
the data is accessible using a web API.

The data are transformed into a format appropriate for the [Urban Flows Observatory](https://urbanflows.ac.uk/).

## Useful links

* `mj-ttgopaxcounter` data storage [API documentation](https://mj-ttgopaxcounter.data.thethingsnetwork.org/)

## Installation

To create a virtual environment with the required packages, create an Conda environment as follows:

```bash
conda create --name <my_environment> --file environment.yml
```

The pipeline is configured using the values specified in `the_things_network.cfg`.

## Usage

To get help:

```bash
$ python ufttn --help
$ python ufttn.metadata --help
```
