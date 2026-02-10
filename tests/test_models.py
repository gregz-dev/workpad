import pytest
from pydantic import ValidationError
from workpad.models import Entry, EntryCreate, ContextItem, EntryType, EntryStatus

def test_entry_creation_defaults():
    entry = Entry(type=EntryType.note, content="Hello")
    assert entry.id is not None
    assert entry.timestamp is not None
    assert entry.status == EntryStatus.active
    assert entry.tags == []

def test_entry_validation_content_length():
    with pytest.raises(ValidationError):
        Entry(type=EntryType.note, content="a" * 50001)

def test_entry_validation_tags():
    tags = ["valid", "a" * 51] # 51 chars is too long
    with pytest.raises(ValidationError):
        Entry(type=EntryType.note, content="test", tags=tags)

def test_context_item_creation():
    item = ContextItem(
        type="file", 
        source="test.py", 
        content="print('hello')"
    )
    assert item.id is not None
    assert item.created_at is not None
