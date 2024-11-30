#!/usr/bin/env python3
import os
import sys
import typer
import logging
from flask_socketio import SocketIO
from watchdog.observers import Observer
from .core import app, setup_logging
from .modules.differ import FileDiffer
from .modules.watcher import FileChangeHandler

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
    import socket
    
    # Test if we can bind to the port
    test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        test_socket.bind((host, port))
        test_socket.close()
        port_available = True
    except OSError:
        port_available = False
        typer.echo(f"\nWarning: Port {port} might already be in use!", err=True)
    
    protocol = "http"
    url = f"{protocol}://localhost:{port}"
    
    typer.echo(f"\nStarting Live Differ...")
    typer.echo(f"Host: {host}")
    typer.echo(f"Port: {port}")
    typer.echo(f"Debug mode: enabled")
    if port_available:
        typer.echo(f"Server should be available at: {url}")
    if host == "0.0.0.0":
        typer.echo("Server is accessible from any network interface")
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
        help="Host to bind the server to (use 0.0.0.0 for external access)",
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
        True,  # Always enable debug for now
        "--debug",
        help="Enable debug mode",
        envvar="FLASK_DEBUG"
    )
):
    """
    Run the Live Differ application to compare two files in real-time.
    """
    import logging
    
    # Set up basic logging immediately
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    
    try:
        logger.debug("Starting Live Differ application...")
        logger.debug(f"Host: {host}")
        logger.debug(f"Port: {port}")
        logger.debug(f"Debug mode: {debug}")
        
        # Convert to absolute paths
        file1_abs = os.path.abspath(file1)
        file2_abs = os.path.abspath(file2)
        
        logger.debug(f"File 1: {file1_abs}")
        logger.debug(f"File 2: {file2_abs}")
        
        # Validate files exist
        if not os.path.exists(file1_abs):
            raise typer.BadParameter(f"File not found: {file1}")
        if not os.path.exists(file2_abs):
            raise typer.BadParameter(f"File not found: {file2}")
        
        # Store file paths in app config
        app.config['FILE1'] = file1_abs
        app.config['FILE2'] = file2_abs
        app.config['DEBUG'] = True
        
        # Initialize differ to validate files are readable
        logger.debug("Initializing differ...")
        differ = FileDiffer(app.config['FILE1'], app.config['FILE2'])
        
        # Create quiet version of SocketIO
        logger.debug("Setting up SocketIO...")
        quiet_socketio = QuietSocketIO(app)
        
        # Set up file watching
        logger.debug("Setting up file watchers...")
        event_handler = FileChangeHandler(differ, quiet_socketio)
        observer = Observer()
        observer.schedule(event_handler, path=os.path.dirname(differ.file1_path), recursive=False)
        observer.schedule(event_handler, path=os.path.dirname(differ.file2_path), recursive=False)
        observer.start()
        
        # Display startup message
        start_message(host, port)
        
        try:
            logger.debug("Starting Flask application...")
            # Run the application
            quiet_socketio.run(
                app,
                host=host,
                port=port,
                debug=True,  # Always enable debug
                use_reloader=False,  # Disable reloader
                allow_unsafe_werkzeug=True
            )
        except OSError as e:
            if "Address already in use" in str(e):
                logger.error(f"Port {port} is already in use!")
                typer.echo(f"Error: Port {port} is already in use. Try a different port with --port option.", err=True)
            else:
                logger.error(f"Error starting server: {e}", exc_info=True)
                typer.echo(f"Error starting server: {str(e)}", err=True)
            raise typer.Exit(code=1)
        except Exception as e:
            logger.error(f"Unexpected error while running server: {e}", exc_info=True)
            typer.echo(f"Unexpected error: {str(e)}", err=True)
            raise typer.Exit(code=1)
        finally:
            logger.debug("Shutting down file watchers...")
            observer.stop()
            observer.join()
            
    except Exception as e:
        logger.error(f"Error in run command: {e}", exc_info=True)
        typer.echo(f"Error: {str(e)}", err=True)
        raise typer.Exit(code=1)

if __name__ == "__main__":
    cli()
