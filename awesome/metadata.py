import argparse
import json
from typing import Tuple

import assets


def get_args() -> Tuple[argparse.ArgumentParser, argparse.Namespace]:
    parser = argparse.ArgumentParser(description="Show Urban Flows Observatory metadata objects")

    parser.add_argument('-s', '--sites', action='store_true')
    parser.add_argument('-f', '--families', action='store_true')
    parser.add_argument('-p', '--pairs', action='store_true')
    parser.add_argument('-e', '--sensors', action='store_true')

    return parser, parser.parse_args()


def jprint(*args, **kwargs):
    print(*(json.dumps(obj, indent=2) for obj in args), **kwargs)


if __name__ == '__main__':
    parser, args = get_args()

    sites, families, pairs, sensors = assets.get_metadata()

    result = None

    if args.sites:
        result = sites
    elif args.families:
        result = families
    elif args.pairs:
        result = pairs
    elif args.sensors:
        result = sensors
    else:
        parser.print_help()
        exit()

    jprint(result)
