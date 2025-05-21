import os
import difflib
import logging
import re
from datetime import datetime
from typing import Dict, List, Union

class DifferError(Exception):
    """Custom exception for differ-related errors"""
    pass

class FileDiffer:
    def __init__(self, file1_path: str, file2_path: str, debug: bool = False):
        self.logger = logging.getLogger(__name__)
        self.debug = debug
        
        if self.debug:
            self.logger.debug(f"Initializing FileDiffer with files: {file1_path}, {file2_path}")
        
        if not all([file1_path, file2_path]):
            raise DifferError("Both file paths must be provided")
            
        self.file1_path = os.path.abspath(file1_path)
        self.file2_path = os.path.abspath(file2_path)
        
        # Validate files exist and are readable
        for path in [self.file1_path, self.file2_path]:
            try:
                with open(path, 'r') as f:
                    pass  # attempt to open the file to verify existence and readability
            except FileNotFoundError:
                self.logger.error(f"File not found: {path}")
                raise DifferError(f"File not found: {path}")
            except PermissionError:
                self.logger.error(f"File not readable: {path}")
                raise DifferError(f"File not readable: {path}")
            except IOError as e:
                self.logger.error(f"Error accessing file {path}: {str(e)}")
                raise DifferError(f"Error accessing file {path}: {str(e)}")
        
        if self.debug:
            self.logger.debug("FileDiffer initialized successfully")
    
    def get_file_info(self, file_path: str) -> Dict[str, Union[str, int]]:
        """Get metadata about a file"""
        if self.debug:
            self.logger.debug(f"Getting file info for: {file_path}")
        try:
            stat = os.stat(file_path)
            info = {
                'path': file_path,
                'name': os.path.basename(file_path),
                'modified_time': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'size': stat.st_size
            }
            if self.debug:
                self.logger.debug(f"File info: {info}")
            return info
        except OSError as e:
            self.logger.error(f"Error getting file info for {file_path}: {str(e)}")
            raise DifferError(f"Failed to get file info: {str(e)}")
    
    def read_file(self, file_path: str) -> List[str]:
        """Read and return the lines of a file"""
        if self.debug:
            self.logger.debug(f"Reading file: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if self.debug:
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
        if self.debug:
            self.logger.debug("Generating diff...")
        try:
            # Get file info first
            file1_info = self.get_file_info(self.file1_path)
            file2_info = self.get_file_info(self.file2_path)
            
            # Read files
            if self.debug:
                self.logger.debug("Reading files...")
            file1_lines = self.read_file(self.file1_path)
            file2_lines = self.read_file(self.file2_path)
            
            if self.debug:
                self.logger.debug("Creating diff table...")
            differ = difflib.HtmlDiff(tabsize=2, wrapcolumn=120)
            
            # Get the diff output first
            diff_table = differ.make_file(
                file1_lines, 
                file2_lines,
                fromdesc=os.path.basename(self.file1_path),
                todesc=os.path.basename(self.file2_path),
                context=True
            )
            
            # Clean up the HTML output
            diff_table = diff_table.replace('&nbsp;', ' ')  # Replace &nbsp; with regular spaces
            diff_table = diff_table.replace('<table class="diff"', '<table class="diff-table"')
            
            # Remove navigation cells and links
            diff_table = re.sub(r'<td class="diff_next".*?</td>', '', diff_table)
            diff_table = re.sub(r'<a href="#difflib_chg_.*?</a>', '', diff_table)
            
            # Fix the table structure to align file names correctly
            # First, extract the file names
            file1_name = os.path.basename(self.file1_path)
            file2_name = os.path.basename(self.file2_path)
            
            # Create a new table header with proper structure
            new_header = f'''
            <table class="diff-table" cellspacing="0" cellpadding="0">
            <colgroup>
                <col class="diff_header" width="4%" />
                <col width="46%" />
                <col class="diff_header" width="4%" />
                <col width="46%" />
            </colgroup>
            <thead>
                <tr>
                    <th colspan="2" class="diff_header">{file1_name}</th>
                    <th colspan="2" class="diff_header">{file2_name}</th>
                </tr>
            </thead>
            '''
            
            # Replace the original table header with our new one
            diff_table = re.sub(
                r'<table class="diff-table".*?<tr>.*?</tr>',
                new_header,
                diff_table,
                flags=re.DOTALL
            )
            
            if self.debug:
                self.logger.debug("Diff generation complete")
            return {
                'file1_info': file1_info,
                'file2_info': file2_info,
                'diff_html': diff_table
            }
        except Exception as e:
            self.logger.exception(f"Error generating diff:")
            raise DifferError(f"Failed to generate diff: {str(e)}")
