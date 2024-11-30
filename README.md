# Live Differ

A real-time file difference viewer that automatically updates when files change. Live Differ provides an intuitive web interface for comparing files side-by-side with real-time updates when either file is modified.

![Live Differ Screenshot](assets/images/screenshot.png)

## Features

- Real-time file difference visualization
- Automatic updates when files change
- Side-by-side comparison view
- Modern command-line interface with auto-completion
- File metadata display
- Comprehensive error handling and logging
- Environment variable support for configuration
- Development-friendly debug mode

## Installation

### Option 1: Install from PyPI (Recommended)
```bash
pip install live-differ
```

### Option 2: Install directly from Git
```bash
# Install from main branch
pip install git+https://github.com/manthanby/live_differ.git

# Install from a specific branch
pip install git+https://github.com/manthanby/live_differ.git@branch-name

# Install from a specific tag or release
pip install git+https://github.com/manthanby/live_differ.git@v1.0.0
```

### Option 3: Install from Source
1. Clone the repository:
```bash
git clone <repository-url>
cd live_differ
```

2. Create and activate a virtual environment (recommended):
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

## Usage

Live Differ features a modern command-line interface with various options and automatic help:

### Basic Usage

Compare two files with default settings:
```bash
live-differ file1.txt file2.txt
```

### Advanced Usage

```bash
# Custom host and port
live-differ file1.txt file2.txt --host 0.0.0.0 --port 8000

# Enable debug mode
live-differ file1.txt file2.txt --debug

# View all available options
live-differ --help
```

### Using Environment Variables

All configuration options can be set using environment variables:

```bash
# Set configuration via environment variables
export FLASK_HOST=0.0.0.0
export FLASK_PORT=8000
export FLASK_DEBUG=1

# Run with environment configuration
live-differ file1.txt file2.txt
```

After starting the server, open your browser and navigate to the displayed URL (default: `http://127.0.0.1:5000`).

## Configuration

The application supports various configuration options:

| Option | Environment Variable | Default | Description |
|--------|---------------------|---------|-------------|
| Host | FLASK_HOST | 127.0.0.1 | Server host address |
| Port | FLASK_PORT | 5000 | Server port number |
| Debug Mode | FLASK_DEBUG | False | Enable debug mode |

### Command-Line Options

```
Options:
  -h, --host TEXT          Host to bind the server to [default: 127.0.0.1]
  -p, --port INTEGER       Port to run the server on [default: 5000]
  --debug                  Enable debug mode
  --help                   Show this message and exit.
```

## Development

### Directory Structure

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
├── LICENSE            # License information
└── requirements.txt   # Development dependencies
```

### Development Setup

1. Clone the repository
2. Create and activate a virtual environment
3. Install in development mode:
```bash
pip install -e .
```

4. Make your changes
5. Test the changes:
```bash
live-differ test_sample1.txt test_sample2.txt
```

## Security Considerations

The application implements several security measures:
- File size limit of 16MB to prevent memory issues
- Input validation for all file paths and parameters
- No execution of file contents
- Local-only file access
- Debug mode disabled by default

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Add your license here]
