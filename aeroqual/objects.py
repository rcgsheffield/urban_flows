import datetime
import logging

from typing import Iterable, Dict

from http_session import AeroqualSession

Rows = Iterable[Dict]

LOGGER = logging.getLogger(__name__)


class Object:
    EDGE = None

    def __init__(self, identifier: str):
        self.identifier = identifier

    def __repr__(self):
        return "{}('{}')".format(self.__class__.__name__, self.identifier)

    @classmethod
    def list(cls, session: AeroqualSession, **kwargs):
        return session.call(endpoint=cls.EDGE, **kwargs)

    def get(self, session: AeroqualSession, **kwargs):
        return session.call(self.endpoint, **kwargs)

    @property
    def endpoint(self) -> str:
        return "{}/{}".format(self.EDGE, self.identifier)


class Instrument(Object):
    EDGE = 'instrument'


class Data(Object):
    EDGE = 'data'

    def query(self, session, start: datetime.datetime, end: datetime.datetime, averagingperiod: int,
              includejournal: bool = False) -> Rows:
        """
        Fetch instrument data.

        serial = serial number of instrument
        start time = date/time of beginning of required data period (inclusive) – in instrument local time zone,
            format yyyy-mm-ddThh:mm:ss
        end time = date/time of end of required data period (not inclusive)
        averaging period = period in minutes to average data – minimum 1 minute
        include journal = (optional) whether to include journal entries – true or false
        """
        # Example query:
        # from=2016-01-01T00:00:00&to=2016-01-02T00:00:00&averagingperiod=60&includejournal=false
        params = {
            'from': start.isoformat(),
            'to': end.isoformat(),
            'averagingperiod': averagingperiod,
            'includejournal': includejournal,
        }
        body = self.get(session, params=params)

        data = body.pop('data')

        # Log metadata
        for key, value in body.items():
            LOGGER.debug("%s: %s", key, value)

        yield from data
