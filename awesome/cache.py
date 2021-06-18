import pathlib
import shelve
from typing import Optional

import settings


class Cache:
    """
    Disk caching utility

    Thin wrapper about shelve standard library
    """

    def __init__(self, name: str):
        self.name = name
        self._shelf = None  # type: Optional[shelve.Shelf]

    @property
    def path(self) -> pathlib.Path:
        return settings.BOOKMARK_PATH_PREFIX.joinpath(self.name)

    @property
    def shelf(self) -> shelve.Shelf:
        if self._shelf is None:
            # Ensure directory exists
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._shelf = shelve.open(str(self.path))
        return self._shelf

    def __enter__(self, *args, **kwargs):
        yield self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __getitem__(self, item):
        return self.shelf[item]

    def get(self, item, default=None):
        try:
            return self[item]
        except KeyError:
            return default

    def __setitem__(self, key, value):
        self.shelf[key] = value
        self.shelf.sync()

    def __del__(self):
        self.close()

    def close(self):
        self.shelf.close()
