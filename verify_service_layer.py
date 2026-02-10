from workpad.service import WorkpadService
from workpad.storage.json_storage import JSONStorage
from workpad.models import EntryCreate, EntryType, ContextItemCreate, ContextType
from pathlib import Path
import shutil

# Setup
data_path = Path("./data_service_verify")
if data_path.exists():
    shutil.rmtree(data_path)
    
data_path.mkdir(exist_ok=True)

storage = JSONStorage(str(data_path))
storage.initialize()
service = WorkpadService(storage)

# Create
print("Creating entry...")
entry = service.create_entry(EntryCreate(type=EntryType.task, content="Verify service"))
print(f"Created: {entry.id}")

# Add context
print("Adding context...")
ctx = service.add_context(entry.id, ContextItemCreate(
    type=ContextType.note, source="manual", content="Manual context"
))
print(f"Added context: {ctx.id}")

# Verify Context Persistence
print("Verifying context...")
loaded = service.get_entry(entry.id)
assert len(loaded.context_items) == 1
assert loaded.context_items[0].content == "Manual context"
print("Context verified")

# Relations
print("Testing relations...")
entry2 = service.create_entry(EntryCreate(type=EntryType.note, content="Linked entry"))
service.add_relation(entry.id, entry2.id)

l1 = service.get_entry(entry.id)
l2 = service.get_entry(entry2.id)
assert entry2.id in l1.related_entries
assert entry.id in l2.related_entries
print("Relations verified")

# Cleanup
shutil.rmtree(data_path)
print("Verification complete!")
