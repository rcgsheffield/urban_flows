"""
Department for Environment, Food and Rural Affairs - Atom Download Services
https://uk-air.defra.gov.uk/data/atom-dls/
"""

import os
import logging
import argparse

import http_session
import parsers.inspire
import settings

DESCRIPTION = """
Department for Environment, Food and Rural Affairs - Atom Download Services
https://uk-air.defra.gov.uk/data/atom-dls/

Automatically download specified DEFRA data for a particular year and save the source data files to disk.

The XML resources found by following a trail of links as follows:

  1. Annual ATOM list of resources
  2. A specific site e.g. "GB Fixed Observations for Barnsley Gawber (BAR3) in 2020"
  3. Observations for that site for a particular year
"""

LOGGER = logging.getLogger(__name__)

# Root Atom feeds
URL_TEMPLATES = [
    'https://uk-air.defra.gov.uk/data/atom-dls/auto/{year}/atom.en.xml',
    'https://uk-air.defra.gov.uk/data/atom-dls/non-auto/{year}/atom.en.xml',
]


def configure_arguments():
    """Command-line arguments"""

    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument('-o', '--output', default=settings.DEFAULT_RAW_DIR, type=str, help="Output file directory")
    parser.add_argument('-y', '--year', required=True, type=int, help="Year time filter")
    parser.add_argument('-v', '--verbose', action='store_true', help="Debug logging mode")

    # Geographical filter parameters
    parser.add_argument('-l', '--location', type=tuple, help='Central location of interest',
                        default=settings.DEFAULT_LOCATION)
    parser.add_argument('-d', '--distance', type=float, help='Maximum distance from current location',
                        default=settings.DEFAULT_DISTANCE)
    parser.add_argument('-u', '--unit', type=str, help='Units of distance', default=settings.DEFAULT_UNIT)

    return parser.parse_args()


def configure_logging(args):
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(name)s:%(lineno)d %(levelname)s: %(message)s"
    )


def build_path(args, url) -> str:
    # e.g. "non-auto/GB_FixedObservations_2015_SHE.xml"
    path_parts = url.split('/')[-2:]
    path = os.path.join(args.output, str(args.year), *path_parts)

    # Ensure subdirectory exists
    os.makedirs(os.path.dirname(path), exist_ok=True)

    return path


def serialise(path, data):
    with open(path, 'xb') as file:
        file.write(data)

        LOGGER.info("Wrote '%s'", file.name)


def main():
    args = configure_arguments()
    configure_logging(args)

    session = http_session.DEFRASession()

    # Iterate over data set indexes
    for template in URL_TEMPLATES:
        url = template.format(year=args.year)

        LOGGER.info(url)

        # Data set index ATOM feed
        index = parsers.inspire.InspireAtomParser.get(session, url)

        # Get data sets within specified geographical area
        for data_set in index.filter_data_sets_by_distance(args.location, args.distance, args.unit):

            # Get data ATOM feeds
            for link in data_set.alternate_links:
                url = link['href']

                LOGGER.info(url)

                # Parse ATOM feed
                feed = parsers.atom.AtomParser.get(session, url)

                # Follow links to data files
                for entry in feed.entries:
                    for data_link in entry.alternate_links:
                        data_url = data_link['href']

                        LOGGER.info(data_url)

                        # Serialise data XML
                        data = session.get(data_url).content
                        path = build_path(args, data_url)
                        serialise(path, data)


if __name__ == '__main__':
    main()
