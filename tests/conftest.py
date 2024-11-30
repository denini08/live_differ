import os
import pytest
from pathlib import Path

@pytest.fixture
def sample_files(tmp_path):
    """Create sample files for testing."""
    file1 = tmp_path / "file1.txt"
    file2 = tmp_path / "file2.txt"
    
    file1.write_text("Line 1\nLine 2\nLine 3\n")
    file2.write_text("Line 1\nLine 2 modified\nLine 3\nLine 4\n")
    
    return str(file1), str(file2)

@pytest.fixture
def temp_log_dir(tmp_path):
    """Create a temporary log directory."""
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    return log_dir
