import json
import datetime
import uuid
import os

class ReadWrite:

    @staticmethod
    def read(path):
        """Loads and returns JSON data from a file."""
        with open(path, "r") as f:
            data = json.loads(f.read())
            return data

    @staticmethod
    def write_json(data, path):
        """Writes data to a JSON file."""
        with open(path, "w") as file:
            json.dump(data, file, indent=4)

    @staticmethod
    def log_error(path, message, email, model):
        """Appends an error log entry to a log file."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%d-%m-%Y %H:%M %p")
        error_id  = uuid.uuid4().hex[:8]
        log_line  = (
            f"Email={email} | {timestamp} | model={model} | "
            f"ERROR_ID={error_id} - {message}\n"
        )
        with open(path, "a") as file:
            file.write(log_line)