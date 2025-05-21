"""
Tests for the differ module.
"""
import os
import pytest
import re
from datetime import datetime
from unittest.mock import patch, MagicMock, mock_open
from live_differ.modules.differ import FileDiffer, DifferError

@pytest.fixture
def temp_files(tmp_path):
    file1 = tmp_path / "file1.txt"
    file2 = tmp_path / "file2.txt"
    file1.write_text("Line 1\nLine 2\nLine 3\n")
    file2.write_text("Line 1\nLine 2 modified\nLine 3\nLine 4\n")
    return str(file1), str(file2)

def test_differ_initialization(temp_files):
    file1, file2 = temp_files
    differ = FileDiffer(file1, file2)
    assert differ.file1_path == file1
    assert differ.file2_path == file2

def test_differ_initialization_errors(temp_files):
    file1, file2 = temp_files

    # Test missing files
    with pytest.raises(DifferError, match="Both file paths must be provided"):
        FileDiffer("", file2)
    
    with pytest.raises(DifferError, match="Both file paths must be provided"):
        FileDiffer(file1, "")

    # Test non-existent files
    with pytest.raises(DifferError, match=re.escape(f"File not found: {os.path.abspath('nonexistent1.txt')}")):
        FileDiffer("nonexistent1.txt", file2)
    
    with pytest.raises(DifferError, match=re.escape(f"File not found: {os.path.abspath('nonexistent2.txt')}")):
        FileDiffer(file1, "nonexistent2.txt")

    # Test unreadable files
    with patch("builtins.open", side_effect=PermissionError("Permission denied")):
        with pytest.raises(DifferError, match=re.escape(f"File not readable: {os.path.abspath('unreadable1.txt')}")):
            FileDiffer("unreadable1.txt", file2)
    
    with patch("builtins.open", side_effect=[mock_open(read_data="").return_value, PermissionError("Permission denied")]):
        with pytest.raises(DifferError, match=re.escape(f"File not readable: {os.path.abspath('unreadable2.txt')}")):
            FileDiffer(file1, "unreadable2.txt")

    # Test generic IOError on first file
    with patch("builtins.open", side_effect=IOError("Disk full")):
        with pytest.raises(DifferError, match=re.escape(f"Error accessing file {os.path.abspath('file1.txt')}: Disk full")):
            FileDiffer("file1.txt", file2)

    # Test generic IOError on second file
    with patch("builtins.open", side_effect=[mock_open(read_data="").return_value, IOError("Disk full")]):
        with pytest.raises(DifferError, match=re.escape(f"Error accessing file {os.path.abspath('file2.txt')}: Disk full")):
            FileDiffer(file1, "file2.txt")

    # Test symbolic links (placeholder, passes if no link check)
    with patch("builtins.open", mock_open(read_data="")), \
         patch("os.path.islink", return_value=True):
        differ = FileDiffer(file1, file2)
        assert differ.file1_path == file1
        assert differ.file2_path == file2

def test_get_file_info(temp_files):
    file1, file2 = temp_files
    differ = FileDiffer(file1, file2)
    info = differ.get_file_info(file1)
    
    assert info['path'] == file1
    assert info['name'] == "file1.txt"
    assert isinstance(info['modified_time'], str)
    assert isinstance(info['size'], int)

def test_get_file_info_error(temp_files):
    file1, file2 = temp_files
    with patch("os.stat", side_effect=OSError("Test error")):
        differ = FileDiffer(file1, file2)
        with pytest.raises(DifferError, match="Failed to get file info"):
            differ.get_file_info(file1)

def test_read_file(temp_files):
    file1, file2 = temp_files
    differ = FileDiffer(file1, file2)
    lines = differ.read_file(file1)
    assert lines == ["Line 1\n", "Line 2\n", "Line 3\n"]

def test_read_file_errors(temp_files):
    file1, file2 = temp_files
    differ = FileDiffer(file1, file2)
    
    # Test UnicodeDecodeError
    with patch("builtins.open", side_effect=UnicodeDecodeError("utf-8", b"", 0, 1, "Test error")):
        with pytest.raises(DifferError, match="must be UTF-8 encoded"):
            differ.read_file(file1)
    
    # Test IOError
    with patch("builtins.open", side_effect=IOError("Test error")):
        with pytest.raises(DifferError, match="Failed to read file"):
            differ.read_file(file1)

def test_compare_files(temp_files):
    file1, file2 = temp_files
    differ = FileDiffer(file1, file2)
    diff = differ.get_diff()
    
    assert isinstance(diff, dict)
    assert "diff_html" in diff
    assert "file1_info" in diff
    assert "file2_info" in diff
    assert diff["file1_info"]["name"] == "file1.txt"
    assert diff["file2_info"]["name"] == "file2.txt"
    # Check for changed line (Line 2 modified) and added line (Line 4)
    assert re.search(r'<td[^>]*><span class="diff_add">Line\s*2\s*modified</span></td>', diff["diff_html"], re.IGNORECASE)
    assert re.search(r'<td[^>]*><span class="diff_add">Line\s*4</span></td>', diff["diff_html"], re.IGNORECASE)

def test_get_diff_error(temp_files):
    file1, file2 = temp_files
    with patch("live_differ.modules.differ.FileDiffer.read_file", side_effect=Exception("Test error")):
        differ = FileDiffer(file1, file2)
        with pytest.raises(DifferError, match="Failed to generate diff"):
            differ.get_diff()

def test_differ_debug_logging(temp_files):
    file1, file2 = temp_files
    with patch("logging.Logger.debug") as mock_logger:
        differ = FileDiffer(file1, file2, debug=True)
        mock_logger.assert_called_with("FileDiffer initialized successfully")

def test_differ_large_file(tmp_path):
    large_file = tmp_path / "large.txt"
    with large_file.open("w") as f:
        f.write("A" * 1024 * 1024)  # 1MB file
    second_file = tmp_path / "file2.txt"
    second_file.write_text("Line 1\n")
    
    differ = FileDiffer(str(large_file), str(second_file))
    info = differ.get_file_info(str(large_file))
    assert info["size"] == 1024 * 1024

def test_differ_empty_file(tmp_path):
    empty_file = tmp_path / "empty.txt"
    empty_file.write_text("")
    second_file = tmp_path / "file2.txt"
    second_file.write_text("Line 1\n")
    
    differ = FileDiffer(str(empty_file), str(second_file))
    lines = differ.read_file(str(empty_file))
    assert lines == []