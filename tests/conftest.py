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
def sample_entry() -> Entry:
    """Create a sample entry object."""
    return Entry(
        type=EntryType.observation,
        content="This is a test entry",
        tags=["test", "sample"]
    )
