import utils
import logging

import http_session
import maps
import settings

from objects import Instrument

LOGGER = logging.getLogger(__name__)


class AeroqualMetadataArgumentParser(utils.AeroqualArgumentParser):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_argument('-s', '--csv', action='store_true', help='Show CSV headers')
        self.add_argument('-n', '--sensors', action='store_true', help='Get sensor metadata')


def main():
    parser = AeroqualMetadataArgumentParser()
    args = parser.parse_args()
    utils.configure_logging(verbose=args.verbose, debug=args.debug, error=args.error)

    session = http_session.AeroqualSession(config_file=args.config)

    if args.csv:
        # TODO static list of columns
        print(settings.UrbanDialect.delimiter.join(set()))
    elif args.sensors:
        for serial_number in Instrument.list(session):
            instrument = Instrument(serial_number)
            instr_data = instrument.get(session)

            uf_sensor = maps.instrument_to_sensor(instrument=instr_data)
            print(uf_sensor)

    elif args.sites:
        pass

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
