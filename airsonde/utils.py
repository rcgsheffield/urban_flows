import configparser

CONFIG_PATH = 'settings.cfg'


def get_settings() -> configparser.ConfigParser:
    config = configparser.ConfigParser()

    config.read(CONFIG_PATH)

    return config
