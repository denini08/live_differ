#!/usr/bin/env python3
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, request, jsonify, Response
from flask_socketio import SocketIO
from flask_cors import CORS
from .modules.differ import FileDiffer

# Configure logging
def setup_logging(debug=False):
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Set up file handler
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'app.log'),
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)  # Always log debug to file
    
    # Set up console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)  # Always show debug in console
    
    # Configure root logger
    logger = logging.getLogger()
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.setLevel(logging.DEBUG)
    
    # Configure Flask and Werkzeug loggers
    logging.getLogger('werkzeug').setLevel(logging.DEBUG)
    logging.getLogger('engineio').setLevel(logging.DEBUG)
    logging.getLogger('socketio').setLevel(logging.DEBUG)

# Get the package's root directory
package_dir = os.path.dirname(os.path.abspath(__file__))

# Initialize Flask app with correct template and static paths
template_dir = os.path.join(package_dir, 'templates')
static_dir = os.path.join(package_dir, 'static')

app = Flask(__name__,
           template_folder=template_dir,
           static_folder=static_dir,
           static_url_path='/static')  # Explicit static URL path

# Basic app configuration
app.config.update(
    DEBUG=True,
    TESTING=True,
    TEMPLATES_AUTO_RELOAD=True,
    SEND_FILE_MAX_AGE_DEFAULT=0,
    SECRET_KEY=os.urandom(24),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=False,
    MAX_CONTENT_LENGTH=16 * 1024 * 1024
)

# Log template and static directories
app.logger.debug(f"Template directory: {template_dir}")
app.logger.debug(f"Static directory: {static_dir}")
app.logger.debug(f"Template directory exists: {os.path.exists(template_dir)}")
app.logger.debug(f"Static directory exists: {os.path.exists(static_dir)}")

if os.path.exists(template_dir):
    app.logger.debug(f"Template files: {os.listdir(template_dir)}")
if os.path.exists(static_dir):
    app.logger.debug(f"Static files: {os.listdir(static_dir)}")

# Security and CORS settings
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize SocketIO with debugging
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    logger=True,
    engineio_logger=True,
    debug=True
)

@app.before_request
def log_request_info():
    """Log details about each request."""
    app.logger.debug("=" * 50)
    app.logger.debug("Incoming request:")
    app.logger.debug(f"Method: {request.method}")
    app.logger.debug(f"URL: {request.url}")
    app.logger.debug(f"Headers: {dict(request.headers)}")
    app.logger.debug("=" * 50)

@app.after_request
def after_request(response):
    """Log response info."""
    app.logger.debug("=" * 50)
    app.logger.debug("Outgoing response:")
    app.logger.debug(f"Status: {response.status}")
    app.logger.debug(f"Headers: {dict(response.headers)}")
    app.logger.debug("=" * 50)
    return response

@app.route('/')
def index():
    """Render the index page with file comparison."""
    try:
        app.logger.debug("Index route accessed")
        
        # Get file paths
        file1 = app.config.get('FILE1')
        file2 = app.config.get('FILE2')
        
        app.logger.debug(f"File1: {file1}")
        app.logger.debug(f"File2: {file2}")
        
        if not file1 or not file2:
            error_msg = "File paths not configured"
            app.logger.error(error_msg)
            return render_template('error.html', error=error_msg), 400
        
        # Initialize differ and get diff
        try:
            differ = FileDiffer(file1, file2)
            diff_data = differ.get_diff()
            app.logger.debug("Diff generated successfully")
            app.logger.debug(f"File1 info: {diff_data['file1_info']}")
            app.logger.debug(f"File2 info: {diff_data['file2_info']}")
            app.logger.debug("Diff HTML length: %d", len(diff_data['diff_html']))
            
            # For large diffs, we'll stream the response
            if len(diff_data['diff_html']) > 1_000_000:  # If diff is larger than 1MB
                app.logger.debug("Large diff detected, streaming response")
                def generate():
                    # Yield the template header
                    yield render_template('index_header.html', diff_data=diff_data)
                    # Yield the diff content div start
                    yield '<div class="diff-content" id="diff-view">'
                    # Yield the diff in chunks
                    chunk_size = 100_000  # 100KB chunks
                    diff_html = diff_data['diff_html']
                    for i in range(0, len(diff_html), chunk_size):
                        yield diff_html[i:i + chunk_size]
                    # Yield the diff content div end and footer
                    yield '</div>'
                    yield render_template('index_footer.html')
                
                return app.response_class(generate(), mimetype='text/html')
            
            # For smaller diffs, render normally
            app.logger.debug("Rendering template...")
            response = render_template('index.html', diff_data=diff_data)
            app.logger.debug("Template rendered successfully")
            return response
            
        except Exception as e:
            app.logger.exception("Error in differ:")
            return render_template('error.html', error=f"Error comparing files: {str(e)}"), 500
            
    except Exception as e:
        app.logger.exception(f"Unexpected error in index route:")
        return render_template('error.html', error=str(e)), 500

@app.route('/health')
def health_check():
    """Simple health check endpoint."""
    return jsonify({"status": "ok"})

@app.errorhandler(404)
def not_found_error(error):
    app.logger.error(f"404 error: {error}")
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.exception(f"500 error: {error}")
    return render_template('error.html', error="Internal server error"), 500

# Initialize logging
setup_logging(debug=True)
