"""
Tests for the CLI module.
"""
import os
import sys
import pytest
import typer
from datetime import datetime
from typer.testing import CliRunner
from unittest.mock import patch, Mock, MagicMock, mock_open, ANY
from live_differ.cli import cli, validate_files, start_message, QuietSocketIO, run


# fixture to set up and tear down test files
@pytest.fixture
def setup_files(tmp_path):
    """Create temporary files for testing and clean them up afterward."""
    file1 = tmp_path / "file1.txt"
    file2 = tmp_path / "file2.txt"
    
    file1.write_text("test content 1")
    file2.write_text("test content 2")
    
    yield str(file1), str(file2)
    

def test_validate_files(setup_files):
    file1, file2 = setup_files  # get paths to temporary files

    # First file does not exist
    with pytest.raises(typer.BadParameter, match="File not found: nonexistent1.txt"):
        validate_files("nonexistent1.txt", file2)

    # Second file does not exist
    with pytest.raises(typer.BadParameter, match="File not found: nonexistent2.txt"):
        validate_files(file1, "nonexistent2.txt")

    # First file is not readable (PermissionError)
    with patch("builtins.open", side_effect=PermissionError("Permission denied")):
        with pytest.raises(typer.BadParameter, match="File not readable: unreadable1.txt"):
            validate_files("unreadable1.txt", file2)

    # Second file is not readable (PermissionError)
    with patch("builtins.open", side_effect=[mock_open(read_data="").return_value, PermissionError("Permission denied")]):
        with pytest.raises(typer.BadParameter, match="File not readable: unreadable2.txt"):
            validate_files(file1, "unreadable2.txt")

    # Both files are valid and readable
    assert validate_files(file1, file2) is True

    # Generic IOError on first file
    with patch("builtins.open", side_effect=IOError("Disk full")):
        with pytest.raises(typer.BadParameter, match="Error accessing file file1.txt: Disk full"):
            validate_files("file1.txt", file2)

    # Generic IOError on second file
    with patch("builtins.open", side_effect=[mock_open(read_data="").return_value, IOError("Disk full")]):
        with pytest.raises(typer.BadParameter, match="Error accessing file file2.txt: Disk full"):
            validate_files(file1, "file2.txt")


def test_start_message():
    with patch('typer.echo') as mock_echo:
        start_message("127.0.0.1", 5000)
        assert mock_echo.call_count == 3
        mock_echo.assert_any_call("\nLive Differ is running!")
        mock_echo.assert_any_call("View the diff at: http://127.0.0.1:5000")
        mock_echo.assert_any_call("\nPress Ctrl+C to quit.")

def test_start_message_with_all_interfaces():
    with patch('typer.echo') as mock_echo:
        start_message("0.0.0.0", 5000)
        mock_echo.assert_any_call("View the diff at: http://localhost:5000")

def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Run the Live Differ application" in result.stdout

def test_quiet_socketio():
    app = MagicMock()
    app.extensions = {}
    socketio = QuietSocketIO(app)
    
    with patch('flask.cli.show_server_banner') as mock_banner:
        with patch.object(socketio, 'server') as mock_server:
            mock_server.eio.async_mode = 'threading'
            socketio.run(app, allow_unsafe_werkzeug=True)
            mock_banner.assert_not_called()
