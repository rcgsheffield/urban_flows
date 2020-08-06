import pathlib

DEFAULT_TOKEN_PATH = pathlib.Path.home().joinpath('awesome_token.txt')

LOGGING = dict(
    format="%(levelname)s %(asctime)-15s %(filename)s:%(lineno)d %(message)s",
)
