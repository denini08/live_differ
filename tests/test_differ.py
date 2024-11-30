"""
Tests for the differ module.
"""
import os
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
from live_differ.modules.differ import FileDiffer, DifferError

@pytest.fixture
def temp_files(tmp_path):
    file1 = tmp_path / "file1.txt"
    file2 = tmp_path / "file2.txt"
    file1.write_text("Line 1\nLine 2\nLine 3\n")
    file2.write_text("Line 1\nLine 2 modified\nLine 3\nLine 4\n")
    return str(file1), str(file2)

def test_differ_initialization():
    with patch('os.path.exists', return_value=True), \
         patch('os.access', return_value=True), \
         patch('os.path.abspath', side_effect=lambda x: x):
        differ = FileDiffer("file1.txt", "file2.txt")
        assert differ.file1_path == "file1.txt"
        assert differ.file2_path == "file2.txt"

def test_differ_initialization_errors():
    # Test missing files
    with pytest.raises(DifferError, match="Both file paths must be provided"):
        FileDiffer("", "file2.txt")
    
    with pytest.raises(DifferError, match="Both file paths must be provided"):
        FileDiffer("file1.txt", "")
    
    # Test non-existent files
    with patch('os.path.exists', return_value=False), \
         patch('os.path.abspath', side_effect=lambda x: x):
        with pytest.raises(DifferError, match="File not found"):
            FileDiffer("nonexistent1.txt", "file2.txt")
    
    # Test unreadable files
    with patch('os.path.exists', return_value=True), \
         patch('os.access', return_value=False), \
         patch('os.path.abspath', side_effect=lambda x: x):
        with pytest.raises(DifferError, match="File not readable"):
            FileDiffer("unreadable1.txt", "file2.txt")

def test_get_file_info():
    mock_stat = MagicMock()
    mock_stat.st_mtime = datetime.now().timestamp()
    mock_stat.st_size = 1234
    
    with patch('os.path.exists', return_value=True), \
         patch('os.access', return_value=True), \
         patch('os.path.abspath', side_effect=lambda x: x), \
         patch('os.stat', return_value=mock_stat):
        
        differ = FileDiffer("file1.txt", "file2.txt")
        info = differ.get_file_info("file1.txt")
        
        assert info['path'] == "file1.txt"
        assert info['name'] == "file1.txt"
        assert isinstance(info['modified_time'], str)
        assert info['size'] == 1234

def test_get_file_info_error():
    with patch('os.path.exists', return_value=True), \
         patch('os.access', return_value=True), \
         patch('os.path.abspath', side_effect=lambda x: x), \
         patch('os.stat', side_effect=OSError("Test error")):
        
        differ = FileDiffer("file1.txt", "file2.txt")
        with pytest.raises(DifferError, match="Failed to get file info"):
            differ.get_file_info("file1.txt")

def test_read_file():
    mock_content = ["Line 1\n", "Line 2\n"]
    mock_file = MagicMock()
    mock_file.__enter__.return_value = mock_file
    mock_file.__exit__.return_value = None
    mock_file.readlines.return_value = mock_content
    
    with patch('os.path.exists', return_value=True), \
         patch('os.access', return_value=True), \
         patch('os.path.abspath', side_effect=lambda x: x), \
         patch('builtins.open', return_value=mock_file):
        
        differ = FileDiffer("file1.txt", "file2.txt")
        lines = differ.read_file("file1.txt")
        assert lines == mock_content

def test_read_file_errors():
    with patch('os.path.exists', return_value=True), \
         patch('os.access', return_value=True), \
         patch('os.path.abspath', side_effect=lambda x: x):
        differ = FileDiffer("file1.txt", "file2.txt")
        
        # Test UnicodeDecodeError
        mock_file = MagicMock()
        mock_file.__enter__.return_value = mock_file
        mock_file.__exit__.return_value = None
        mock_file.readlines.side_effect = UnicodeDecodeError('utf-8', b'', 0, 1, 'Test error')
        with patch('builtins.open', return_value=mock_file):
            with pytest.raises(DifferError, match="must be UTF-8 encoded"):
                differ.read_file("file1.txt")
        
        # Test IOError
        mock_file = MagicMock()
        mock_file.__enter__.return_value = mock_file
        mock_file.__exit__.return_value = None
        mock_file.readlines.side_effect = IOError("Test error")
        with patch('builtins.open', return_value=mock_file):
            with pytest.raises(DifferError, match="Failed to read file"):
                differ.read_file("file1.txt")

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

def test_get_diff_error():
    with patch('os.path.exists', return_value=True), \
         patch('os.access', return_value=True), \
         patch('os.path.abspath', side_effect=lambda x: x), \
         patch('live_differ.modules.differ.FileDiffer.read_file', side_effect=Exception("Test error")):
        
        differ = FileDiffer("file1.txt", "file2.txt")
        with pytest.raises(DifferError, match="Failed to generate diff"):
            differ.get_diff()
