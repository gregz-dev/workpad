import os
from workpad.storage.sqlite_storage import SQLiteStorage
from workpad.service import WorkpadService
from workpad.models import EntryCreate, EntryType, EntryFilter

def main():
    # 1. Initialize Storage
    # We use a local SQLite database for this example
    db_path = "example_data"
    os.makedirs(db_path, exist_ok=True)
    
    storage = SQLiteStorage(db_path)
    storage.initialize()
    
    # 2. Initialize Service
    service = WorkpadService(storage)
    
    print("--- Workpad Library Usage Example ---")
    
    # 3. Create Entries
    print("\n1. Creating entries...")
    note = service.create_entry(EntryCreate(
        type=EntryType.note,
        content="This is a simple note created via the library.",
        tags=["example", "note"]
    ))
    print(f"   Created Note: {note.id}")
    
    task = service.create_entry(EntryCreate(
        type=EntryType.task,
        content="Finish the documentation",
        tags=["example", "urgent"],
        metadata={"priority": "high"}
    ))
    print(f"   Created Task: {task.id}")
    
    # 4. List Entries
    print("\n2. Listing entries (tag='example')...")
    filters = EntryFilter(tags=["example"])
    entries = service.list_entries(filters)
    for e in entries:
        print(f"   - [{e.type.value}] {e.content} (ID: {e.id})")
        
    # 5. Stats
    print("\n3. Stats:")
    stats = service.get_stats()
    print(f"   {stats}")

if __name__ == "__main__":
    main()
