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
        
        if not all([file1_path, file2_path]):
            raise DifferError("Both file paths must be provided")
            
        self.file1_path = os.path.abspath(file1_path)
        self.file2_path = os.path.abspath(file2_path)
        
        # Validate files exist and are readable
        for path in [self.file1_path, self.file2_path]:
            if not os.path.exists(path):
                raise DifferError(f"File not found: {path}")
            if not os.access(path, os.R_OK):
                raise DifferError(f"File not readable: {path}")
        
    def get_file_info(self, file_path: str) -> Dict[str, Union[str, int]]:
        """Get metadata about a file"""
        try:
            stat = os.stat(file_path)
            return {
                'path': file_path,
                'name': os.path.basename(file_path),
                'modified_time': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'size': stat.st_size
            }
        except OSError as e:
            self.logger.error(f"Error getting file info for {file_path}: {str(e)}")
            raise DifferError(f"Failed to get file info: {str(e)}")
    
    def read_file(self, file_path: str) -> List[str]:
        """Read and return the lines of a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.readlines()
        except UnicodeDecodeError:
            self.logger.error(f"File {file_path} is not UTF-8 encoded")
            raise DifferError(f"File {file_path} must be UTF-8 encoded")
        except IOError as e:
            self.logger.error(f"Error reading file {file_path}: {str(e)}")
            raise DifferError(f"Failed to read file: {str(e)}")

    def get_diff(self) -> Dict[str, Union[Dict, str]]:
        """Generate a diff between the two files"""
        try:
            file1_lines = self.read_file(self.file1_path)
            file2_lines = self.read_file(self.file2_path)
            
            differ = difflib.HtmlDiff()
            diff_table = differ.make_file(
                file1_lines, 
                file2_lines,
                fromdesc=os.path.basename(self.file1_path),
                todesc=os.path.basename(self.file2_path),
                context=True
            )
            
            return {
                'file1_info': self.get_file_info(self.file1_path),
                'file2_info': self.get_file_info(self.file2_path),
                'diff_html': diff_table
            }
        except Exception as e:
            self.logger.error(f"Error generating diff: {str(e)}")
            raise DifferError(f"Failed to generate diff: {str(e)}")
