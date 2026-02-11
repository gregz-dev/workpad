# Workpad - Plan de Test et Découverte

Ce document vous guide à travers les différentes fonctionnalités de Workpad pour apprendre à l'utiliser et vérifier que tout fonctionne.

## Prérequis

```bash
cd /home/greg/src/workpad
pip install -e .
```

## Test 1: Utilisation comme Bibliothèque Python

### 1.1 Test Basique avec SQLite Storage

```bash
python3 examples/basic_usage.py
```

**Résultat attendu:**
- Création de 2 entrées (note + task)
- Affichage de la liste filtrée
- Statistiques affichées

**Vérification:**
```bash
ls -la example_data/
# Vous devriez voir workpad.db
sqlite3 example_data/workpad.db "SELECT id, type, content FROM entries;"
```

### 1.2 Test Interactif avec JSON Storage

Créez `examples/test_interactive.py`:

```python
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
```

Exécutez:
```bash
python3 examples/test_interactive.py
```

**Vérification:**
```bash
ls -la my_test_data/
# Vous devriez voir des fichiers JSON
ls my_test_data/entries/2026-*/*.json
# Voir le contenu d'un fichier
cat my_test_data/entries/2026-*/*.json | head -1 | python3 -m json.tool
```

## Test 2: Utilisation avec SQLite

### 2.1 Test SQLite Storage

Créez `test_sqlite.py`:

```python
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
```

Exécutez:
```bash
python3 test_sqlite.py
```

Vérifiez la base de données:
```bash
ls -la sqlite_test_data/
sqlite3 sqlite_test_data/workpad.db "SELECT COUNT(*) FROM entries;"
sqlite3 sqlite_test_data/workpad.db "SELECT type, COUNT(*) FROM entries GROUP BY type;"
```

## Test 3: API REST

### 3.1 Démarrer le serveur

Terminal 1:
```bash
export WORKPAD_DATA_PATH=./api_test_data
export WORKPAD_STORAGE_TYPE=json
flask --app workpad.api:create_app run --debug
```

**Résultat attendu:**
- Serveur démarre sur http://127.0.0.1:5000
- Aucune erreur

### 3.2 Test Health Check

Terminal 2:
```bash
curl http://localhost:5000/api/v1/health
```

**Résultat attendu:**
```json
{"status":"ok"}
```

### 3.3 Test CRUD via API

```bash
# Créer une entrée
curl -X POST http://localhost:5000/api/v1/entries \
  -H "Content-Type: application/json" \
  -d '{
    "type": "note",
    "content": "Test via API",
    "tags": ["api", "test"]
  }'

# Sauvegarder l'ID retourné, puis:
ENTRY_ID="<id-retourné>"

# Récupérer l'entrée
curl http://localhost:5000/api/v1/entries/$ENTRY_ID

# Lister toutes les entrées
curl http://localhost:5000/api/v1/entries

# Filtrer par type
curl "http://localhost:5000/api/v1/entries?type=note"

# Ajouter du contexte
curl -X POST http://localhost:5000/api/v1/entries/$ENTRY_ID/context \
  -H "Content-Type: application/json" \
  -d '{
    "type": "note",
    "source": "api-test",
    "content": "Context ajouté via API"
  }'

# Vérifier
curl http://localhost:5000/api/v1/entries/$ENTRY_ID

# Stats
curl http://localhost:5000/api/v1/stats
```

### 3.4 Test avec le script client

```bash
python3 examples/api_client.py
```

**Résultat attendu:**
- Connexion réussie
- Création d'entrée
- Ajout de contexte
- Affichage des détails

## Test 4: Configuration

### 4.1 Test avec fichier .env

Créez `.env`:
```bash
WORKPAD_DATA_PATH=/tmp/workpad_env_test
WORKPAD_STORAGE_TYPE=sqlite
WORKPAD_LOG_LEVEL=DEBUG
```

Puis:
```bash
python3 -c "from workpad.config import settings; print(f'Data path: {settings.DATA_PATH}'); print(f'Storage: {settings.STORAGE_TYPE}')"
```

### 4.2 Test avec config.yaml

Créez `config.yaml`:
```yaml
data_path: /tmp/workpad_yaml_test
storage_type: json
log_level: WARNING
cors_origins: "*"
```

Puis:
```bash
python3 -c "from workpad.config import settings; print(f'Data path: {settings.DATA_PATH}'); print(f'Log level: {settings.LOG_LEVEL}')"
```

## Test 5: Docker (si disponible)

### 5.1 Build

```bash
docker build -t workpad .
```

### 5.2 Run avec Docker Compose

```bash
docker-compose up -d
```

Vérifiez:
```bash
docker-compose ps
curl http://localhost:5000/api/v1/health
```

Arrêtez:
```bash
docker-compose down
```

## Test 6: Tests Automatisés

### 6.1 Tous les tests

```bash
pytest -v
```

**Résultat attendu:** 31 tests passent

### 6.2 Tests par module

```bash
# Foundation
pytest tests/test_models.py -v

# Storage
pytest tests/test_storage.py tests/test_sqlite_storage.py -v

# Service
pytest tests/test_service.py -v

# API
pytest tests/test_api.py -v
```

### 6.3 Avec couverture

```bash
pytest --cov=workpad --cov-report=html
# Ouvrir htmlcov/index.html dans un navigateur
```

## Checklist de Validation

- [ ] ✓ Exemple `basic_usage.py` fonctionne
- [ ] ✓ Script interactif avec JSON storage fonctionne
- [ ] ✓ Script avec SQLite storage fonctionne
- [ ] ✓ Serveur Flask démarre sans erreur
- [ ] ✓ Health check API répond
- [ ] ✓ CRUD via API fonctionne
- [ ] ✓ Script `api_client.py` fonctionne
- [ ] ✓ Configuration via .env fonctionne
- [ ] ✓ Configuration via YAML fonctionne
- [ ] ✓ Tous les tests pytest passent (31/31)
- [ ] ✓ Docker build réussit (si disponible)

## Scénarios d'Usage Réels

### Scénario 1: Journal de Recherche

```python
from workpad.storage.sqlite_storage import SQLiteStorage
from workpad.service import WorkpadService
from workpad.models import EntryCreate, EntryType, ContextItemCreate, ContextType

storage = SQLiteStorage("./research_journal")
storage.initialize()
service = WorkpadService(storage)

# Note de lecture
paper = service.create_entry(EntryCreate(
    type=EntryType.note,
    content="Paper: Attention is All You Need - Transformers architecture",
    tags=["paper", "nlp", "transformers"],
    metadata={"authors": "Vaswani et al.", "year": 2017}
))

# Ajouter source
service.add_context(paper.id, ContextItemCreate(
    type=ContextType.url,
    source="arxiv",
    content="https://arxiv.org/abs/1706.03762"
))

# Idée liée
idea = service.create_entry(EntryCreate(
    type=EntryType.idea,
    content="Appliquer self-attention au projet X",
    tags=["idea", "project-x"]
))

service.add_relation(paper.id, idea.id)
```

### Scénario 2: Suivi de Tâches

```python
# Créer des tâches
task1 = service.create_entry(EntryCreate(
    type=EntryType.task,
    content="Implémenter feature A",
    tags=["sprint-1", "backend"],
    metadata={"priority": "high", "estimate": "3d"}
))

task2 = service.create_entry(EntryCreate(
    type=EntryType.task,
    content="Tests pour feature A",
    tags=["sprint-1", "testing"]
))

# Lier les tâches
service.add_relation(task1.id, task2.id)

# Rechercher tâches du sprint
from workpad.models import EntryFilter
sprint_tasks = service.list_entries(EntryFilter(tags=["sprint-1"]))
print(f"Sprint 1: {len(sprint_tasks)} tâches")
```

## Dépannage

### Problème: Module not found
```bash
pip install -e .
```

### Problème: Permission denied sur data/
```bash
chmod -R u+w data/
```

### Problème: Port 5000 déjà utilisé
```bash
flask --app workpad.api:create_app run --port 5001
```

### Problème: Tests échouent
```bash
# Nettoyer les données de test
rm -rf test_data/ example_data/ my_test_data/ sqlite_test_data/
pytest -v
```
