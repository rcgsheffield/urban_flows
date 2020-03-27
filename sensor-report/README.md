# Urban Flows Observatory Sensor Report

## Summary
This repository contains the codebase for the Urban Flows' sensor report. The aim of the report is to provide a RAG status for each sensor measurement based on the CSV data provided to the script.

The RAG status is defined as follows:

*  Green - 100% uptime
*  Amber - Between the Amber Threshold (default 80%) and 100% uptime
*  Red - Between 0% and the Amber Threshold uptime

## Pre-requisites
Python 3.6 and Python 3.7 are supported. The script has been tested using Python 3.7 on Windows and Ubuntu.

CSV data must be provided in UTF-8 format and files must have a .csv extension.

## Installation
To install use the following command:
```bash
$ pip3 install -r requirements.txt
```

We recommend the use of python virtual environments to avoid package dependency issues.

## How to run ##
Place the input CSV file or files in a directory. Then to run the script enter:

```python3 sensor_report.py -i INPUT_LOCATION/INPUT_FILE.csv -o OUTPUTFILE_LOCATION.csv -t AMBER_THRESHOLD```

*  Replace INPUT_LOCATION with the file path to the directory which contains the csv files to be used as input data
* A singular file can also be used for the input file by entering the location to the csv file.
    * for example: ./data/data.csv
* Replace OUTPUTFILE_LOCATION.csv with the location where you want the output data to be saved.
    * for example ./data/output/report.csv
* Replace AMBER_THRESHOLD with the threshold for the amber RAG status
    * for example 0.8
    
## Error handling
Exceptions will be shown in the terminal using the "standard output". Most common errors are handled, including:

*  Missing files or directories
*  Invalid columns in the input files
*  Incorrectly formatted CSV files

Not handled:

*  The script expects UTF-8 CSV files, potentially ambiguous errors may occur if non-UTF-8 files are supplied

## Tests
Basic unit tests have been supplied that check the functionality of the RAG status and the expected outcome of the report. To run the tests, use the following command:

```bash
$ python -m unittest tests.sensor_report_tests
```

## Output ##

The given output file will follow this structure:

```
site_id | sensor_id | measure | uptime | RAG
A0001 |	1 | AQ_CO | 1 | Green
A0001 | 2 | AQ_CO | 0 | Red
A0001 | 3 | AQ_CO | 0.8 | Amber
```

## Support
For support, email us at: operations.helpdesk@jaywing.com or call us: 0333 370 6500.