"""
Tests for the TransformationEngine class.
"""

import unittest
import json
import tempfile
import shutil
from pathlib import Path
import zipfile

from main import TransformationEngine


class TestTransformationEngine(unittest.TestCase):
    """
    Test cases for the TransformationEngine class.
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
        self.test_file.write_text("Test content for orchestrator test")

        # Create a test ZIP file
        self.zip_file = self.source_dir / "test.zip"
        with zipfile.ZipFile(self.zip_file, "w") as zipf:
            zipf.write(self.test_file, arcname="test.txt")

        # Create a test XML file
        self.xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<transactions>
  <transaction>
    <id>1001</id>
    <date>2023-05-15</date>
    <amount>150.75</amount>
  </transaction>
  <transaction>
    <id>1002</id>
    <date>2023-05-16</date>
    <amount>75.20</amount>
  </transaction>
</transactions>"""

        self.xml_file = self.source_dir / "test.xml"
        self.xml_file.write_text(self.xml_content)

        # Create a test job definition
        self.job_data = {
            "transformations": [
                {
                    "object": {
                        "origin": "s3://test-bucket/source/test.zip",
                        "destiny": "s3://test-bucket/dest/",
                        "parser": "unzip",
                        "classname": "ZipFileParser",
                    },
                    "kwargs": {},
                },
                {
                    "object": {
                        "origin": "s3://test-bucket/source/test.xml",
                        "destiny": "s3://test-bucket/dest/",
                        "parser": "xml_to_csv",
                        "classname": "XmlToCsvParser",
                    },
                    "kwargs": {},
                },
            ]
        }

        self.job_file = self.temp_dir / "test_job.json"
        with open(self.job_file, "w", encoding="utf-8") as f:
            json.dump(self.job_data, f)

    def tearDown(self):
        """
        Clean up test environment after each test case.
        """
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)

    def test_load_job_definition(self):
        """
        Test loading a job definition file.
        """
        # Initialize engine
        engine = TransformationEngine(self.job_file)

        # Load job definition
        job_data = engine.load_job_definition()

        # Assert job data was loaded correctly
        self.assertIsNotNone(job_data)
        # Only check the structure if job_data is not None
        if job_data is not None:  # Add this check to handle potential None
            self.assertIn("transformations", job_data)
            self.assertEqual(len(job_data["transformations"]), 2)

    def test_run_transformation(self):
        """
        Test running a single transformation.
        """
        # Initialize engine
        engine = TransformationEngine(self.job_file)

        # Patch the local_origin and local_destiny properties for testing
        def monkey_patch_parser(parser):
            if "zip" in parser.origin.lower():
                parser.local_origin = self.zip_file
            else:
                parser.local_origin = self.xml_file
            parser.local_destiny = self.dest_dir
            return parser

        # Patch the factory to use our test files
        original_create_parser = engine.parser_factory.create_parser

        def patched_create_parser(*args, **kwargs):
            parser = original_create_parser(*args, **kwargs)
            return monkey_patch_parser(parser)

        engine.parser_factory.create_parser = patched_create_parser

        # Run the first transformation
        result = engine.run_transformation(self.job_data["transformations"][0])

        # Assert transformation was successful
        self.assertTrue(result)

        # Check if the file was extracted
        extracted_file = self.dest_dir / "test.txt"
        self.assertTrue(extracted_file.exists())

    def test_run_complete_job(self):
        """
        Test running a complete job with multiple transformations.
        """
        # Initialize engine
        engine = TransformationEngine(self.job_file)

        # Patch the local_origin and local_destiny properties for testing
        def monkey_patch_parser(parser):
            if "zip" in parser.origin.lower():
                parser.local_origin = self.zip_file
            else:
                parser.local_origin = self.xml_file
            parser.local_destiny = self.dest_dir
            return parser

        # Patch the factory to use our test files
        original_create_parser = engine.parser_factory.create_parser

        def patched_create_parser(*args, **kwargs):
            parser = original_create_parser(*args, **kwargs)
            return monkey_patch_parser(parser)

        engine.parser_factory.create_parser = patched_create_parser

        # Run the job
        result = engine.run()

        # Assert job was successful
        self.assertTrue(result)

        # Check if all files were processed
        self.assertEqual(engine.total_jobs, 2)
        self.assertEqual(engine.successful_jobs, 2)
        self.assertEqual(engine.failed_jobs, 0)

        # Check if both output files exist
        extracted_file = self.dest_dir / "test.txt"
        csv_file = self.dest_dir / "test.csv"
        self.assertTrue(extracted_file.exists())
        self.assertTrue(csv_file.exists())


if __name__ == "__main__":
    unittest.main()
