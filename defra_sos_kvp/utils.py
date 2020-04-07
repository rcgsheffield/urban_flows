"""
Utility functions
"""

import datetime
import os
import logging

import settings

LOGGER = logging.getLogger(__name__)


def within_bounding_box(bounding_box, position: tuple) -> bool:
    """Is a geographical position within the specified area?"""

    latitude, longitude = position

    return (bounding_box[1][0] <= latitude <= bounding_box[0][0]) and (
            bounding_box[0][1] <= longitude <= bounding_box[1][1])


def parse_date(s: str) -> datetime.date:
    t = datetime.datetime.strptime(s, settings.DATE_FORMAT)
    return t.date()


def build_path(date: datetime.date, sub_dir: str, ext: str, suffix: str = ''):
    output_dir = os.path.join(settings.DATA_DIR, sub_dir, *date.isoformat().split('-'))
    os.makedirs(output_dir, exist_ok=True)

    if suffix:
        suffix = '_{}'.format(suffix)
    filename = "{date}{suffix}.{ext}".format(date=date.isoformat(), ext=ext, suffix=suffix)

    path = os.path.join(output_dir, filename)

    return path
