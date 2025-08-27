"""
Parser for converting XML files to CSV format.
"""

import csv
import xml.etree.ElementTree as ET

from parsers.base_parser import BaseParser
from utils.path_utils import get_filename_from_path


class XmlToCsvParser(BaseParser):
    """
    Parser for converting XML files to CSV format.
    """

    def parse(self):
        """
        Convert an XML file to CSV format.

        The implementation assumes a simple structure where:
        - XML has a root element with child elements representing rows
        - Each child element has the same structure/fields

        Returns:
            bool: True if conversion was successful, False otherwise.
        """
        # Validate input file
        if not self.validate_input():
            return False

        # Ensure output directory exists
        output_dir = self.ensure_output_directory()

        try:
            self.logger.info(
                "Starting XML to CSV conversion from %s", self.local_origin
            )

            # Parse XML
            tree = ET.parse(self.local_origin)
            root = tree.getroot()

            # Get the first child element to determine column names
            if len(root) == 0:
                self.logger.warning("XML file has no child elements under root")
                return False

            # Determine output filename (replace .xml extension with .csv)
            input_filename = get_filename_from_path(self.local_origin)
            output_filename = input_filename.rsplit(".", 1)[0] + ".csv"
            output_path = output_dir / output_filename

            # Extract field names from the first child element
            first_element = root[0]
            field_names = [child.tag for child in first_element]

            # Open CSV file for writing
            with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=field_names)
                writer.writeheader()

                # Process all child elements
                for element in root:
                    row = {child.tag: child.text for child in element}
                    writer.writerow(row)

            self.logger.info(
                "XML to CSV conversion completed successfully to %s", output_path
            )
            return True

        except ET.ParseError:
            self.logger.error("Failed to parse XML file %s", self.local_origin)
            return False
        except (IOError, PermissionError) as e:
            self.logger.error("File I/O error: %s", str(e))
            return False
        except Exception as e:
            self.logger.error("Error during XML to CSV conversion: %s", str(e))
            return False
