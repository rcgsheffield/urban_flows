import logging
import utils
import csv

import download
import metadata

DESCRIPTION = """
DEFRA UK-AIR Sensor Observation Service (SOS) API
https://uk-air.defra.gov.uk/data/about_sos

Download DEFRA UK-AIR Sensor Observation Service (SOS) data.
"""

LOGGER = logging.getLogger(__name__)


def main():
    args = utils.get_args(DESCRIPTION)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    harvester = download.DEFRASOSHarvestor(args.date, args.distance, args.update_meta, args.output_meta)

    meta = metadata.DEFRASOSHarvestorMeta(args.output_meta)

    utils.build_dir(args.output_meta)

    # CSV output to file
    with open(args.output_data, 'w', newline='') as file:
        writer = csv.DictWriter(file, harvester.columns)
        writer.writeheader()

        # Iterate over stations
        for station in harvester.get_stations():

            # Save station metadata
            site = meta.build_site(station)
            site.save()

            # Generate data
            for row in harvester.get_data(station):
                row = harvester.transform(row)
                writer.writerow(row)

        LOGGER.info("Wrote '%s'", file.name)


if __name__ == '__main__':
    main()
