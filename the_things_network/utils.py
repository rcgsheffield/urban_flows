import configparser
import getpass

DEFAULT_CONFIG_PATH = 'the_things_network.cfg'


def get_config(path: str = DEFAULT_CONFIG_PATH) -> dict:
    config = configparser.ConfigParser()
    config.read(path)

    return config._sections


def get_access_token() -> str:
    # TODO *remove this!!!*
    return 'ttn-account-v2.1UV9XTVFgokW7OtCdkiseJoKIfJ2WPiJDQ2V6mLkiig'
    return getpass.getpass('Enter access token: ')
