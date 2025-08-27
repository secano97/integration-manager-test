"""
Main script for the transformation engine.
This script reads job definitions from a JSON file and executes the specified transformations.
"""

import json
import sys
from pathlib import Path

from factory.parser_factory import ParserFactory
from utils.logger import setup_logger


class TransformationEngine:
    """
    Main orchestrator class for the transformation engine.
    """

    def __init__(self, job_definition_path):
        """
        Initialize the transformation engine.

        Args:
            job_definition_path (str or Path): Path to the job definition JSON file.
        """
        self.logger = setup_logger("TransformationEngine")
        self.job_definition_path = Path(job_definition_path)
        self.parser_factory = ParserFactory()

        # Statistics for tracking job results
        self.total_jobs = 0
        self.successful_jobs = 0
        self.failed_jobs = 0

        self.logger.info(
            "Transformation engine initialized with job definition: %s",
            self.job_definition_path,
        )

    def load_job_definition(self):
        """
        Load the job definition from the JSON file.

        Returns:
            dict: The job definition data, or None if loading failed.
        """
        try:
            self.logger.info("Loading job definition from %s", self.job_definition_path)

            if not self.job_definition_path.exists():
                self.logger.error(
                    "Job definition file not found: %s", self.job_definition_path
                )
                return None

            with open(self.job_definition_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.logger.info("Job definition loaded successfully")
            return data
        except json.JSONDecodeError:
            self.logger.error("Invalid JSON format in job definition file")
            return None
        except Exception as e:
            self.logger.error("Error loading job definition: %s", str(e))
            return None

    def run_transformation(self, transformation):
        """
        Execute a single transformation task.

        Args:
            transformation (dict): The transformation job definition.

        Returns:
            bool: True if the transformation was successful, False otherwise.
        """
        try:
            # Extract job parameters
            obj = transformation.get("object", {})
            kwargs = transformation.get("kwargs", {})

            origin = obj.get("origin")
            destiny = obj.get("destiny")
            classname = obj.get("classname")

            # Validate required parameters
            if not all([origin, destiny, classname]):
                self.logger.error("Missing required parameters in job definition")
                return False

            # Create and run the parser
            parser = self.parser_factory.create_parser(
                classname, origin, destiny, **kwargs
            )
            return parser.parse()

        except ValueError as e:
            self.logger.error("Invalid job configuration: %s", str(e))
            return False
        except Exception as e:
            self.logger.error("Error executing transformation: %s", str(e))
            return False

    def run(self):
        """
        Run all transformations defined in the job definition.

        Returns:
            bool: True if all transformations were successful, False otherwise.
        """
        # Load job definition
        job_data = self.load_job_definition()
        if not job_data:
            return False

        # Get transformations list
        transformations = job_data.get("transformations", [])
        if not transformations:
            self.logger.warning("No transformations found in job definition")
            return True

        # Initialize statistics
        self.total_jobs = len(transformations)
        self.successful_jobs = 0
        self.failed_jobs = 0

        self.logger.info(
            "Starting execution of %d transformation jobs", self.total_jobs
        )

        # Execute each transformation
        for i, transformation in enumerate(transformations, 1):
            self.logger.info("Processing job %d of %d", i, self.total_jobs)

            success = self.run_transformation(transformation)
            if success:
                self.successful_jobs += 1
            else:
                self.failed_jobs += 1

        # Log results
        self.logger.info("Transformation execution completed")
        self.logger.info(
            "Total jobs: %d, Successful: %d, Failed: %d",
            self.total_jobs,
            self.successful_jobs,
            self.failed_jobs,
        )

        return self.failed_jobs == 0


def main():
    """
    Main entry point for the transformation engine.
    """
    # Default job definition path
    job_path = "job_definition.json"

    # Allow overriding job definition path from command line
    if len(sys.argv) > 1:
        job_path = sys.argv[1]

    # Create and run the transformation engine
    engine = TransformationEngine(job_path)
    success = engine.run()

    # Set exit code based on success
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
