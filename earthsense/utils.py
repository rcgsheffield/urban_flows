import pathlib
import configparser


def get_config(path: pathlib.Path) -> configparser.ConfigParser:
    path = pathlib.Path(path)

    config = configparser.ConfigParser()
    with path.open() as file:
        config.read_file(file)

    return config


def get_credentials(path) -> dict:
    config = get_config(path)
    return dict(config['credentials'])
