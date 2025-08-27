"""
Factory for creating parser instances based on the parser type.
"""

from parsers.zip_file_parser import ZipFileParser
from parsers.xml_to_csv_parser import XmlToCsvParser
from utils.logger import setup_logger


class ParserFactory:
    """
    Factory class for creating parser instances based on the parser type.
    """

    def __init__(self):
        """
        Initialize the parser factory.
        """
        self.logger = setup_logger("ParserFactory")

        # Register available parsers
        self.parsers = {
            "ZipFileParser": ZipFileParser,
            "XmlToCsvParser": XmlToCsvParser,
        }

    def create_parser(self, classname, origin, destiny, **kwargs):
        """
        Create a parser instance based on the class name.

        Args:
            classname (str): The name of the parser class to instantiate.
            origin (str): S3 path to the source file.
            destiny (str): S3 path to the destination directory.
            **kwargs: Additional arguments required by specific parsers.

        Returns:
            BaseParser: An instance of the requested parser, or None if not found.

        Raises:
            ValueError: If the parser class is not registered.
        """
        if classname not in self.parsers:
            self.logger.error("Parser class not found: %s", classname)
            raise ValueError(f"Unknown parser class: {classname}")

        parser_class = self.parsers[classname]
        self.logger.info("Creating parser: %s", classname)

        return parser_class(origin, destiny, **kwargs)
