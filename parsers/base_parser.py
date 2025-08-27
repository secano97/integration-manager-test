"""
Base abstract parser class that all parser implementations should inherit from.
"""

from abc import ABC, abstractmethod

from utils.logger import setup_logger
from utils.path_utils import s3_to_local_path, ensure_directory_exists


class BaseParser(ABC):
    """
    Abstract base class for all parsers.

    All parsers must implement the parse method.
    """

    def __init__(self, origin, destiny, **kwargs):
        """
        Initialize the base parser with common attributes.

        Args:
            origin (str): S3 path to the source file.
            destiny (str): S3 path to the destination directory.
            **kwargs: Additional arguments required by specific parsers.
        """
        self.logger = setup_logger(self.__class__.__name__)
        self.origin = origin
        self.destiny = destiny

        # Convert S3 paths to local paths
        self.local_origin = s3_to_local_path(origin)
        self.local_destiny = s3_to_local_path(destiny)

        # Store any additional arguments
        self.kwargs = kwargs

        # Log initialization
        self.logger.info(
            f"Initialized {self.__class__.__name__} with origin: {origin}, destiny: {destiny}"
        )

    @abstractmethod
    def parse(self):
        """
        Transform the input file according to the parser's logic and save the result.

        This method must be implemented by all derived classes.

        Returns:
            bool: True if parsing was successful, False otherwise.
        """
        pass

    def validate_input(self):
        """
        Validate that the input file exists and is accessible.

        Returns:
            bool: True if the input file is valid, False otherwise.
        """
        if not self.local_origin.exists():
            self.logger.error(f"Input file does not exist: {self.local_origin}")
            return False

        self.logger.debug(f"Input file validated: {self.local_origin}")
        return True

    def ensure_output_directory(self):
        """
        Ensure the output directory exists, creating it if necessary.

        Returns:
            Path: The path to the output directory.
        """
        return ensure_directory_exists(self.local_destiny)
