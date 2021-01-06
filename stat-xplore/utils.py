import json
import pathlib

import settings


def load_api_key(path: pathlib.Path = None) -> str:
    """
    Read API access token from diskn
    """
    path = path or settings.TOKEN_PATH
    with path.open() as file:
        return file.read().strip()


def jprint(obj):
    print(json.dumps(obj, indent=2))
