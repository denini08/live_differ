# Contributing to Live Differ

Thank you for your interest in contributing to Live Differ! This document provides comprehensive guidelines and instructions for contributing to the project.

## Table of Contents
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing Guidelines](#testing-guidelines)
- [Documentation Guidelines](#documentation-guidelines)
- [Building and Publishing](#building-and-publishing)
- [Error Handling](#error-handling)
- [Logging Guidelines](#logging-guidelines)
- [Pull Request Process](#pull-request-process)

## Development Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)
- Git

### Setting Up Development Environment

1. Fork the repository on GitHub

2. Clone your fork:
```bash
git clone https://github.com/YOUR_USERNAME/live_differ.git
cd live_differ
```

3. Add the upstream repository:
```bash
git remote add upstream https://github.com/manthanby/live_differ.git
```

4. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate     # On Windows
```

5. Install development dependencies:
```bash
pip install -e .
pip install build twine pytest pytest-cov black isort flake8
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
│   │   ├── css/        # Stylesheets
│   │   └── js/         # JavaScript files
│   ├── templates/       # HTML templates
│   └── assets/          # Project assets
│       └── images/      # Images for documentation
├── tests/               # Test directory
│   ├── __init__.py
│   ├── test_differ.py
│   └── test_watcher.py
├── pyproject.toml       # Project configuration
├── MANIFEST.in         # Package manifest
├── README.md          # User documentation
├── CONTRIBUTING.md    # Contributor documentation
└── LICENSE           # License information
```

### Key Components

1. **Core Application (core.py)**
   - Flask application setup
   - Route definitions
   - WebSocket handling
   - Error handling

2. **Command Line Interface (cli.py)**
   - Command-line argument parsing
   - Environment variable handling
   - Application entry point

3. **Differ Module (modules/differ.py)**
   - File comparison logic
   - Difference calculation
   - Result formatting

4. **Watcher Module (modules/watcher.py)**
   - File system monitoring
   - Change detection
   - Event handling

## Development Workflow

### 1. Creating a New Feature

1. Update your main branch:
```bash
git checkout main
git pull upstream main
```

2. Create a feature branch:
```bash
git checkout -b feature/your-feature-name
```

3. Make your changes following our coding standards

4. Test your changes:
```bash
pytest tests/
```

### 2. Code Quality Checks

Run these before committing:

```bash
# Format code
black live_differ tests
isort live_differ tests

# Check style
flake8 live_differ tests

# Run tests with coverage
pytest --cov=live_differ tests/
```

### 3. Committing Changes

Follow these commit message guidelines:
- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit first line to 72 characters
- Reference issues and pull requests

Example:
```bash
git commit -m "Add real-time update feature

- Implement WebSocket connection
- Add file change detection
- Update UI automatically
- Add error handling

Fixes #123"
```

## Code Style Guidelines

### Python Style
- Follow [PEP 8](https://pep8.org/)
- Use 4 spaces for indentation
- Maximum line length: 88 characters (Black default)
- Use meaningful variable and function names

### Documentation Style
- Use Google-style docstrings
- Document all public functions, classes, and methods
- Include type hints

Example:
```python
def compare_files(file1: str, file2: str) -> Dict[str, Any]:
    """Compare two files and return their differences.

    Args:
        file1 (str): Path to the first file
        file2 (str): Path to the second file

    Returns:
        Dict[str, Any]: Dictionary containing:
            - 'differences': List of line differences
            - 'metadata': Dict with file information

    Raises:
        FileNotFoundError: If either file doesn't exist
        PermissionError: If files can't be read
    """
```

## Testing Guidelines

### Test Structure
- Use pytest for testing
- Organize tests by module
- Use fixtures for common setup
- Include unit and integration tests

### Writing Tests
```python
def test_file_differ():
    """Test file comparison functionality."""
    # Arrange
    differ = FileDiffer("test1.txt", "test2.txt")
    
    # Act
    result = differ.compare()
    
    # Assert
    assert result is not None
    assert "differences" in result
```

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_differ.py

# Run with coverage
pytest --cov=live_differ --cov-report=html
```

## Building and Publishing

### Building the Package
```bash
# Clean previous builds
rm -rf build/ dist/ *.egg-info/

# Build package
python -m build

# Check distribution
twine check dist/*
```

### Testing the Build
```bash
# Create a new virtual environment
python -m venv test_env
source test_env/bin/activate

# Install the built package
pip install dist/*.whl

# Test the installation
live-differ --help
```

## Error Handling

### Guidelines
1. Use custom exceptions for specific errors
2. Provide clear error messages
3. Include context in exceptions
4. Log errors appropriately
5. Handle edge cases

Example:
```python
class DifferError(Exception):
    """Base exception for differ-related errors."""
    pass

class FileComparisonError(DifferError):
    """Raised when file comparison fails."""
    pass

def compare_files(file1: str, file2: str) -> Dict[str, Any]:
    try:
        # Comparison logic
    except OSError as e:
        raise FileComparisonError(f"Failed to compare files: {e}")
```

## Logging Guidelines

### Log Levels
- DEBUG: Detailed information for debugging
- INFO: General operational events
- WARNING: Unexpected but handled events
- ERROR: Serious issues that need attention
- CRITICAL: System-level failures

### Logging Example
```python
import logging

logger = logging.getLogger(__name__)

def process_file(filename: str) -> None:
    logger.debug("Starting file processing: %s", filename)
    try:
        # Processing logic
        logger.info("Successfully processed file: %s", filename)
    except Exception as e:
        logger.error("Failed to process file: %s", str(e))
        raise
```

## Pull Request Process

1. **Before Submitting**
   - Update your branch with main
   - Run all tests and style checks
   - Update documentation if needed
   - Add tests for new features

2. **PR Description**
   - Clearly describe the changes
   - Link related issues
   - Include screenshots for UI changes
   - List any breaking changes

3. **Review Process**
   - Address reviewer comments
   - Keep the PR focused and small
   - Be responsive to feedback

4. **After Merging**
   - Delete your feature branch
   - Update your local main branch

## Questions or Need Help?

- Open an issue for bugs or feature requests
- Join our discussions for questions
- Tag maintainers for urgent issues

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License.
