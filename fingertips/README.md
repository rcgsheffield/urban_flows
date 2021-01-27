# PHE Fingertips harvester

Public Health England (PHE) [https://fingertips.phe.org.uk](https://fingertips.phe.org.uk) data accessed via the Fingertips API.

## Resources

* [API docs](https://fingertips.phe.org.uk/api)
* [Technical Guidance](https://fingertips.phe.org.uk/profile/guidance)

# Usage

## Data retrieval

To view the command-line arguments, run:

```bash
python . --help
```

Life expectancy at birth (part of the Local Authority Health Profile) by district and region:

```bash
python . --verbose --profile_id 26 --indicator_id 90366 --area_type_id 201 --parent_area_type_id 6
```

The same query, filtered for Sheffield only:

```bash
python . --verbose --profile_id 26 --indicator_id 90366 --area_type_id 201 --parent_area_type_id 6 --area_code E08000019
```

## Metadata

This script may be used to navigate the metadata.

```bash
python metadata.py --help
```

Examples:

```
# List health data profiles
python metadata.py --profiles
# List area types
python metadata.py --area_types
# Search for indicators (metrics) by name
python metadata.py -s "life exp"
```

# API

This code contains Python objects which correspond to entities on the remote system. More information is contained in the docstrings of the classes. A HTTP transport layer is required to communicate with that server for most actions.

The base class is `objects.FingertipObject` which implements a `list(session)` class method to get all the objects of that class, where `session` is a HTTP session (an instance of `http_session.FingertipsSession`). This class also contains various useful functions to assist working with the API.

Each entity is implemented, such as National Public Health Profiles as shown below:

```python
import objects

help(objects.Profile)
objects.Profile(100)
```

To retrieve a list of objects from the remote server:

```python
import http_session

session = http_session.FingertipsSession()
objects.Profile.list(session)
```

# Glossary

The objects in the API are also documented in the docstrings of the Python classes.

* Profile: Collections of data sets. It contains groups of data (the tabs on the GUI display.) For example, the profile with identifier 100 is "Wider Impacts of COVID-19 on Health."
* Geospatial concepts
  * Area Type: geographical systems e.g. categories governmental regions, etc. For example, area type 201 is "Lower tier local authorities (4/19 - 3/20)"
    * Area: A specific geospatial 2D place e.g. "Sheffield"

