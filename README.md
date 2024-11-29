# Live Differ

A real-time file difference viewer that automatically updates when files change.

## Features

- Real-time file difference visualization
- Automatic updates when files change
- Side-by-side comparison view
- File metadata display
- Error handling and logging
- Production-ready configuration

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd live_differ
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

The application can be configured using environment variables:

- `FLASK_DEBUG`: Enable debug mode (default: False)
- `FLASK_HOST`: Host to bind to (default: 127.0.0.1)
- `FLASK_PORT`: Port to listen on (default: 5000)
- `SECRET_KEY`: Flask secret key (default: dev-key-please-change-in-production)

## Usage

Run the application with two files to compare:

```bash
python app.py file1.txt file2.txt
```

Then open your browser and navigate to `http://localhost:5000`

## Production Deployment

For production deployment:

1. Set proper environment variables:
```bash
export FLASK_DEBUG=False
export SECRET_KEY=your-secure-secret-key
export FLASK_HOST=0.0.0.0  # If you want to accept external connections
```

2. Use a production WSGI server like Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 'app:app'
```

## Logging

Logs are written to the `logs/app.log` file with rotation enabled (10MB max size, keeping 10 backup files).

## Error Handling

The application includes comprehensive error handling:
- File validation (existence, permissions)
- UTF-8 encoding validation
- General error pages with helpful messages
- Detailed logging of all errors

## Security Considerations

- File size limit of 16MB
- Input validation for file paths
- No execution of file contents
- Configurable host binding
- Secret key configuration

## License

[Add your license here]
