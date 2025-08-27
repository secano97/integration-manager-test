"""
Tests for the XmlToCsvParser class.
"""

import unittest
import csv
import tempfile
import shutil
from pathlib import Path

from parsers.xml_to_csv_parser import XmlToCsvParser


class TestXmlToCsvParser(unittest.TestCase):
    """
    Test cases for the XmlToCsvParser class.
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

        # Create a test XML file
        self.xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<transactions>
  <transaction>
    <id>1001</id>
    <date>2023-05-15</date>
    <amount>150.75</amount>
    <description>Payment for services</description>
  </transaction>
  <transaction>
    <id>1002</id>
    <date>2023-05-16</date>
    <amount>75.20</amount>
    <description>Subscription renewal</description>
  </transaction>
</transactions>"""

        self.xml_file = self.source_dir / "test.xml"
        self.xml_file.write_text(self.xml_content)

        # Define S3 paths for testing
        self.s3_origin = "s3://test-bucket/source/test.xml"
        self.s3_destiny = "s3://test-bucket/dest/"

    def tearDown(self):
        """
        Clean up test environment after each test case.
        """
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)

    def test_parse_success(self):
        """
        Test successful parsing of an XML file to CSV.
        """
        # Initialize parser
        parser = XmlToCsvParser(self.s3_origin, self.s3_destiny)

        # Adjust local paths to point to our temp directory
        parser.local_origin = self.xml_file
        parser.local_destiny = self.dest_dir

        # Run the parser
        result = parser.parse()

        # Assert result is True (success)
        self.assertTrue(result)

        # Assert CSV file was created correctly
        csv_file = self.dest_dir / "test.csv"
        self.assertTrue(csv_file.exists())

        # Read the CSV file and check its contents
        with open(csv_file, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

            # Check number of rows
            self.assertEqual(len(rows), 2)

            # Check fields
            self.assertEqual(rows[0]["id"], "1001")
            self.assertEqual(rows[0]["date"], "2023-05-15")
            self.assertEqual(rows[0]["amount"], "150.75")
            self.assertEqual(rows[0]["description"], "Payment for services")

            self.assertEqual(rows[1]["id"], "1002")
            self.assertEqual(rows[1]["date"], "2023-05-16")
            self.assertEqual(rows[1]["amount"], "75.20")
            self.assertEqual(rows[1]["description"], "Subscription renewal")

    def test_parse_file_not_found(self):
        """
        Test parsing with a non-existent XML file.
        """
        # Initialize parser with non-existent file
        parser = XmlToCsvParser(
            "s3://test-bucket/source/nonexistent.xml", self.s3_destiny
        )

        # Adjust local paths to point to our temp directory
        parser.local_origin = self.source_dir / "nonexistent.xml"
        parser.local_destiny = self.dest_dir

        # Run the parser
        result = parser.parse()

        # Assert result is False (failure)
        self.assertFalse(result)

    def test_parse_invalid_xml(self):
        """
        Test parsing with an invalid XML file.
        """
        # Create an invalid XML file
        invalid_xml = self.source_dir / "invalid.xml"
        invalid_xml.write_text("This is not a valid XML file")

        # Initialize parser
        parser = XmlToCsvParser("s3://test-bucket/source/invalid.xml", self.s3_destiny)

        # Adjust local paths to point to our temp directory
        parser.local_origin = invalid_xml
        parser.local_destiny = self.dest_dir

        # Run the parser
        result = parser.parse()

        # Assert result is False (failure)
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
