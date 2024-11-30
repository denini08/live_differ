#!/usr/bin/env python3
import os
import typer
from app import app, socketio, setup_logging
from modules.differ import FileDiffer

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
    
    # Run the application
    socketio.run(app, host=host, port=port, debug=debug)

if __name__ == "__main__":
    cli()
