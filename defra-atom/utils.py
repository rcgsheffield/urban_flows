"""
Random utility functions
"""

import os.path
import pathlib


def build_input_dir(root_input_dir: str, year: int) -> str:
    return os.path.join(root_input_dir, str(year))


def build_output_dir(root_output_dir, year, input_path) -> str:
    """Prepare output directory"""

    output_dir = os.path.join(root_output_dir, str(year), *pathlib.Path(input_path).parts[-2:-1])

    os.makedirs(output_dir, exist_ok=True)

    return output_dir


def build_output_path(output_dir, input_path):
    filename = os.path.basename(input_path)
    return os.path.join(output_dir, filename)
