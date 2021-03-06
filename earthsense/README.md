# EarthSense data harvester

This is a Python script to harvest data from EarthSense Zepyhr. It works by iterating over all the devices available on the EarthSense portal using their API.

* [EarthSense Zephyr devices](https://www.earthsense.co.uk/zephyr) (the API docs are linked from this page)
* [MyAir portal](https://portal.earthsense.co.uk/)

# Documentation

Use these commands to view the usage instructions.

```bash
$ python . --help
$ python metadata.py --help
```

# Usage

Specify a configuration file using the `--config` command line argument. By default, the scripts will attempt to load a configuration file named `earthsense.cfg` in the user's home directory. A sample configuration file is provided in this repository named `earthsense.sample.cfg`.

To download data:

```bash
$ python . --date 2020-05-01 --output data/2020-05-01.csv
```

Get get metadata:

```bash
$ python metadata.py --sensors > sensors.txt
$ python metadata.py --sites > sites.txt
```

