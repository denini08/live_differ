import os
import pytest
from datetime import datetime
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
    assert differ.file1_path == os.path.abspath(file1)
    assert differ.file2_path == os.path.abspath(file2)

def test_differ_initialization_errors():
    with pytest.raises(DifferError, match="Both file paths must be provided"):
        FileDiffer("", "")
    
    with pytest.raises(DifferError, match="File not found"):
        FileDiffer("nonexistent1.txt", "nonexistent2.txt")

def test_get_file_info(temp_files):
    file1, _ = temp_files
    differ = FileDiffer(file1, file1)  # Using same file for simplicity
    info = differ.get_file_info(file1)
    
    assert isinstance(info, dict)
    assert 'path' in info
    assert 'name' in info
    assert 'modified_time' in info
    assert 'size' in info
    assert info['name'] == os.path.basename(file1)

def test_read_file(temp_files):
    file1, _ = temp_files
    differ = FileDiffer(file1, file1)
    lines = differ.read_file(file1)
    assert lines == ["Line 1\n", "Line 2\n", "Line 3\n"]

def test_read_file_errors(tmp_path):
    # Test with non-UTF8 file
    binary_file = tmp_path / "binary.bin"
    binary_file.write_bytes(bytes([0xFF, 0xFE, 0xFD]))
    
    differ = FileDiffer(str(binary_file), str(binary_file))
    with pytest.raises(DifferError, match="must be UTF-8 encoded"):
        differ.read_file(str(binary_file))

def test_compare_files(temp_files):
    file1, file2 = temp_files
    differ = FileDiffer(file1, file2)
    diff = differ.get_diff()
    
    assert isinstance(diff, dict)
    assert 'diff_html' in diff
    assert 'file1_info' in diff
    assert 'file2_info' in diff
    
    # Verify file info
    assert diff['file1_info']['name'] == 'file1.txt'
    assert diff['file2_info']['name'] == 'file2.txt'
    
    # Verify diff contains expected changes in HTML format
    diff_html = diff['diff_html']
    assert '<span class="diff_add">Line&nbsp;2&nbsp;modified</span>' in diff_html
    assert '<span class="diff_add">Line&nbsp;4</span>' in diff_html
