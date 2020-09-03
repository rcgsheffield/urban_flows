import argparse
import datetime
import logging

from typing import Type

import objects
import settings
import utils

from http_session import PortalSession

LOGGER = logging.getLogger(__name__)


class DeleteArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_argument('-v', '--verbose', action='store_true')
        self.add_argument('-d', '--debug', action='store_true')


def delete_objects(session: PortalSession, cls: Type[objects.AwesomeObject]):
    LOGGER.info(cls.__class__.__name__)
    for data in cls.list_iter(session):
        obj = cls(data['id'])
        obj.delete(session)


def delete(session: PortalSession):
    # Bulk delete readings
    LOGGER.info('Bulk deleting readings...')
    for reading_type in objects.ReadingType.list_iter(session):
        LOGGER.info(reading_type)
        objects.Reading.delete_bulk(
            session=session,
            start=datetime.datetime.min.replace(tzinfo=datetime.timezone.utc),
            end=datetime.datetime.utcnow(),
            reading_type_id=reading_type['id']
        )

    # Delete metadata objects
    LOGGER.info('Deleting metadata objects...')
    delete_objects(session, objects.Location)
    delete_objects(session, objects.Sensor)
    delete_objects(session, objects.ReadingCategory)
    delete_objects(session, objects.ReadingType)
    delete_objects(session, objects.SensorType)
    delete_objects(session, objects.SensorCategory)


def main():
    parser = DeleteArgumentParser()
    args = parser.parse_args()

    utils.configure_logging(verbose=args.verbose, debug=args.debug)

    with PortalSession(token_path=settings.DEFAULT_TOKEN_PATH) as session:
        delete(session)


if __name__ == '__main__':
    main()
