#  

# Environment Agency flood data harvester

This script retrieves data from the [Environment Agency Real Time flood-monitoring API](https://environment.data.gov.uk/flood-monitoring/doc/reference). It will first attempt to retrieve the [historic archived data](https://environment.data.gov.uk/flood-monitoring/doc/reference#historic-readings), and if that files it will go to the live data API.

# Usage

To get help:

```bash
$ python . --help
$ python metadata.py --help
```

The configure the pipeline, the files `sites.txt` and `measures.txt` are required. These files contain a list of the URIs for the resources that should be accessed. To generate these files, run the `metadata.py` script as shown below:

```bash
$ python metadata.py --stations > stations.txt
$ python metadata.py --measures > measures.txt
```

To run the pipeline, specify the date and the output file.

```bash
$ python . --date 2020-05-01 --output /path/filename.csv
```

To generate metadata, run the scripts below. The data will be printed to the screen.

```bash
$ python metadata.py --sites
$ python metadata.py --sensors
```

