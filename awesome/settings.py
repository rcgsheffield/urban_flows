import pathlib

# Authentication token
DEFAULT_TOKEN_PATH = pathlib.Path.home().joinpath('configs', 'awesome_token.txt')

# Log config
LOGGING = dict(
    format="%(levelname)s %(asctime)s %(filename)s:%(lineno)d %(message)s",
)

# The maximum number of readings to upload at once to /api/reading/bulk. The limit is 100.
BULK_READINGS_CHUNK_SIZE = 200

DEFAULT_READING_TYPE_GROUPS_FILE = 'reading_type_groups.json'
