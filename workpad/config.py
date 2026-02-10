import os
from pathlib import Path

class Settings:
    def __init__(self):
        # Default to ./data if not set
        self.DATA_PATH = os.environ.get("WORKPAD_DATA_PATH", "./data")
        self.STORAGE_TYPE = os.environ.get("WORKPAD_STORAGE_TYPE", "json") # json or sqlite

settings = Settings()
