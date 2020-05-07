import configparser


def get_credentials(path: str):
    config = configparser.ConfigParser()
    with open(path) as file:
        config.read_file(file)

    return config['credentials']
