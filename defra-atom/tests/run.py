"""
Run the entire data pipeline automatically
"""

import logging
import subprocess
import datetime

LOGGER = logging.getLogger(__name__)

START_YEAR = 2015

SCRIPTS = (
    'download.py',
    'convert.py',
    'clean.py',
    'todb.py',
)


def run(command: list) -> int:
    """Execute script"""

    result = subprocess.run(command)

    # Raise exceptions
    result.check_returncode()

    return result.returncode


def main():
    logging.basicConfig(level=logging.INFO)

    current_year = datetime.date.today().year

    # Iterate over time
    for year in range(START_YEAR, current_year):
        # Iterate over steps in the pipeline
        for script in SCRIPTS:
            # Build shell command
            command = ['python', script, '--year', str(year)]

            run(command)

    # Run meta-data script
    run(['python', 'metadata.py'])


if __name__ == '__main__':
    main()
