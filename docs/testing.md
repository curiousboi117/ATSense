# Testing Protocols

ATSense includes unit tests to ensure that all parser, NLP, scoring, and REST API functionalities operate correctly.

## Automated Test Coverage

The testing suite contains:
* `test_parser.py`: Verifies that file type restrictions, file size limits, and empty content checks throw correct errors.
* `test_nlp.py`: Asserts correct email, phone, name, and section header parsing.
* `test_ats.py`: Verifies scoring ranges and compliance checks.
* `test_api.py`: Tests the integrity of endpoint connections (e.g. `/api/health`, `/api/history`, `/api/reset-all`).

## Execution

Run the tests inside the backend directory:
```bash
pytest backend/tests/
```
Ensure all tests execute and pass without error.
