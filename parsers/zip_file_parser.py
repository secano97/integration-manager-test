"""
Parser for extracting ZIP files.
"""

import zipfile

from parsers.base_parser import BaseParser


class ZipFileParser(BaseParser):
    """
    Parser for extracting ZIP files to a specified destination.
    """

    def parse(self):
        """
        Extract all contents of the ZIP file to the destination directory.

        Returns:
            bool: True if extraction was successful, False otherwise.
        """
        # Validate input file
        if not self.validate_input():
            return False

        # Ensure output directory exists
        output_dir = self.ensure_output_directory()

        try:
            self.logger.info(
                "Starting ZIP extraction from %s to %s", self.local_origin, output_dir
            )

            # Extract the zip file
            with zipfile.ZipFile(self.local_origin, "r") as zip_ref:
                zip_ref.extractall(output_dir)

            self.logger.info("ZIP extraction completed successfully")
            return True
        except zipfile.BadZipFile:
            self.logger.error("The file %s is not a valid ZIP file", self.local_origin)
            return False
        except PermissionError:
            self.logger.error("Permission denied when extracting to %s", output_dir)
            return False
        except Exception as e:
            self.logger.error("Error during ZIP extraction: %s", str(e))
            return False
