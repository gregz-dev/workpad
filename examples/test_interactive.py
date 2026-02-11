
from workpad.storage.json_storage import JSONStorage
from workpad.service import WorkpadService
from workpad.models import EntryCreate, EntryType, ContextItemCreate, ContextType

# Init
storage = JSONStorage("./my_test_data")
storage.initialize()
service = WorkpadService(storage)

# 1. Créer une note
note = service.create_entry(EntryCreate(
    type=EntryType.note,
    content="Ma première note de test",
    tags=["test", "apprentissage"]
))
print(f"✓ Note créée: {note.id}")

# 2. Ajouter du contexte
ctx = service.add_context(note.id, ContextItemCreate(
    type=ContextType.url,
    source="documentation",
    content="https://example.com/doc"
))
print(f"✓ Contexte ajouté: {ctx.id}")

# 3. Créer une deuxième entrée et la lier
task = service.create_entry(EntryCreate(
    type=EntryType.task,
    content="Tester les relations",
    tags=["test"]
))
service.add_relation(note.id, task.id)
print(f"✓ Relation créée entre {note.id} et {task.id}")

# 4. Récupérer et afficher
loaded = service.get_entry(note.id)
print(f"\n✓ Note rechargée:")
print(f"  - Content: {loaded.content}")
print(f"  - Context items: {len(loaded.context_items)}")
print(f"  - Relations: {loaded.related_entries}")

# 5. Stats
stats = service.get_stats()
print(f"\n✓ Statistiques: {stats}")