import time
import os
from watchdog.events import FileSystemEventHandler

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, differ, socket):
        self.differ = differ
        self.socket = socket
        self.last_modified = 0
        
    def on_modified(self, event):
        if not event.is_directory:  # Only handle file modifications
            current_time = time.time()
            # Increase debounce time to 300ms
            if current_time - self.last_modified > 0.3:
                self.last_modified = current_time
                # Get absolute paths for comparison
                event_path = os.path.abspath(event.src_path)
                file1_path = os.path.abspath(self.differ.file1_path)
                file2_path = os.path.abspath(self.differ.file2_path)
                
                if event_path in [file1_path, file2_path]:
                    print(f"File changed: {event_path}")  # Debug log
                    diff_data = self.differ.get_diff()
                    self.socket.emit('update_diff', diff_data, namespace='/')
