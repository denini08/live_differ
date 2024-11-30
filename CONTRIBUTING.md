# Contributing to Live Differ

Thank you for your interest in contributing to Live Differ! This document provides guidelines and instructions for contributing to the project.

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/manthanby/live_differ.git
cd live_differ
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate     # On Windows
```

3. Install in development mode:
```bash
pip install -e .
```

## Project Structure

```
live_differ/
├── live_differ/          # Main package directory
│   ├── __init__.py      # Package initialization
│   ├── __main__.py      # Entry point for running as module
│   ├── cli.py           # Command-line interface
│   ├── core.py          # Core application logic
│   ├── modules/         # Core modules
│   │   ├── __init__.py
│   │   ├── differ.py    # File diffing logic
│   │   └── watcher.py   # File change monitoring
│   ├── static/          # Static web assets
│   ├── templates/       # HTML templates
│   └── assets/          # Project assets
├── pyproject.toml       # Project configuration and metadata
├── README.md           # Project documentation
└── LICENSE            # License information
```

## Development Workflow

1. Create a new branch for your feature/fix:
```bash
git checkout -b feature-name
```

2. Make your changes and test them:
```bash
live-differ test_sample1.txt test_sample2.txt
```

3. Ensure your code follows the project's style guidelines

4. Commit your changes:
```bash
git add .
git commit -m "Description of changes"
```

5. Push to your fork and submit a pull request

## Building the Package

1. Install build tools:
```bash
pip install build twine
```

2. Build the package:
```bash
python -m build
```

3. Test the built package locally:
```bash
pip install dist/*.whl
```

## Code Style Guidelines

- Follow PEP 8 style guide for Python code
- Use meaningful variable and function names
- Add docstrings for functions and classes
- Keep functions focused and single-purpose
- Add comments for complex logic

## Testing

Before submitting a pull request:
1. Test your changes thoroughly
2. Ensure all existing functionality works
3. Add new test cases if needed

## Logging

The application uses Python's logging module with the following features:
- Logs are written to `logs/app.log`
- Rotation enabled (10MB max size)
- Keeps 10 backup files
- Includes timestamps, log levels, and source information

## Error Handling Guidelines

When adding new features:
- Add appropriate error handling
- Use custom exceptions when needed
- Provide helpful error messages
- Log errors appropriately
- Return meaningful HTTP status codes for web endpoints

## Questions or Need Help?

Feel free to:
- Open an issue for questions
- Join our discussions
- Reach out to maintainers

Thank you for contributing to Live Differ!
