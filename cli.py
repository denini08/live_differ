#!/usr/bin/env python3
import os
import sys
import typer
import logging
from flask_socketio import SocketIO
from watchdog.observers import Observer
from app import app, setup_logging
from modules.differ import FileDiffer
from modules.watcher import FileChangeHandler

# Configure Flask and Werkzeug loggers to be quiet
logging.getLogger('werkzeug').disabled = True
cli = typer.Typer(
    name="live_differ",
    help="A real-time file difference viewer with live updates",
    add_completion=True
)

def validate_files(file1: str, file2: str):
    """Validate that both files exist and are readable."""
    if not os.path.isfile(file1):
        raise typer.BadParameter(f"File not found: {file1}")
    if not os.path.isfile(file2):
        raise typer.BadParameter(f"File not found: {file2}")
    if not os.access(file1, os.R_OK):
        raise typer.BadParameter(f"File not readable: {file1}")
    if not os.access(file2, os.R_OK):
        raise typer.BadParameter(f"File not readable: {file2}")
    return True

def start_message(host: str, port: int):
    """Display the startup message with the URL."""
    protocol = "http"
    if host == "0.0.0.0":
        host = "localhost"
    url = f"{protocol}://{host}:{port}"
    typer.echo(f"\nLive Differ is running!")
    typer.echo(f"View the diff at: {url}")
    typer.echo("\nPress Ctrl+C to quit.")

class QuietSocketIO(SocketIO):
    def run(self, app, **kwargs):
        # Suppress Flask's logging output
        import flask.cli
        flask.cli.show_server_banner = lambda *args, **kwargs: None
        
        # Call the original run method
        super().run(app, **kwargs)

@cli.command()
def run(
    file1: str = typer.Argument(
        ...,
        help="First file to compare",
        show_default=False
    ),
    file2: str = typer.Argument(
        ...,
        help="Second file to compare",
        show_default=False
    ),
    host: str = typer.Option(
        "127.0.0.1",
        "--host",
        "-h",
        help="Host to bind the server to",
        envvar="FLASK_HOST"
    ),
    port: int = typer.Option(
        5000,
        "--port",
        "-p",
        help="Port to run the server on",
        envvar="FLASK_PORT"
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Enable debug mode",
        envvar="FLASK_DEBUG"
    )
):
    """
    Run the Live Differ application to compare two files in real-time.
    
    The application will watch for changes in both files and update the diff view
    automatically when either file changes.
    """
    # Validate files
    validate_files(file1, file2)
    
    # Setup logging
    setup_logging()
    
    # Configure Flask app
    app.config['DEBUG'] = debug
    
    # Store file paths in app config for access in routes
    app.config['FILE1'] = os.path.abspath(file1)
    app.config['FILE2'] = os.path.abspath(file2)
    
    try:
        # Initialize differ
        differ = FileDiffer(app.config['FILE1'], app.config['FILE2'])
        
        # Create quiet version of SocketIO
        quiet_socketio = QuietSocketIO(app)
        
        # Set up file watching
        event_handler = FileChangeHandler(differ, quiet_socketio)
        observer = Observer()
        observer.schedule(event_handler, path=os.path.dirname(differ.file1_path), recursive=False)
        observer.schedule(event_handler, path=os.path.dirname(differ.file2_path), recursive=False)
        observer.start()
        
        # Display startup message
        start_message(host, port)
        
        try:
            # Run the application with minimal output
            app.logger.disabled = True
            quiet_socketio.run(app, host=host, port=port, debug=debug, log_output=False)
        finally:
            observer.stop()
            observer.join()
    except Exception as e:
        typer.echo(f"Error: {str(e)}", err=True)
        raise typer.Exit(1)

if __name__ == "__main__":
    cli()
