import configparser


def get_credentials(path: str):
    config = configparser.ConfigParser()
    config.read(path)

    return config['credentials']
