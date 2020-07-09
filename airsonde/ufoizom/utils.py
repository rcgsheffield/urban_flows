import logging
import configparser

import ufoizom.http_session


def load_config(path) -> configparser.ConfigParser:
    config = configparser.ConfigParser()

    with open(path) as file:
        config.read_file(file)

    return config


def get_session(config_file):
    config = load_config(config_file)
    return ufoizom.http_session.OizumSession(client_id=config['credentials']['client_id'],
                                             client_secret=config['credentials']['client_secret'])


def configure_logging(verbose: bool = False):
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)
