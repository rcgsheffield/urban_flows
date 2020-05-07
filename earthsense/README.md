# EarthSense data harvester

* [EarthSense Zephyr devices](https://www.earthsense.co.uk/zephyr) (the API docs are linked from this page)

# Documentation

```bash
$ python . --help
$ python metadata.py --help
```

# Usage

To download data:

```bash
$ python . --date 2020-05-01 --output data/2020-05-01.csvs
```

Get get metadata:

```bash
$ python metadata.py --sensors > sensors.txt
$ python metadata.py --sites > sites.txt
```

