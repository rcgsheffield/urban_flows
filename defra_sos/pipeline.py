"""
EDefra’s UK-AIR Sensor Observation Service (SOS) API
https://uk-air.defra.gov.uk/data/about_sos
"""

import logging
import utils

import download
import csv
import metadata

DESCRIPTION = """
Defra’s UK-AIR Sensor Observation Service (SOS) API
https://uk-air.defra.gov.uk/data/about_sos

Automatically download Defra’s UK-AIR Sensor Observation Service (SOS) data 
for a particular date and particular catchment areas 
and save the source data files to disk.

"""

LOGGER = logging.getLogger(__name__)


def main():
    args = utils.get_args(DESCRIPTION)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    fh = download.DEFRASOSHarvestor(args.date, args.distance, args.update_meta, args.output_meta, LOGGER)

    stations = fh.get_stations()

    utils.build_dir(args.output_meta)
    md = metadata.DEFRASOSHarvestorMeta(args.output_meta)

    if args.update_meta:
        for station in stations:
            md.generate_metadata(station)
            md.generate_metadata_csv(stations)

            # TODO remove
            break

    # CSV output to file
    with open(args.output_data, 'w', newline='') as file:
        writer = csv.DictWriter(file, fh.columns)
        writer.writeheader()

        # Generate data
        for row in fh.get_data(stations):
            row = fh.transform(row)
            writer.writerow(row)

            # TODO remove
            break


if __name__ == '__main__':
    main()
