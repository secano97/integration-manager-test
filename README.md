# Parser Transformation Engine

A Python-based transformation engine that processes files according to job definitions. This engine can currently:
- Extract ZIP files (ZipFileParser)
- Convert XML files to CSV (XmlToCsvParser)

The system is designed to be extensible, allowing for easy addition of new parser types.

## Architecture

The project follows a clean architecture and SOLID approach with the following components:

- **Factory Pattern**: Creates appropriate parser instances based on configuration
- **BaseParser Interface**: Defines the contract that all parsers must implement
- **Specialized Parsers**: Implement the BaseParser interface for specific file transformations
- **Orchestrator**: Coordinates the overall transformation process

## Setup (Local)

```bash
python3 -m venv integration_manager
source integration_manager/bin/activate      # or integration_manager\Scripts\activate on Windows
pip install -r requirements.txt
```

## Running the Engine

```bash
python main.py
```

By default, the engine will look for a `job_definition.json` file in the current directory. You can specify a different job definition file by passing it as an argument:

```bash
python main.py path/to/job_definition.json
```

## Running Unit Tests

```bash
python -m unittest discover tests/
```

## Project Structure

```
project_root/
├── docs/.                     # Docs related to the challenge
│   ├── Prueba para el rol.pdf # Challenge instructions
│   └── answers.md             # Contains the answers for point 1 and 3 of the challenge
├── main.py                    # Main orchestrator script
├── job_definition.json        # Job configuration file
├── s3_simulation/             # Local directory simulating S3 buckets
├── parsers/                   # Parser implementations
│   ├── __init__.py
│   ├── base_parser.py         # Abstract base parser class
│   ├── zip_file_parser.py     # ZIP file extractor
│   └── xml_to_csv_parser.py   # XML to CSV converter
├── factory/                   # Factory pattern implementation
│   ├── __init__.py
│   └── parser_factory.py      # Creates parser instances
├── utils/                     # Utility functions
│   ├── __init__.py
│   ├── logger.py              # Logging setup
│   └── path_utils.py          # Path conversion utilities
├── tests/                     # Unit tests
│   ├── test_zip_parser.py
│   ├── test_xml_parser.py
│   └── test_orchestrator.py
├── README.md                  # This file
└── requirements.txt           # Dependencies
```

## Notes

- S3 paths are mapped to local paths in `./s3_simulation/`.
- Transformation logic is defined in `job_definition.json`.
- The engine is designed to be easily extensible with new parser types.
- Error handling and logging are implemented throughout the codebase.