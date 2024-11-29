#!/usr/bin/env python3
import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
from watchdog.observers import Observer
from modules.differ import FileDiffer
from modules.watcher import FileChangeHandler

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
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    HOST = os.environ.get('FLASK_HOST', '127.0.0.1')
    PORT = int(os.environ.get('FLASK_PORT', 5000))
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app = Flask(__name__)
app.config.from_object(Config)
socketio = SocketIO(app)

@app.route('/')
def index():
    try:
        if len(sys.argv) != 3:
            return render_template('error.html', error="Please provide two files to compare"), 400
            
        differ = FileDiffer(sys.argv[1], sys.argv[2])
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

def main():
    setup_logging()
    app.logger.info("Starting Live Differ application")
    
    if len(sys.argv) != 3:
        app.logger.error("Invalid number of arguments")
        print("Usage: python app.py file1_path file2_path")
        sys.exit(1)

    try:
        differ = FileDiffer(sys.argv[1], sys.argv[2])
        
        # Set up file watching
        event_handler = FileChangeHandler(differ, socketio)
        observer = Observer()
        observer.schedule(event_handler, path=os.path.dirname(differ.file1_path), recursive=False)
        observer.schedule(event_handler, path=os.path.dirname(differ.file2_path), recursive=False)
        observer.start()

        app.logger.info(f"Starting server on {Config.HOST}:{Config.PORT}")
        socketio.run(app, 
                    host=Config.HOST,
                    port=Config.PORT,
                    debug=Config.DEBUG)
    except Exception as e:
        app.logger.error(f"Application error: {str(e)}")
        raise
    finally:
        observer.stop()
        observer.join()

if __name__ == '__main__':
    main()
