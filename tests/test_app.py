import os
import pytest
from unittest.mock import patch, Mock
from live_differ.core import app, setup_logging, Config

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_config_defaults():
    config = Config()
    assert config.DEBUG is False
    assert config.HOST == '127.0.0.1'
    assert config.PORT == 5000
    assert config.MAX_CONTENT_LENGTH == 16 * 1024 * 1024
    assert config.FILE1 is None
    assert config.FILE2 is None

def test_config_from_env():
    with patch.dict('os.environ', {
        'FLASK_DEBUG': 'true',
        'FLASK_HOST': 'localhost',
        'FLASK_PORT': '8000',
        'FILE1': '/path/to/file1',
        'FILE2': '/path/to/file2'
    }):
        config = Config()
        assert config.DEBUG == True
        assert config.HOST == 'localhost'
        assert config.PORT == 8000
        assert config.FILE1 == '/path/to/file1'
        assert config.FILE2 == '/path/to/file2'

def test_setup_logging(tmp_path):
    log_dir = tmp_path / "logs"
    with patch('os.path.exists', return_value=False) as mock_exists, \
         patch('os.makedirs') as mock_makedirs, \
         patch('logging.getLogger') as mock_get_logger, \
         patch('logging.handlers.RotatingFileHandler') as mock_handler, \
         patch('logging.Formatter') as mock_formatter:
        
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_handler_instance = Mock()
        mock_handler.return_value = mock_handler_instance
        
        setup_logging()
        
        mock_exists.assert_called_once_with('logs')
        mock_makedirs.assert_called_once_with('logs')
        mock_formatter.assert_called_once()
        mock_handler.assert_called_once()
        mock_handler_instance.setFormatter.assert_called_once()
        assert mock_logger.addHandler.called
        assert mock_logger.setLevel.called

def test_index_route_no_files(client):
    response = client.get('/')
    assert response.status_code == 400
    assert b"File paths not configured" in response.data

def test_index_route_with_files(client, tmp_path):
    file1 = tmp_path / "file1.txt"
    file2 = tmp_path / "file2.txt"
    file1.write_text("test content 1")
    file2.write_text("test content 2")
    
    app.config['FILE1'] = str(file1)
    app.config['FILE2'] = str(file2)
    
    response = client.get('/')
    assert response.status_code == 200

def test_not_found_error(client):
    response = client.get('/nonexistent')
    assert response.status_code == 404

def test_internal_error():
    with app.test_client() as client:
        with patch('live_differ.core.render_template', side_effect=Exception('Test error')):
            response = client.get('/')
            assert response.status_code == 500
