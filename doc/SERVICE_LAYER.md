# Service Layer Architecture

The Service Layer acts as the intermediary between the external interfaces (API, CLI) and the persistence layer. It encapsulates all business logic and orchestrates complex operations.

## Architecture

```plantuml
@startuml
interface StorageInterface {
  +create(entry): Entry
  +get(id): Entry
  +update(id, updates): Entry
  +delete(id): bool
}

class WorkpadService {
  -storage: StorageInterface
  __ CRUD __
  +create_entry(data: EntryCreate): Entry
  +get_entry(id: str): Entry
  +list_entries(filters: EntryFilter): List[Entry]
  +update_entry(id: str, data: EntryUpdate): Entry
  +delete_entry(id: str): bool
  __ Context __
  +add_context(id: str, data: ContextItemCreate): ContextItem
  +remove_context(id: str, context_id: str): bool
  __ Relations __
  +add_relation(id1: str, id2: str): bool
  +remove_relation(id1: str, id2: str): bool
  __ Stats __
  +get_stats(): Dict
}

WorkpadService --> StorageInterface
@enduml
```

## Key Responsibilities

### 1. Data Transformation
The service converts DTOs (Data Transfer Objects) like `EntryCreate` into domain models (`Entry`) before passing them to storage.

### 2. Validation
It performs business-level validation, such as ensuring an entry cannot be linked to itself.

### 3. Context Management
It handles the addition of context items (`ContextItem`) to entries, ensuring correct instantiation and persistence.

### 4. Relations Management
It manages bidirectional relationships between entries. When `entry A` is linked to `entry B`, the service ensures `entry B` is also updated to reference `entry A`.

## Usage Example

```python
from workpad.service import WorkpadService
from workpad.storage.json_storage import JSONStorage
from workpad.models import EntryCreate, EntryType

# Initialize
storage = JSONStorage("./data")
service = WorkpadService(storage)

# Create
entry = service.create_entry(EntryCreate(
    type=EntryType.task,
    content="Implement feature X"
))

# Stats
stats = service.get_stats()
print(f"Total entries: {stats['total_entries']}")
```
