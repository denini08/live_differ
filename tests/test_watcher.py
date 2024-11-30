import os
import time
import pytest
from unittest.mock import Mock, patch
from watchdog.events import FileModifiedEvent
from live_differ.modules.watcher import FileChangeHandler

@pytest.fixture
def mock_differ():
    differ = Mock()
    differ.file1_path = "/path/to/file1.txt"
    differ.file2_path = "/path/to/file2.txt"
    differ.get_diff.return_value = {"diff": "test diff"}
    return differ

@pytest.fixture
def mock_socket():
    socket = Mock()
    return socket

def test_file_change_handler_initialization(mock_differ, mock_socket):
    handler = FileChangeHandler(mock_differ, mock_socket)
    assert handler.differ == mock_differ
    assert handler.socket == mock_socket
    assert handler.last_modified == 0

def test_on_modified_ignores_directories(mock_differ, mock_socket):
    handler = FileChangeHandler(mock_differ, mock_socket)
    event = FileModifiedEvent("/path/to/dir")
    event.is_directory = True
    
    handler.on_modified(event)
    mock_differ.get_diff.assert_not_called()
    mock_socket.emit.assert_not_called()

def test_on_modified_handles_watched_files(mock_differ, mock_socket):
    handler = FileChangeHandler(mock_differ, mock_socket)
    event = FileModifiedEvent(mock_differ.file1_path)
    event.is_directory = False
    
    handler.on_modified(event)
    mock_differ.get_diff.assert_called_once()
    mock_socket.emit.assert_called_once_with('update_diff', {"diff": "test diff"}, namespace='/')

def test_on_modified_debounce(mock_differ, mock_socket):
    handler = FileChangeHandler(mock_differ, mock_socket)
    event = FileModifiedEvent(mock_differ.file1_path)
    event.is_directory = False
    
    # First call
    handler.on_modified(event)
    assert mock_differ.get_diff.call_count == 1
    
    # Second call immediately after
    handler.on_modified(event)
    # Should still be 1 due to debounce
    assert mock_differ.get_diff.call_count == 1
    
    # Wait for debounce period and try again
    time.sleep(0.4)  # Debounce is 0.3s
    handler.on_modified(event)
    assert mock_differ.get_diff.call_count == 2

def test_on_modified_ignores_unrelated_files(mock_differ, mock_socket):
    handler = FileChangeHandler(mock_differ, mock_socket)
    event = FileModifiedEvent("/unrelated/file.txt")
    event.is_directory = False
    
    handler.on_modified(event)
    mock_differ.get_diff.assert_not_called()
    mock_socket.emit.assert_not_called()
