"""
Utility functions for working with file paths and S3 paths.
"""

import os
from pathlib import Path


def s3_to_local_path(s3_path):
    """
    Converts an S3 path to a local path.

    Args:
        s3_path (str): The S3 path to convert, should start with 's3://'.

    Returns:
        Path: The corresponding local path object.

    Raises:
        ValueError: If the s3_path doesn't start with 's3://'.
    """
    if not s3_path.startswith("s3://"):
        raise ValueError(
            f"Not a valid S3 path: {s3_path}. S3 paths must start with 's3://'"
        )

    # Remove 's3://' prefix
    relative_path = s3_path[5:]

    # Convert to local path
    base_dir = Path("s3_simulation")
    return base_dir / relative_path


def ensure_directory_exists(path):
    """
    Ensures a directory exists, creating it if necessary.

    Args:
        path (str or Path): The directory path to ensure exists.

    Returns:
        Path: The path object of the directory.
    """
    path = Path(path)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    return path


def get_filename_from_path(path):
    """
    Extracts the filename from a path.

    Args:
        path (str or Path): The path to extract the filename from.

    Returns:
        str: The filename without the directory path.
    """
    return os.path.basename(str(path))
