# Live Differ

A real-time file difference viewer that automatically updates when files change.

![Live Differ Screenshot](assets/images/screenshot.png)

## Features

- Real-time file difference visualization
- Automatic updates when files change
- Side-by-side comparison view
- File metadata display
- Error handling and logging

## Installation

You can install Live Differ using pip:

```bash
pip install git+https://github.com/manthanby/live_differ.git
```

Or using uv:

```bash
uv pip install git+https://github.com/manthanby/live_differ.git
```

Alternatively, you can install from source:

1. Clone the repository:
```bash
git clone <repository-url>
cd live_differ
```

2. Install using pip:
```bash
pip install .
```

Or using uv:
```bash
uv pip install .
```

## Usage

After installation, you can run Live Differ directly from the command line:

```bash
live-differ
```

This will start the Live Differ server on http://127.0.0.1:5000 by default.

You can configure the following environment variables:
- `FLASK_HOST`: Server host (default: 127.0.0.1)
- `FLASK_PORT`: Server port (default: 5000)
- `FLASK_DEBUG`: Enable debug mode (default: False)

Example with custom configuration:
```bash
FLASK_HOST=0.0.0.0 FLASK_PORT=8000 live-differ
```

Once the server is running:
1. Open your web browser and navigate to the server address
2. Upload or select the files you want to compare
3. The differences will be displayed in real-time and will update automatically when files change

This is a client-side application that runs locally on your machine. To use it:

Run the application with two files to compare:

```bash
python app.py file1.txt file2.txt
```

Then open your browser and navigate to `http://localhost:5000`

## Configuration

The application uses minimal configuration since it runs locally:

- `FLASK_DEBUG`: Enable debug mode (default: False)
- `FLASK_PORT`: Port to listen on (default: 5000)

## Logging

Logs are written to the `logs/app.log` file with rotation enabled (10MB max size, keeping 10 backup files).

## Error Handling

The application includes comprehensive error handling:
- File validation (existence, permissions)
- UTF-8 encoding validation
- General error pages with helpful messages
- Detailed logging of all errors

## Security Considerations

Since this is a client-side application that only runs locally:
- File size limit of 16MB
- Input validation for file paths
- No execution of file contents
- Only processes local files

## License

[Add your license here]
