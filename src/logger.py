# Logging utility
import logging
from datetime import datetime
import os

class BuildLogger:
    def __init__(self, log_dir='logs'):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
    def log_build_result(self, build_id, stage, status, details):
        """
        Log build results to a new file in the "logs" folder.
        
        Args:
            build_id (str): Unique identifier for the build
            stage (str): Pipeline stage (e.g., 'syntax_check', 'tests')
            status (str): Status of the stage ('success', 'failure')
            details (str): Additional information about the stage result
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_file = os.path.join(self.log_dir, f'build_{build_id}.log')
        
        with open(log_file, 'a') as f:
            f.write(f'[{timestamp}] {stage}: {status}\n')
            f.write(f'Details: {details}\n\n')