# DWP Harvester

This is a data harvester for the Department for Work and Pensions (DWP) [Stat-Explore](https://stat-xplore.dwp.gov.uk/) system. See [Stat-Xplore : Open Data API](https://stat-xplore.dwp.gov.uk/webapi/online-help/Open-Data-API.html) documentation. This API is based on the [SuperSTAR 9.5 Open Data API](https://docs.wingarc.com.au/superstar95/9.5/open-data-api) by [WingArc1st](https://wingarc.com.au/).

# Usage

An authenticated HTTP session is required to communicate with the API.

```python
import http_session

session = http_session.StatSession(api_key='<access_token>')
```

## API objects

The subclasses of `objects.StatObject` are thin wrappers around the API endpoints. Please refer to the [API documentation](https://stat-xplore.dwp.gov.uk/webapi/online-help/Open-Data-API.html).

### Schema

The [/schema endpoint](/schema endpoint) returns information about the Stat-Xplore datasets that are available to you, and their fields and measures.

The root endpoint, `/schema`, returns details of all datasets and folders at the root level of Stat-Xplore.

```python
import objects

# List all data schemas
objects.Schema.list(session)
# Get info about a schema
objects.Schema('str:folder:fuc').get(session)
# Get the schema of a specific table
objects.Schema('str:database:UC_Monthly').get(session)
```

### Table examples

The `/table` [endpoint](https://stat-xplore.dwp.gov.uk/webapi/online-help/Open-Data-API-Table.html) allows you to submit table queries and receive the results. The body of the request contains your query.

```python
# Retrieve the number of people on Universal Credit broken down by month
objects.Table('str:database:UC_Monthly').query(session,
    measures=['str:count:UC_Monthly:V_F_UC_CASELOAD_FULL'],
    dimensions=[['str:field:UC_Monthly:F_UC_DATE:DATE_NAME']],
)
```

