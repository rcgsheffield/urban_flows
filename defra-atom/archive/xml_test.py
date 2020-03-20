import os
import logging
import argparse
import csv
import datetime
import xml.etree.ElementTree
import json
import urllib.parse

import http_session
import spatial_object

DESCRIPTION = """
Department for Environment, Food and Rural Affairs - Atom Download Services
https://uk-air.defra.gov.uk/data/atom-dls/

Automatically download specified DEFRA data for a particular year and save the output as CSV to a file

The selected sensor sites are configured within the script in the SELECTED_IDS constant.

The XML resources found by following a trail of links as follows:

  1. Annual ATOM list of resources
  2. A specific site e.g. "GB Fixed Observations for Barnsley Gawber (BAR3) in 2020"
  3. Observations for that site for a particular year
"""

LOGGER = logging.getLogger(__name__)

URL_TEMPLATE = "https://uk-air.defra.gov.uk/data/atom-dls/auto/{year}/atom.en.xml"

# Data sets to retrieve
SELECTED_IDS = {
    'GB_FixedObservations_{year}_SHBR',
    'GB_FixedObservations_{year}_SHDG',
    'GB_FixedObservations_{year}_SHE',
}

VOCAB = None
VOCAB_PATH = 'vocab_aq_pollutant.json'


def parse(data):
    root = xml.etree.ElementTree.fromstring(data)

    for key, value in root.attrib.items():
        LOGGER.debug("%s: %s", key, value)

    return root


def get_entries(root) -> iter:
    """Iterate over the overall listing for one year and get all the sites"""
    for item in root:
        for child in item:
            if child.tag == '{http://inspire.ec.europa.eu/schemas/inspire_dls/1.0}spatial_dataset_identifier_code':

                # Is this a selected site?
                if child.text in SELECTED_IDS:
                    site_id = child.text

                    yield site_id, item


def get_sites(url: str, session) -> iter:
    """Retrieve meta-data about data streams"""
    for site_id, entry in get_entries(session.get(url)):
        for prop in entry:
            if prop.tag == '{http://www.w3.org/2005/Atom}link':
                if prop.attrib['rel'] == 'alternate':
                    site_url = prop.attrib['href']

                    yield site_id, site_url


def get_data_urls(root) -> iter:
    """Retrieve the URL for the actual data stream"""
    for item in root:
        if item.tag == '{http://www.w3.org/2005/Atom}entry':
            for prop in item:
                # Get hyperlink
                if prop.tag == '{http://www.w3.org/2005/Atom}link':
                    if prop.attrib['rel'] == 'alternate':
                        data_url = prop.attrib['href']

                        yield data_url


def get_data(url: str) -> iter:
    """Retrieve data from the XML file"""

    block_sep = '@@'
    sep = ','

    for feature_member in parse(get(url)):
        for child in feature_member:
            # Reset for each new item
            headers = list()
            n_rows = 0
            element_count = 0
            observed_property = None
            feature_of_interest = None
            unit_of_measurement = None

            if child.tag == '{http://www.opengis.net/om/2.0}OM_Observation':

                for obs_prop in child:

                    # Get observed property
                    if obs_prop.tag == '{http://www.opengis.net/om/2.0}observedProperty':
                        observed_property = obs_prop.attrib['{http://www.w3.org/1999/xlink}href']

                        LOGGER.info("Observed property: %s", observed_property)

                    # Feature of interest
                    elif obs_prop.tag == '{http://www.opengis.net/om/2.0}featureOfInterest':
                        feature_of_interest = obs_prop.attrib['{http://www.w3.org/1999/xlink}href']

                        LOGGER.info("Feature of interest: %s", feature_of_interest)

                    # Get results
                    elif obs_prop.tag == '{http://www.opengis.net/om/2.0}result':
                        for data_array in obs_prop:
                            for element in data_array:

                                if element.tag == '{http://www.opengis.net/swe/2.0}elementCount':
                                    element_count = int(element[0][0].text)

                                elif element.tag == '{http://www.opengis.net/swe/2.0}elementType':

                                    # Iterate over data fields
                                    for field in element[0]:
                                        name = field.attrib['name']
                                        headers.append(name)

                                        if name == 'Value':
                                            # field -> Quantity -> uom
                                            unit_of_measurement = field[0][0].attrib[
                                                '{http://www.w3.org/1999/xlink}href']

                                            LOGGER.info("Unit of measurement: %s", unit_of_measurement)

                                # Get CSV format
                                elif element.tag == '{http://www.opengis.net/swe/2.0}encoding':
                                    csv_format = element[0].attrib
                                    block_sep = csv_format['blockSeparator']
                                    sep = csv_format['tokenSeparator']

                                # Build data rows
                                elif element.tag == '{http://www.opengis.net/swe/2.0}values':
                                    # Parse CSV data
                                    lines = element.text.strip().split(block_sep)

                                    # Iterate over lines of data
                                    for line in lines:
                                        values = line.split(sep)
                                        row = dict(zip(headers, values))

                                        # Append meta-data
                                        row['observed_property'] = observed_property
                                        row['feature_of_interest'] = feature_of_interest
                                        row['unit_of_measurement'] = unit_of_measurement

                                        yield row

                                        n_rows += 1

                                    # Validate row count
                                    if n_rows != element_count:
                                        raise ValueError(f"Unexpected number of rows, {n_rows} != {element_count}")

                                    LOGGER.info("Retrieved %s rows of data", n_rows)


def parse_timestamp(timestamp: str) -> datetime.datetime:
    try:
        t = datetime.datetime.fromisoformat(timestamp[:-1])

    # The hour is "24" (instead of "00")
    except ValueError:
        date = datetime.date.fromisoformat(timestamp[:10])
        time = datetime.time.min
        t = datetime.datetime.combine(date, time)

    return t.replace(tzinfo=datetime.timezone.utc)


def transform(row: dict, append: dict) -> dict:
    """Clean a row of data"""

    # Parse timestamps
    for key in {'StartTime', 'EndTime'}:
        row[key] = parse_timestamp(row[key])

    # Insert values
    for key, value in append.items():
        row[key] = value

    return row


def configure_arguments():
    """Command-line arguments"""

    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument('-o', '--output', required=True, type=str, help="Output CSV file")
    parser.add_argument('-y', '--year', required=True, type=int, help="Year time filter")
    parser.add_argument('-v', '--verbose', action='store_true', help="Debug logging mode")

    return parser.parse_args()


def set_selected_ids(year: int):
    """Insert the selected year into the site identifier"""
    return {s.format(year=year) for s in SELECTED_IDS}


def clean(rows, **kwargs) -> iter:
    yield from (transform(row, **kwargs) for row in rows)


def write_csv(rows, file):
    writer = None

    # Stream data
    for row in rows:

        # Initialise CSV writer
        if not writer:
            writer = csv.DictWriter(file, row.keys())
            writer.writeheader()

        writer.writerow(row)


def load_vocabulary(path: str) -> iter:
    """Map vocabulary URL to the metric name"""

    with open(path) as file:
        data = json.load(file)

        base = data['@context']['@base']

        # Iterate over metrics
        for item in data['concepts']:
            identifier = item['@id']

            # Build URL
            url = urllib.parse.urljoin(base, identifier)

            friendly_name = item['prefLabel'][0]['@value']

            yield url, friendly_name


def main():
    global VOCAB, SELECTED_IDS, SESSION

    args = configure_arguments()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(name)s:%(lineno)d %(levelname)s: %(message)s"
    )

    # Select time filter
    SELECTED_IDS = set_selected_ids(year=args.year)
    url = URL_TEMPLATE.format(year=args.year)

    LOGGER.info(url)

    VOCAB = dict(load_vocabulary(VOCAB_PATH))

    os.makedirs(spatial_object.SpatialObject.DIR, exist_ok=True)

    session = http_session.DEFRASession()

    with open(args.output, 'x', newline='') as file:

        # Get list of data entries for this year
        # Iterate over sites
        for site_id, site_url in get_sites(url, session):

            LOGGER.info("Site URL: %s", site_url)

            # Retrieve data locations for those sites
            for data_url in get_data_urls(site_url, session):
                LOGGER.info("Data URL: %s", data_url)

                # Clean the data
                rows = clean(get_data(data_url), append=dict(site_id=site_id))

                # Output results
                write_csv(rows, file=file)


if __name__ == '__main__':
    main()
