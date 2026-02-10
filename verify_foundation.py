from workpad.models import Entry, EntryCreate, EntryType, EntryStatus, EntryFilter
from workpad.storage.json_storage import JSONStorage
from pathlib import Path
import shutil
import uuid

# Setup
data_path = Path("./data_verify")
if data_path.exists():
    shutil.rmtree(data_path)

data_path.mkdir(exist_ok=True)

storage = JSONStorage(str(data_path))
storage.initialize()

# Create
print("Creating entry...")
# We must create a full Entry object for the storage layer
# The Service layer (future) would handle EntryCreate -> Entry conversion
entry = Entry(
    type=EntryType.observation, 
    content="Test content verification", 
    tags=["verify"]
)
saved_entry = storage.create(entry)
print(f"Created entry: {saved_entry.id}")

# Read
print("Reading entry...")
loaded = storage.get(saved_entry.id)
assert loaded is not None
assert loaded.content == "Test content verification"
assert loaded.id == saved_entry.id
print("Read successful")

# List
print("Listing entries...")
entries = storage.list(EntryFilter(tags=["verify"]))
assert len(entries) == 1
print(f"List successful: found {len(entries)} entry")

# Cleanup
shutil.rmtree(data_path)
print("Verification complete!")
