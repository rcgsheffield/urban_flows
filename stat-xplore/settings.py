import pathlib

CONFIGS_DIR = pathlib.Path.home().joinpath('configs')
TOKEN_PATH = CONFIGS_DIR.joinpath('stat_explore.txt')

# Arguments for logging.basicConfig
LOGGING = dict(
    # Log string format
    # https://docs.python.org/3.8/library/logging.html#logrecord-attributes
    format='%(asctime)s %(filename)s:%(lineno)s %(levelname)s %(message)s',
)
