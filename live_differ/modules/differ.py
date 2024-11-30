import os
import difflib
import logging
from datetime import datetime
from typing import Dict, List, Union

class DifferError(Exception):
    """Custom exception for differ-related errors"""
    pass

class FileDiffer:
    def __init__(self, file1_path: str, file2_path: str):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        
        self.logger.debug(f"Initializing FileDiffer with files: {file1_path}, {file2_path}")
        
        if not all([file1_path, file2_path]):
            raise DifferError("Both file paths must be provided")
            
        self.file1_path = os.path.abspath(file1_path)
        self.file2_path = os.path.abspath(file2_path)
        
        # Validate files exist and are readable
        for path in [self.file1_path, self.file2_path]:
            if not os.path.exists(path):
                self.logger.error(f"File not found: {path}")
                raise DifferError(f"File not found: {path}")
            if not os.access(path, os.R_OK):
                self.logger.error(f"File not readable: {path}")
                raise DifferError(f"File not readable: {path}")
        
        self.logger.debug("FileDiffer initialized successfully")
    
    def get_file_info(self, file_path: str) -> Dict[str, Union[str, int]]:
        """Get metadata about a file"""
        self.logger.debug(f"Getting file info for: {file_path}")
        try:
            stat = os.stat(file_path)
            info = {
                'path': file_path,
                'name': os.path.basename(file_path),
                'modified_time': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'size': stat.st_size
            }
            self.logger.debug(f"File info: {info}")
            return info
        except OSError as e:
            self.logger.error(f"Error getting file info for {file_path}: {str(e)}")
            raise DifferError(f"Failed to get file info: {str(e)}")
    
    def read_file(self, file_path: str) -> List[str]:
        """Read and return the lines of a file"""
        self.logger.debug(f"Reading file: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                self.logger.debug(f"Read {len(lines)} lines from {file_path}")
                return lines
        except UnicodeDecodeError:
            self.logger.error(f"File {file_path} is not UTF-8 encoded")
            raise DifferError(f"File {file_path} must be UTF-8 encoded")
        except IOError as e:
            self.logger.error(f"Error reading file {file_path}: {str(e)}")
            raise DifferError(f"Failed to read file: {str(e)}")

    def get_diff(self) -> Dict[str, Union[Dict, str]]:
        """Generate a diff between the two files"""
        self.logger.debug("Generating diff...")
        try:
            # Get file info first
            file1_info = self.get_file_info(self.file1_path)
            file2_info = self.get_file_info(self.file2_path)
            
            # Read files
            self.logger.debug("Reading files...")
            file1_lines = self.read_file(self.file1_path)
            file2_lines = self.read_file(self.file2_path)
            
            self.logger.debug("Creating diff table...")
            differ = difflib.HtmlDiff(tabsize=2, wrapcolumn=60)
            diff_table = differ.make_file(
                file1_lines, 
                file2_lines,
                fromdesc=os.path.basename(self.file1_path),
                todesc=os.path.basename(self.file2_path),
                context=True
            )
            
            # Clean up the HTML output
            diff_table = diff_table.replace('&nbsp;', ' ')  # Replace &nbsp; with regular spaces
            diff_table = diff_table.replace('<table class="diff"', '<table class="diff-table"')  # Add our custom class
            
            self.logger.debug("Diff generation complete")
            return {
                'file1_info': file1_info,
                'file2_info': file2_info,
                'diff_html': diff_table
            }
        except Exception as e:
            self.logger.exception(f"Error generating diff:")
            raise DifferError(f"Failed to generate diff: {str(e)}")
