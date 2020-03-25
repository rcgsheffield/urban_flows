import configparser
import getpass

DEFAULT_CONFIG_PATH = 'the_things_network.cfg'


def get_config(path: str = DEFAULT_CONFIG_PATH) -> dict:
    config = configparser.ConfigParser()
    config.read(path)

    return config._sections


def get_access_token() -> str:
    return getpass.getpass('Enter access token: ')
