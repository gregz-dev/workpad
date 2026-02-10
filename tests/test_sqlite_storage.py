import pytest
from datetime import datetime
from workpad.storage.sqlite_storage import SQLiteStorage
from workpad.models import Entry, EntryCreate, EntryUpdate, EntryFilter, EntryType, EntryStatus, ContextItem

@pytest.fixture
def storage():
    # Use in-memory DB for speed and isolation
    s = SQLiteStorage(":memory:")
    s.initialize()
    return s

@pytest.fixture
def sample_entry_domain():
    return Entry(
        type=EntryType.observation,
        content="SQLite Test",
        tags=["sqlite", "test"]
    )

def test_initialize(storage):
    # Should not raise
    pass

def test_create_and_get(storage, sample_entry_domain):
    saved = storage.create(sample_entry_domain)
    assert saved.id == sample_entry_domain.id
    
    loaded = storage.get(saved.id)
    assert loaded is not None
    assert loaded.content == "SQLite Test"
    assert loaded.tags == ["sqlite", "test"]

def test_list_filters(storage):
    e1 = Entry(type=EntryType.note, content="Note 1", tags=["a"])
    e2 = Entry(type=EntryType.task, content="Task 1", tags=["b"])
    storage.create(e1)
    storage.create(e2)
    
    # Filter by type
    res = storage.list(EntryFilter(type=EntryType.note))
    assert len(res) == 1
    assert res[0].content == "Note 1"
    
    # Filter by tag
    res = storage.list(EntryFilter(tags=["b"]))
    assert len(res) == 1
    assert res[0].content == "Task 1"
    
    # Search
    res = storage.list(EntryFilter(search="Task"))
    assert len(res) == 1

def test_update(storage, sample_entry_domain):
    entry = storage.create(sample_entry_domain)
    
    update = EntryUpdate(content="Updated Content", tags=["new"])
    updated = storage.update(entry.id, update)
    
    assert updated.content == "Updated Content"
    assert updated.tags == ["new"]
    
    loaded = storage.get(entry.id)
    assert loaded.content == "Updated Content"

def test_update_context(storage):
    e = Entry(type=EntryType.note, content="Context Update Test")
    entry = storage.create(e)
    
    # Add context via update (simulating service layer)
    ctx = ContextItem(type="note", source="test", content="Ctx 1")
    update = EntryUpdate(context_items=[ctx])
    
    updated = storage.update(entry.id, update)
    assert len(updated.context_items) == 1
    assert updated.context_items[0].content == "Ctx 1"
    
    # Reload
    loaded = storage.get(entry.id)
    assert len(loaded.context_items) == 1

def test_delete(storage, sample_entry_domain):
    entry = storage.create(sample_entry_domain)
    assert storage.delete(entry.id) is True
    assert storage.get(entry.id) is None
    assert storage.delete(entry.id) is False
