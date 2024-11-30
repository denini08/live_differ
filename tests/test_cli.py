import os
import pytest
import typer
from typer.testing import CliRunner
from live_differ.cli import cli, validate_files, start_message

runner = CliRunner()

def test_validate_files(tmp_path):
    # Create temporary test files
    file1 = tmp_path / "test1.txt"
    file2 = tmp_path / "test2.txt"
    file1.write_text("test content 1")
    file2.write_text("test content 2")
    
    # Test with valid files
    assert validate_files(str(file1), str(file2)) is True
    
    # Test with non-existent file
    with pytest.raises(typer.BadParameter):
        validate_files("nonexistent.txt", str(file2))
    
    # Test with non-readable file (if possible on the system)
    if os.name != 'nt':  # Skip on Windows
        file1.chmod(0)
        with pytest.raises(typer.BadParameter):
            validate_files(str(file1), str(file2))

def test_start_message(capsys):
    start_message("localhost", 5000)
    captured = capsys.readouterr()
    assert "Live Differ is running!" in captured.out
    assert "http://localhost:5000" in captured.out

def test_start_message_with_all_interfaces(capsys):
    start_message("0.0.0.0", 5000)
    captured = capsys.readouterr()
    assert "http://localhost:5000" in captured.out  # Should convert 0.0.0.0 to localhost

@pytest.mark.asyncio
async def test_cli_help():
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Run the Live Differ application to compare two files in real-time" in result.output
