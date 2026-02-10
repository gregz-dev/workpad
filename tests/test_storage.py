import pytest
from workpad.models import Entry, EntryUpdate, EntryFilter, EntryType, EntryStatus
from workpad.storage.json_storage import JSONStorage

def test_storage_initialize(test_data_path):
    store = JSONStorage(str(test_data_path))
    store.initialize()
    assert (test_data_path / "entries").exists()
    assert (test_data_path / "metadata.json").exists()

def test_create_and_get_entry(storage, sample_entry):
    saved = storage.create(sample_entry)
    assert saved.id == sample_entry.id
    
    loaded = storage.get(saved.id)
    assert loaded is not None
    assert loaded.id == saved.id
    assert loaded.content == saved.content

def test_list_entries(storage):
    # Create 3 entries
    e1 = Entry(type=EntryType.observation, content="First", tags=["tag1"])
    e2 = Entry(type=EntryType.hypothesis, content="Second", tags=["tag2"])
    e3 = Entry(type=EntryType.observation, content="Third", tags=["tag1"])
    
    storage.create(e1)
    storage.create(e2)
    storage.create(e3)
    
    # List all
    all_entries = storage.list(EntryFilter())
    assert len(all_entries) == 3
    
    # Filter by type
    obs = storage.list(EntryFilter(type=EntryType.observation))
    assert len(obs) == 2
    
    # Filter by tag
    t1 = storage.list(EntryFilter(tags=["tag1"]))
    assert len(t1) == 2

def test_update_entry(storage, sample_entry):
    storage.create(sample_entry)
    
    update = EntryUpdate(content="Updated content", status=EntryStatus.completed)
    updated = storage.update(sample_entry.id, update)
    
    assert updated.content == "Updated content"
    assert updated.status == EntryStatus.completed
    assert updated.updated_at > sample_entry.updated_at
    
    # Verify persistence
    loaded = storage.get(sample_entry.id)
    assert loaded.content == "Updated content"

def test_delete_entry(storage, sample_entry):
    storage.create(sample_entry)
    assert storage.get(sample_entry.id) is not None
    
    result = storage.delete(sample_entry.id)
    assert result is True
    assert storage.get(sample_entry.id) is None
