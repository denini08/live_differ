"""
Tests for the CLI module.
"""
import os
import sys
import pytest
import typer
from datetime import datetime
from typer.testing import CliRunner
from unittest.mock import patch, Mock, MagicMock, ANY
from live_differ.cli import cli, validate_files, start_message, QuietSocketIO, run

def test_validate_files():
    with pytest.raises(typer.BadParameter, match="File not found"):
        validate_files("nonexistent1.txt", "file2.txt")
    
    with pytest.raises(typer.BadParameter, match="File not found"):
        validate_files("file1.txt", "nonexistent2.txt")
    
    with patch('os.path.isfile', return_value=True), \
         patch('os.access', return_value=False):
        with pytest.raises(typer.BadParameter, match="File not readable"):
            validate_files("unreadable1.txt", "file2.txt")
        with pytest.raises(typer.BadParameter, match="File not readable"):
            validate_files("file1.txt", "unreadable2.txt")
    
    with patch('os.path.isfile', return_value=True), \
         patch('os.access', return_value=True):
        assert validate_files("file1.txt", "file2.txt") is True

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
