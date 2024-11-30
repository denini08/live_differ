# Live Differ

A real-time file difference viewer that automatically updates when files change. Live Differ provides an intuitive web interface for comparing files side-by-side with real-time updates when either file is modified.

![Live Differ Screenshot](assets/images/screenshot.png)

## Features

- Real-time file difference visualization
- Side-by-side comparison view
- Automatic updates when files change
- Web-based interface
- Modern command-line interface
- Easy to use and configure

## Installation

### From PyPI
```bash
pip install live-differ
```

### From Git
```bash
# Install latest version
pip install git+https://github.com/manthanby/live_differ.git

# Install specific version
pip install git+https://github.com/manthanby/live_differ.git@v1.0.0
```

## Quick Start

1. Compare two files:
```bash
live-differ file1.txt file2.txt
```

2. Open your browser to view the comparison (default: http://127.0.0.1:5000)

3. Edit either file and see the changes update in real-time!

## Usage Examples

### Basic Usage
```bash
# Compare two files
live-differ path/to/file1.txt path/to/file2.txt
```

### Advanced Options
```bash
# Use custom host and port
live-differ file1.txt file2.txt --host 0.0.0.0 --port 8000

# Enable debug mode
live-differ file1.txt file2.txt --debug

# View all options
live-differ --help
```

## Configuration

You can configure Live Differ using environment variables:

```bash
# Set custom host and port
export FLASK_HOST=0.0.0.0
export FLASK_PORT=8000

# Enable debug mode
export FLASK_DEBUG=1
```

## Contributing

Interested in contributing? Check out our [Contributing Guidelines](CONTRIBUTING.md) for details on how to get started.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
