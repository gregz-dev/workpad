# Workpad Foundation Layer

This document describes the foundation layer of Workpad, which includes the core data models and the storage engine.

## Overview

The foundation layer is responsible for:
- Defining the data structures (`Entry`, `ContextItem`) using Pydantic.
- Providing a consistent interface for storage operations (`StorageInterface`).
- Implementing a file-based JSON storage backend (`JSONStorage`).

## Data Models

The core models are defined in `workpad.models`.

```plantuml
@startuml
enum EntryType {
  observation
  hypothesis
  test
  nextstep
  note
  task
}

enum EntryStatus {
  active
  completed
  invalidated
  confirmed
  archived
}

class ContextItem {
  +id: UUID
  +type: ContextType
  +source: string
  +content: string
  +metadata: map
  +created_at: datetime
}

class Entry {
  +id: UUID
  +timestamp: datetime
  +type: EntryType
  +content: string
  +context_items: List[ContextItem]
  +status: EntryStatus
  +related_entries: List[UUID]
  +tags: List[string]
  +metadata: map
  +created_at: datetime
  +updated_at: datetime
}

Entry *-- ContextItem
Entry -- EntryType
Entry -- EntryStatus
@enduml
```

## Storage Architecture

The storage layer is designed to be pluggable. The `JSONStorage` implementation stores entries as individual JSON files on the disk.

```plantuml
@startuml
interface StorageInterface {
  +initialize()
  +create(entry: Entry): Entry
  +get(entry_id: str): Entry
  +list(filters: EntryFilter): List[Entry]
  +update(entry_id: str, updates: EntryUpdate): Entry
  +delete(entry_id: str): bool
}

class JSONStorage {
  -data_path: Path
  -index: map
  +initialize()
  +create(entry: Entry): Entry
  +get(entry_id: str): Entry
  +list(filters: EntryFilter): List[Entry]
  +update(entry_id: str, updates: EntryUpdate): Entry
  +delete(entry_id: str): bool
  -_save_index()
  -_get_entry_path(id: str): Path
}

StorageInterface <|.. JSONStorage
@enduml
```

## Directory Structure

When using `JSONStorage`, the data is organized as follows:

```
data/
├── entries/
│   ├── YYYY-MM/
│   │   ├── <uuid>.json
│   │   └── ...
└── metadata.json  # Index for fast lookup
```

## Usage Example

```python
from workpad.models import Entry, EntryType
from workpad.storage.json_storage import JSONStorage

# Initialize storage
storage = JSONStorage("./data")
storage.initialize()

# Create entry
entry = Entry(
    type=EntryType.observation,
    content="This is a test entry",
    tags=["example"]
)
storage.create(entry)

# Retrieve entry
loaded = storage.get(entry.id)
print(loaded.content)
```
