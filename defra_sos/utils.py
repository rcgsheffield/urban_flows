"""
Random utility functions
"""

import os
import argparse
from datetime import datetime
import json


def build_dir(path):
    """Build directories for a given path"""
    os.makedirs(path, exist_ok=True)


def build_output_dir_for_meta(root_output_dir, folder_name):
    """Prepare output directory for meta"""

    output_dir = "{}/{}".format(root_output_dir, folder_name)
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def build_output_dir_for_data(root_output_dir, date: str) -> str:
    """Prepare output directory for each date"""

    output_dir = os.path.join(root_output_dir, *date.split('-'))
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def get_args(description, args=None) -> argparse.Namespace:
    """Command-line arguments"""

    parser = argparse.ArgumentParser(description=description)

    parser.add_argument('-d', '--date', required=True, type=lambda s: datetime.strptime(s, '%Y-%m-%d'),
                        help="ISO UTC date")
    parser.add_argument('-od', '--output_data', required=True, type=str, help="Output CSV file path")
    parser.add_argument('-k', '--distance', type=int, help="Radius distance (km)", default=30)
    parser.add_argument('-um', '--update_meta', action='store_true', help="True if update the metadata")
    parser.add_argument('-om', '--output_meta', type=str, help="Output folder path for metadata files",
                        default="meta")
    parser.add_argument('-v', '--verbose', action='store_true', help='Show debug logs')
    parser.add_argument('-ad', '--assets-dir', type=str, help="Assets directory", default="assets")

    args = parser.parse_args(args=args)

    return args


def get_value1(obj: json, path: str):
    p = path.split('_')
    result = obj
    for i in range(len(p)):
        result = result.get(p[i], '')
    return result if type(result) != tuple else result[0]

