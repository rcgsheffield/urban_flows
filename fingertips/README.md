# PHE Fingertips harvester

Public Health England (PHE) data accessed via the [Fingertips](https://fingertips.phe.org.uk) API.

## Resources

* The [API docs](https://fingertips.phe.org.uk/api) show the arguments for each endpoint with very brief notes.
* The [Technical Guidance](https://fingertips.phe.org.uk/profile/guidance) is for users of the graphical user interface on the PHE website.
* A glossary of terms is included below.

# Usage

## Data retrieval

To view the command-line arguments, run:

```bash
python . --help
```

To run a query, the parameters must be specified using command-line arguments. By default the output data will be printed to screen. Use the `--output` flag to specify the path of a file to write to.

Life expectancy at birth (part of the Local Authority Health Profile) by district and region:

```bash
python . --verbose --indicator_id 90366 --area_type_id 201 --parent_area_type_id 6 --output test.csv
```

The same query, filtered for Sheffield only:

```bash
python . --verbose --indicator_id 90366 --area_type_id 201 --parent_area_type_id 6 --area_code E08000019 --output test.csv
```

All data in the Local Authority Health Profiles, broken down by district and region:

```bash
python . --verbose --profile_id 26 --area_type_id 201 --parent_area_type_id 6 --output test.csv
```

## CSV headers

To print the CSV headers, run the query with the `--write_header` flag:

```bash
python . --verbose --indicator_id 90366 --area_type_id 201 --parent_area_type_id 6 --write_header
```



## Metadata

This script may be used to navigate the metadata, which are displayed as JSON objects.

```bash
python metadata.py --help
```

List health data profiles

```bash
python metadata.py --profiles
```

List area types

```bash
python metadata.py --area_types
```

Search for indicators (metrics) by name

```bash
python metadata.py -s "life exp"
```

Show the details of a single indicator

```bash
python metadata.py -n 90366
```

# API

This code contains Python objects which correspond to entities on the remote system. More information is contained in the docstrings of the classes. A HTTP transport layer is required to communicate with that server for most actions.

The base class is `objects.FingertipObject` which implements a `list(session)` class method to get all the objects of that class, where `session` is a HTTP session (an instance of `http_session.FingertipsSession`). This class also contains various useful functions to assist working with the API.

Each entity is implemented, such as National Public Health Profiles as shown below:

```python
import objects

help(objects)
help(objects.Profile)
objects.Profile(100)
```

To retrieve a list of objects from the remote server:

```python
import http_session
import objects

session = http_session.FingertipsSession()
objects.Profile.list(session)
```

# Glossary

The objects in the API are also documented in the docstrings of the Python classes.

* Profile: Collections of data sets. It contains groups of data (the tabs on the GUI display.) For example, the profile with identifier 100 is "Wider Impacts of COVID-19 on Health."
  * Indicator: A quantitative metric or measurement of a phenomenon
* Geospatial concepts
  * Area Type: geographical systems e.g. categories governmental regions, etc. For example, area type 201 is "Lower tier local authorities (4/19 - 3/20)"
    * Area: A specific geospatial 2D place e.g. "Sheffield"

