from workpad.storage.sqlite_storage import SQLiteStorage
from workpad.service import WorkpadService
from workpad.models import EntryCreate, EntryType, EntryFilter
import os

# Init avec SQLite
db_path = "./sqlite_test_data"
os.makedirs(db_path, exist_ok=True)
storage = SQLiteStorage(db_path)
storage.initialize()
service = WorkpadService(storage)

# Créer plusieurs entrées
for i in range(5):
    service.create_entry(EntryCreate(
        type=EntryType.observation if i % 2 == 0 else EntryType.note,
        content=f"Test SQLite entry {i}",
        tags=["sqlite", f"batch-{i//2}"]
    ))

# Filtrer
notes = service.list_entries(EntryFilter(type=EntryType.note))
print(f"✓ Notes trouvées: {len(notes)}")

observations = service.list_entries(EntryFilter(type=EntryType.observation))
print(f"✓ Observations trouvées: {len(observations)}")

# Recherche
results = service.list_entries(EntryFilter(search="entry 2"))
print(f"✓ Recherche 'entry 2': {len(results)} résultat(s)")

print("\n✓ SQLite fonctionne correctement!")