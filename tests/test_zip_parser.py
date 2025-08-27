"""
Tests for the ZipFileParser class.
"""

import unittest
import shutil
import zipfile
from pathlib import Path
import tempfile

from parsers.zip_file_parser import ZipFileParser


class TestZipFileParser(unittest.TestCase):
    """
    Test cases for the ZipFileParser class.
    """

    def setUp(self):
        """
        Set up test environment before each test case.
        """
        # Create temporary directories
        self.temp_dir = Path(tempfile.mkdtemp())

        # Create directories for simulating S3 structure
        self.s3_dir = self.temp_dir / "s3_simulation"
        self.source_dir = self.s3_dir / "test-bucket" / "source"
        self.dest_dir = self.s3_dir / "test-bucket" / "dest"

        self.source_dir.mkdir(parents=True, exist_ok=True)
        self.dest_dir.mkdir(parents=True, exist_ok=True)

        # Create test content
        self.test_file = self.source_dir / "test.txt"
        self.test_file.write_text("Test content for ZIP parser")

        # Create a test ZIP file
        self.zip_file = self.source_dir / "test.zip"
        with zipfile.ZipFile(self.zip_file, "w") as zipf:
            zipf.write(self.test_file, arcname="test.txt")

        # Define S3 paths for testing
        self.s3_origin = f"s3://test-bucket/source/test.zip"
        self.s3_destiny = f"s3://test-bucket/dest/"

    def tearDown(self):
        """
        Clean up test environment after each test case.
        """
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)

    def test_parse_success(self):
        """
        Test successful parsing of a ZIP file.
        """
        # Initialize parser
        parser = ZipFileParser(self.s3_origin, self.s3_destiny)

        # Adjust local paths to point to our temp directory
        parser.local_origin = self.zip_file
        parser.local_destiny = self.dest_dir

        # Run the parser
        result = parser.parse()

        # Assert result is True (success)
        self.assertTrue(result)

        # Assert file was extracted correctly
        extracted_file = self.dest_dir / "test.txt"
        self.assertTrue(extracted_file.exists())
        self.assertEqual(extracted_file.read_text(), "Test content for ZIP parser")

    def test_parse_file_not_found(self):
        """
        Test parsing with a non-existent ZIP file.
        """
        # Initialize parser with non-existent file
        parser = ZipFileParser(
            "s3://test-bucket/source/nonexistent.zip", self.s3_destiny
        )

        # Adjust local paths to point to our temp directory
        parser.local_origin = self.source_dir / "nonexistent.zip"
        parser.local_destiny = self.dest_dir

        # Run the parser
        result = parser.parse()

        # Assert result is False (failure)
        self.assertFalse(result)

    def test_parse_invalid_zip(self):
        """
        Test parsing with an invalid ZIP file.
        """
        # Create an invalid ZIP file (just a text file)
        invalid_zip = self.source_dir / "invalid.zip"
        invalid_zip.write_text("This is not a valid ZIP file")

        # Initialize parser
        parser = ZipFileParser("s3://test-bucket/source/invalid.zip", self.s3_destiny)

        # Adjust local paths to point to our temp directory
        parser.local_origin = invalid_zip
        parser.local_destiny = self.dest_dir

        # Run the parser
        result = parser.parse()

        # Assert result is False (failure)
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
