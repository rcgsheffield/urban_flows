# AirSonde data pipeline

This is a data pipeline to ingest sensor data from a collection of Environmental Monitoring Solutions (EMS)
[AirSonde](https://www.em-solutions.co.uk/airsonde/) devices via the Oizom API.

## Useful links

* Admin portal: [Oizom Terminal](https://terminal.oizom.com) 
* Oizom [API documentation](https://production.oizom.com/documentation/)

## Installation

Configure the pipeline using a file like `oizom.sample.cfg`. By default, the code will attempt to locate this in the user's home directory. To specify the location, use the `--config` command-line argument, which defaults to `~/oizom.cfg`.

## Usage

```
$ python -m ufoizom --help
$ python -m ufoizom.metadata --help
```

