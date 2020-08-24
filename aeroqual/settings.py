import pathlib

DEFAULT_CONFIG_FILE = pathlib.Path.home().joinpath('configs', 'aeroqual.cfg')

LOGGING = dict(
    # https://docs.python.org/3.8/library/logging.html#logrecord-attributes
    format='%(asctime)s %(filename)s:%(lineno)s %(levelname)s %(message)s',
)

DEFAULT_AVERAGING_PERIOD = 1
