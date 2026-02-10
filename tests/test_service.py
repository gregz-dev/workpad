import pytest
from datetime import datetime
from workpad.service import WorkpadService
from workpad.models import EntryCreate, EntryUpdate, EntryType, EntryStatus, ContextItemCreate, ContextType
from workpad.errors import NotFoundError, ValidationError

@pytest.fixture
def service(storage):
    return WorkpadService(storage)

def test_create_entry(service):
    data = EntryCreate(type=EntryType.note, content="Service test")
    entry = service.create_entry(data)
    assert entry.id is not None
    assert entry.content == "Service test"
    
    # Verify persistence
    loaded = service.get_entry(entry.id)
    assert loaded.id == entry.id

def test_update_entry(service):
    data = EntryCreate(type=EntryType.note, content="Original")
    entry = service.create_entry(data)
    
    update = EntryUpdate(content="Updated")
    updated_entry = service.update_entry(entry.id, update)
    assert updated_entry.content == "Updated"
    
    loaded = service.get_entry(entry.id)
    assert loaded.content == "Updated"

def test_delete_entry(service):
    data = EntryCreate(type=EntryType.note, content="To delete")
    entry = service.create_entry(data)
    
    service.delete_entry(entry.id)
    
    with pytest.raises(NotFoundError):
        service.get_entry(entry.id)

def test_add_context(service):
    data = EntryCreate(type=EntryType.task, content="Task with context")
    entry = service.create_entry(data)
    
    ctx_data = ContextItemCreate(
        type=ContextType.note,
        source="user",
        content="Important context"
    )
    
    item = service.add_context(entry.id, ctx_data)
    assert item.content == "Important context"
    
    loaded = service.get_entry(entry.id)
    assert len(loaded.context_items) == 1
    assert loaded.context_items[0].content == "Important context"

def test_relations(service):
    e1 = service.create_entry(EntryCreate(type=EntryType.note, content="Entry 1"))
    e2 = service.create_entry(EntryCreate(type=EntryType.note, content="Entry 2"))
    
    # Link e1 -> e2
    service.add_relation(e1.id, e2.id)
    
    # Reload and check
    l1 = service.get_entry(e1.id)
    l2 = service.get_entry(e2.id)
    
    assert e2.id in l1.related_entries
    assert e1.id in l2.related_entries
    
    # Remove link
    service.remove_relation(e1.id, e2.id)
    
    l1 = service.get_entry(e1.id)
    l2 = service.get_entry(e2.id)
    
    assert e2.id not in l1.related_entries
    assert e1.id not in l2.related_entries

def test_relations_self_reference(service):
    e1 = service.create_entry(EntryCreate(type=EntryType.note, content="Entry 1"))
    with pytest.raises(ValidationError):
        service.add_relation(e1.id, e1.id)
