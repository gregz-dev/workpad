import pytest
import shutil
from pathlib import Path
from workpad.storage.json_storage import JSONStorage
from workpad.models import Entry, EntryCreate, EntryType

@pytest.fixture
def test_data_path(tmp_path):
    """Create a temporary directory for test data."""
    path = tmp_path / "workpad_data"
    path.mkdir()
    yield path
    # Cleanup handled by tmp_path fixture

@pytest.fixture
def storage(test_data_path):
    """Create initialized storage instance."""
    store = JSONStorage(str(test_data_path))
    store.initialize()
    return store

@pytest.fixture
def app(storage):
    from workpad.api import create_app
    from workpad.config import Settings
    
    class TestSettings(Settings):
        DATA_PATH = str(storage.data_path)
        
    app = create_app()
    # Mock/Override storage in the service?
    # Our routes.py instantiates WorkpadService(JSONStorage(settings.DATA_PATH))
    # So we need to ensure the app uses the test data path.
    # The routes.py `get_service` function imports `settings` from `..config`.
    # We need to patch that settings object or set environment variable.
    
    # Patch the global settings object in config module
    import workpad.config
    workpad.config.settings.DATA_PATH = str(storage.data_path)
    
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def sample_entry() -> Entry:
    """Create a sample entry object."""
    return Entry(
        type=EntryType.observation,
        content="This is a test entry",
        tags=["test", "sample"]
    )
