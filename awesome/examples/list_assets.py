if __name__ == '__main__':
    import logging
    import csv
    import sys
    import argparse

    parser = argparse.ArgumentParser(description='Print UFO metadata as CSV')
    parser.add_argument('--sites', action='store_true')
    parser.add_argument('--families', action='store_true')
    parser.add_argument('--pairs', action='store_true')
    parser.add_argument('--sensors', action='store_true')
    args = parser.parse_args()

    index = 0
    if args.families:
        index = 1
    elif args.pairs:
        index = 2
    elif args.sensors:
        index = 3

    logging.basicConfig(level=logging.INFO)

    writer = None
    rows = get_metadata()[index]
    for row in rows:
        if not writer:
            writer = csv.DictWriter(sys.stdout, fieldnames=row.keys())
            writer.writeheader()
        writer.writerow(row)
