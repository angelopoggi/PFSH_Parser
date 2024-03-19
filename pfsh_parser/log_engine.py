import os
from datetime import datetime


class LogEngine:
    def __init__(self, file_path="log.txt"):
        self.file_path = file_path

    def log(self, message):
        """Logs a message to a file with a timestamp and returns the file path."""
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

        # Open the file and append the message
        with open(self.file_path, "a") as file:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            file.write(f"{timestamp} - {message}\n")

        # Return the path to the log file
        return self.file_path
