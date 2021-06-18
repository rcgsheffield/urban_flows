import logging
import datetime

import assets
import aqi.operations
import ufdex

LOGGER = logging.getLogger(__name__)

DATE = datetime.datetime(2021, 6, 1)


def main():
    logging.basicConfig(level=logging.DEBUG)

    # Get UFO sites
    families = assets.get_metadata()['families']

    aqi_reading_count = 0

    for family_id, family in families.items():
        query = ufdex.UrbanFlowsQuery(
            time_period=[DATE, DATE + datetime.timedelta(days=1)],
            families={family_id},
        )
        readings = list(query())
        LOGGER.info('Got %s readings', len(readings))

        data = aqi.operations.transform_ufo_data(readings)
        print(data.head())

        try:
            for site_id, df in data.groupby('site.id', group_keys=False):
                LOGGER.info(site_id)
                # Remove index level
                df = df.loc[site_id]

                print(df.head())

                air_qual = aqi.operations.calculate_air_quality(df)
                print(air_qual.head())

                aqi_count = len(air_qual.index)
                LOGGER.info("Family '%s': %s AQI readings", family_id,
                            aqi_count)

                aqi_reading_count += aqi_count
        except KeyError:
            if not data.empty:
                raise

    print(DATE.date().isoformat(), 'total AQI readings:', aqi_reading_count)


if __name__ == '__main__':
    main()
