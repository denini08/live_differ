#!/usr/bin/env python3
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template
from flask_socketio import SocketIO
from .modules.differ import FileDiffer

# Configure logging
def setup_logging():
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'app.log'),
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    
    logger = logging.getLogger()
    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)

# App configuration
class Config:
    def __init__(self):
        self.DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
        self.HOST = os.environ.get('FLASK_HOST', '127.0.0.1')
        self.PORT = int(os.environ.get('FLASK_PORT', '5000'))
        self.MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
        self.FILE1 = os.environ.get('FILE1')
        self.FILE2 = os.environ.get('FILE2')

app = Flask(__name__)
app.config.from_object(Config())
socketio = SocketIO(app)

@app.route('/')
def index():
    try:
        file1 = app.config.get('FILE1')
        file2 = app.config.get('FILE2')
        if not file1 or not file2:
            return render_template('error.html', error="File paths not configured"), 400
            
        differ = FileDiffer(file1, file2)
        diff_data = differ.get_diff()
        return render_template('index.html', diff_data=diff_data)
    except Exception as e:
        app.logger.error(f"Error in index route: {str(e)}")
        return render_template('error.html', error=str(e)), 500

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"Server Error: {error}")
    return render_template('error.html', error="Internal server error"), 500
