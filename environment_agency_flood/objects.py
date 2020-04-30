import logging
import csv

from collections import OrderedDict, Mapping

import utils
import settings

LOGGER = logging.getLogger(__name__)


class Object:
    edge = ''

    def __init__(self, object_id: str):
        self.object_id = object_id

    @property
    def endpoint(self) -> str:
        return "{edge}/{identifier}".format(edge=self.edge, identifier=self.identifier)

    @classmethod
    def list(cls, session, **params) -> list:
        return session.call(cls.edge, params=params)['items']

    @property
    def identifier(self) -> str:
        """Unique identifier or reference (last item extracted from URL)"""
        return self.object_id.rpartition('/')[2]

    def get(self, session) -> dict:
        return session.call(self.endpoint)['items']

    def load(self, session):
        data = self.get(session)

        for attr, value in data.items():
            setattr(self, attr, value)


class Station(Object):
    """
    Station

    https://environment.data.gov.uk/flood-monitoring/doc/reference#stations
    """
    edge = 'stations'

    def measures(self, session, **params) -> list:
        endpoint = "{}/measures".format(self.endpoint)

        return session.call(endpoint, params=params)['items']

    def readings(self, session, **params) -> list:
        endpoint = "{endpoint}/readings.csv".format(endpoint=self.endpoint)

        stream = session.call_iter(endpoint, params=params)

        headers = next(csv.reader(stream))
        for row in csv.DictReader(stream, fieldnames=headers):
            # Parse
            try:
                yield OrderedDict(
                    station=self.object_id,
                    measure=row['measure'],
                    timestamp=utils.parse_timestamp(row['dateTime']),
                    value=utils.parse_value(row['value'])
                )
            except ValueError:
                LOGGER.error(row)
                raise

    def load(self, *args, **kwargs):
        super().load(*args, **kwargs)

        # If a single measure is returned, convert it into a list to maintain consistent API
        if isinstance(self.measures, Mapping):
            self.measures = [self.measures]

        # Build measure mapping
        self.measures = {measure['@id']: measure for measure in self.measures}


class Measure(Object):
    """"
    Measure

    https://environment.data.gov.uk/flood-monitoring/doc/reference#measures
    """
    edge = 'measures'


class Reading(Object):
    """
    Reading

    https://environment.data.gov.uk/flood-monitoring/doc/reference#readings
    """
    edge = 'data/readings'

    @classmethod
    def get_archive(cls, session, date):
        endpoint = "../archive/readings-full-{date}.csv".format(date=date)

        lines = session.call_iter(endpoint)
        headers = next(csv.reader(lines))

        for row in csv.DictReader(lines, fieldnames=headers):
            yield OrderedDict(
                timestamp=utils.parse_timestamp(row['dateTime']),
                station=row['station'],
                station_reference=row['stationReference'],
                measure=row['measure'],
                unit_name=row['unitName'],
                value=utils.parse_value(row['value']),
                datumType=row['datumType'],
                label=row['label'],
                parameter=row['parameter'],
                qualifier=row['qualifier'],
                period=row['period'],
                value_type=row['valueType'],
                observed_property=settings.PARAMETER_MAP[row['parameter']],
            )
