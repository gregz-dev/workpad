import os
from pathlib import Path
import logging.config
import yaml
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Settings:
    def __init__(self):
        # Load defaults
        self.DATA_PATH = "./data"
        self.STORAGE_TYPE = "json"
        self.LOG_LEVEL = "INFO"
        self.CORS_ORIGINS = "*"
        
        # Load from config.yaml if present
        self._load_from_yaml()
        
        # Override with Environment Variables
        self.DATA_PATH = os.environ.get("WORKPAD_DATA_PATH", self.DATA_PATH)
        self.STORAGE_TYPE = os.environ.get("WORKPAD_STORAGE_TYPE", self.STORAGE_TYPE)
        self.LOG_LEVEL = os.environ.get("WORKPAD_LOG_LEVEL", self.LOG_LEVEL)
        self.CORS_ORIGINS = os.environ.get("WORKPAD_CORS_ORIGINS", self.CORS_ORIGINS)

    def _load_from_yaml(self):
        config_path = Path("config.yaml")
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f) or {}
                    self.DATA_PATH = config.get("data_path", self.DATA_PATH)
                    self.STORAGE_TYPE = config.get("storage_type", self.STORAGE_TYPE)
                    self.LOG_LEVEL = config.get("log_level", self.LOG_LEVEL)
                    self.CORS_ORIGINS = config.get("cors_origins", self.CORS_ORIGINS)
            except Exception as e:
                print(f"Warning: Failed to load config.yaml: {e}")

    def configure_logging(self):
        logging_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
                },
                "json": {
                     "format": '{"time": "%(asctime)s", "level": "%(levelname)s", "module": "%(module)s", "message": "%(message)s"}'
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "level": self.LOG_LEVEL,
                },
                "file": {
                    "class": "logging.FileHandler",
                    "filename": "workpad.log",
                    "formatter": "json",
                    "level": "INFO",
                }
            },
            "root": {
                "handlers": ["console", "file"],
                "level": self.LOG_LEVEL,
            },
            "loggers": {
                "werkzeug": {
                    "level": "WARNING", # Reduce flask noise
                }
            }
        }
        logging.config.dictConfig(logging_config)

settings = Settings()
