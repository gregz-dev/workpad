<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Workpad - Document d'Implémentation Complet

**Version:** 1.0
**Date:** 10 février 2026
**Repo:** `workpad`
**PyPI:** `workpad`

***

## Vue d'ensemble

### Objectif

Workpad est un **système générique de gestion de notes/entrées** avec timestamps, types, contexte et statuts. C'est un service réutilisable, indépendant et domain-agnostic qui peut servir pour :

- Lab notebooks scientifiques
- Project logs de développement
- Research notes académiques
- Task tracking et investigations
- Documentation de debugging
- Journaux d'incidents


### Philosophie

- **Simple et léger** : 50 MB RAM, dépendances minimales
- **Domain-agnostic** : aucune logique métier spécifique à Mindpad
- **RESTful** : API claire et standard
- **MCP-ready** : suit les guidelines pour être wrappable automatiquement
- **Testable** : tests unitaires complets inclus
- **Dockerizable** : peut tourner standalone ou s'intégrer dans un système plus large

***

## Architecture technique

### Stack technologique

| Composant | Technologie | Raison |
| :-- | :-- | :-- |
| **Web Framework** | Flask | Léger, flexible, standard |
| **Validation** | Pydantic | Type safety, auto-validation |
| **Storage** | JSON files (base) | Simple, portable, pas de dépendance DB |
| **Storage (optionnel)** | SQLite | Performance pour grandes volumétries |
| **Config** | Environment variables + YAML | Standard 12-factor app |
| **Logging** | Python logging module | Standard, configurable |
| **Tests** | pytest | Standard Python testing |
| **Documentation** | OpenAPI/Swagger | Auto-généré depuis Flask + Pydantic |

### Dépendances

**Core (minimal)** :

```
flask>=3.0.0
pydantic>=2.0.0
python-dotenv>=1.0.0
```

**Dev/Test** :

```
pytest>=7.0.0
pytest-cov>=4.0.0
black>=23.0.0
flake8>=6.0.0
```


### Mémoire attendue

- **Runtime minimal** : 30-40 MB
- **Avec données moyennes** (1000 entrées) : 50 MB
- **Maximum** : 80 MB

***

## Modèles de données

### Structures Pydantic

#### Entry (entrée principale)

```pseudocode
class Entry:
    id: str (UUID4)
    timestamp: datetime
    type: EntryType (enum: observation, hypothesis, test, nextstep, note, task)
    content: str (max 50000 chars)
    context_items: list[ContextItem] (default: [])
    status: EntryStatus (enum: active, completed, invalidated, confirmed, archived)
    related_entries: list[str] (UUIDs of related entries)
    tags: list[str] (max 20 tags, each max 50 chars)
    metadata: dict (flexible key-value pairs)
    created_at: datetime
    updated_at: datetime
```


#### ContextItem (élément de contexte attaché)

```pseudocode
class ContextItem:
    id: str (UUID4)
    type: ContextType (enum: code_snippet, file, stacktrace, log_excerpt, url, commit, note)
    source: str (description of source)
    content: str (max 100000 chars)
    metadata: dict (flexible)
    created_at: datetime
```


#### EntryCreate (request schema)

```pseudocode
class EntryCreate:
    type: EntryType
    content: str
    context_items: list[ContextItemCreate] (optional)
    tags: list[str] (optional)
    metadata: dict (optional)
```


#### EntryUpdate (update schema)

```pseudocode
class EntryUpdate:
    content: str (optional)
    type: EntryType (optional)
    status: EntryStatus (optional)
    tags: list[str] (optional)
    metadata: dict (optional)
```


#### EntryFilter (query parameters)

```pseudocode
class EntryFilter:
    type: EntryType (optional)
    status: EntryStatus (optional)
    tags: list[str] (optional, OR logic)
    search: str (optional, full-text in content)
    from_date: datetime (optional)
    to_date: datetime (optional)
    limit: int (default: 100, max: 1000)
    offset: int (default: 0)
```


### Enums

```pseudocode
enum EntryType:
    observation = "observation"
    hypothesis = "hypothesis"
    test = "test"
    nextstep = "nextstep"
    note = "note"
    task = "task"

enum EntryStatus:
    active = "active"
    completed = "completed"
    invalidated = "invalidated"
    confirmed = "confirmed"
    archived = "archived"

enum ContextType:
    code_snippet = "code_snippet"
    file = "file"
    stacktrace = "stacktrace"
    log_excerpt = "log_excerpt"
    url = "url"
    commit = "commit"
    note = "note"
```


***

## API REST

### Endpoints

#### 1. **Créer une entrée**

```
POST /entries
Content-Type: application/json

Body: EntryCreate

Response: 201 Created
{
  "id": "uuid",
  "timestamp": "2026-02-10T21:30:00Z",
  "type": "observation",
  "content": "...",
  ...
}
```

**Docstring** :

```
Create a new entry (observation, hypothesis, test, note, task, etc.)
```


#### 2. **Lister les entrées**

```
GET /entries?type=observation&status=active&limit=50&offset=0

Response: 200 OK
{
  "entries": [...],
  "total": 142,
  "limit": 50,
  "offset": 0
}
```

**Docstring** :

```
List entries with optional filters (type, status, tags, date range, search)
```


#### 3. **Obtenir une entrée**

```
GET /entries/{entry_id}

Response: 200 OK
{
  "id": "uuid",
  ...
}

Response: 404 Not Found
{
  "error": "Entry not found",
  "code": 404
}
```

**Docstring** :

```
Get a single entry by ID
```


#### 4. **Mettre à jour une entrée**

```
PUT /entries/{entry_id}
Content-Type: application/json

Body: EntryUpdate

Response: 200 OK
{
  "id": "uuid",
  "updated_at": "2026-02-10T21:35:00Z",
  ...
}
```

**Docstring** :

```
Update an existing entry (content, status, tags, metadata)
```


#### 5. **Supprimer une entrée**

```
DELETE /entries/{entry_id}

Response: 204 No Content

Response: 404 Not Found
```

**Docstring** :

```
Delete an entry by ID
```


#### 6. **Ajouter un contexte à une entrée**

```
POST /entries/{entry_id}/context
Content-Type: application/json

Body: ContextItemCreate

Response: 201 Created
{
  "id": "context-uuid",
  "type": "code_snippet",
  ...
}
```

**Docstring** :

```
Add a context item (code, file, stacktrace, etc.) to an entry
```


#### 7. **Supprimer un contexte**

```
DELETE /entries/{entry_id}/context/{context_id}

Response: 204 No Content
```

**Docstring** :

```
Remove a context item from an entry
```


#### 8. **Lier deux entrées**

```
POST /entries/{entry_id}/relations/{related_entry_id}

Response: 200 OK
{
  "message": "Entries linked",
  "related_entries": ["uuid1", "uuid2"]
}
```

**Docstring** :

```
Create a bidirectional relation between two entries
```


#### 9. **Statistiques**

```
GET /entries/stats

Response: 200 OK
{
  "total_entries": 142,
  "by_type": {
    "observation": 50,
    "hypothesis": 30,
    ...
  },
  "by_status": {
    "active": 80,
    "completed": 40,
    ...
  },
  "date_range": {
    "oldest": "2026-01-01T00:00:00Z",
    "newest": "2026-02-10T21:30:00Z"
  }
}
```

**Docstring** :

```
Get statistics about entries (counts by type, status, date range)
```


#### 10. **Exporter en JSON**

```
GET /entries/export?format=json&type=observation

Response: 200 OK
Content-Type: application/json
Content-Disposition: attachment; filename="workpad_export_20260210.json"

{
  "exported_at": "2026-02-10T21:30:00Z",
  "entries": [...]
}
```

**Docstring** :

```
Export entries as JSON with optional filters
```


#### 11. **Exporter en Markdown**

```
GET /entries/export?format=markdown

Response: 200 OK
Content-Type: text/markdown
Content-Disposition: attachment; filename="workpad_export_20260210.md"

# Workpad Export
Date: 2026-02-10

## Observations
- [2026-02-10 21:00] Content here...
...
```

**Docstring** :

```
Export entries as formatted Markdown with optional filters
```


#### 12. **Recherche full-text**

```
GET /entries/search?q=segfault&limit=20

Response: 200 OK
{
  "results": [...],
  "query": "segfault",
  "total": 5
}
```

**Docstring** :

```
Full-text search across entry content
```


#### 13. **Health check**

```
GET /health

Response: 200 OK
{
  "status": "healthy",
  "version": "1.0.0",
  "storage": "json",
  "entries_count": 142
}
```

**Docstring** :

```
Health check endpoint for monitoring
```


***

## Stockage

### Option 1 : JSON Files (par défaut)

**Structure de fichiers** :

```
data/
├── entries/
│   ├── 2026-02/
│   │   ├── entry_uuid1.json
│   │   ├── entry_uuid2.json
│   │   └── ...
│   └── 2026-01/
│       └── ...
└── metadata.json (index rapide)
```

**Avantages** :

- Simple, pas de setup
- Portable, facile à backup
- Human-readable
- Pas de dépendance

**Inconvénients** :

- Performance limitée à ~10K entrées
- Pas de transactions
- Full-scan pour les recherches


### Option 2 : SQLite (optionnel)

**Schema** :

```sql
CREATE TABLE entries (
    id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    type TEXT NOT NULL,
    content TEXT NOT NULL,
    status TEXT NOT NULL,
    tags TEXT, -- JSON array
    metadata TEXT, -- JSON object
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE context_items (
    id TEXT PRIMARY KEY,
    entry_id TEXT NOT NULL,
    type TEXT NOT NULL,
    source TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata TEXT, -- JSON object
    created_at TEXT NOT NULL,
    FOREIGN KEY (entry_id) REFERENCES entries(id) ON DELETE CASCADE
);

CREATE TABLE entry_relations (
    entry_id TEXT NOT NULL,
    related_entry_id TEXT NOT NULL,
    PRIMARY KEY (entry_id, related_entry_id),
    FOREIGN KEY (entry_id) REFERENCES entries(id) ON DELETE CASCADE,
    FOREIGN KEY (related_entry_id) REFERENCES entries(id) ON DELETE CASCADE
);

CREATE INDEX idx_entries_type ON entries(type);
CREATE INDEX idx_entries_status ON entries(status);
CREATE INDEX idx_entries_timestamp ON entries(timestamp);
CREATE INDEX idx_context_entry ON context_items(entry_id);
```

**Avantages** :

- Performance jusqu'à 100K+ entrées
- Transactions ACID
- Indexes efficaces
- Still file-based, portable


### Configuration du storage

Via environment variable :

```
WORKPAD_STORAGE_TYPE=json  # ou sqlite
WORKPAD_STORAGE_PATH=./data  # chemin du dossier
```


***

## Configuration

### Variables d'environnement

```bash
# Server
WORKPAD_HOST=0.0.0.0
WORKPAD_PORT=5001
WORKPAD_DEBUG=false

# Storage
WORKPAD_STORAGE_TYPE=json  # json ou sqlite
WORKPAD_STORAGE_PATH=./data

# Limits
WORKPAD_MAX_ENTRIES=10000  # limite totale
WORKPAD_MAX_CONTENT_LENGTH=50000  # chars par entry
WORKPAD_MAX_CONTEXT_LENGTH=100000  # chars par context

# Logging
WORKPAD_LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
WORKPAD_LOG_FILE=./logs/workpad.log

# CORS (pour usage web)
WORKPAD_CORS_ENABLED=true
WORKPAD_CORS_ORIGINS=*  # ou liste d'URLs
```


### Fichier config.yaml (optionnel)

```yaml
server:
  host: 0.0.0.0
  port: 5001
  debug: false

storage:
  type: json
  path: ./data

limits:
  max_entries: 10000
  max_content_length: 50000
  max_context_length: 100000

logging:
  level: INFO
  file: ./logs/workpad.log

cors:
  enabled: true
  origins: "*"
```


***

## Structure du projet

```
workpad/
├── workpad/                    # Package Python
│   ├── __init__.py            # Exports principaux
│   ├── models.py              # Modèles Pydantic
│   ├── enums.py               # EntryType, EntryStatus, ContextType
│   ├── storage/               # Abstraction storage
│   │   ├── __init__.py
│   │   ├── base.py            # Interface abstraite
│   │   ├── json_storage.py    # Implémentation JSON
│   │   └── sqlite_storage.py  # Implémentation SQLite
│   ├── service.py             # Business logic (CRUD operations)
│   ├── api/                   # API REST
│   │   ├── __init__.py
│   │   ├── routes.py          # Flask routes
│   │   ├── schemas.py         # Request/Response schemas
│   │   └── errors.py          # Error handlers
│   ├── config.py              # Configuration management
│   └── utils.py               # Helpers (UUID, datetime, etc.)
├── tests/                     # Tests
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_storage.py
│   ├── test_service.py
│   ├── test_api.py
│   └── fixtures.py
├── examples/                  # Exemples d'utilisation
│   ├── basic_usage.py
│   ├── research_notes.py
│   └── task_tracking.py
├── docs/                      # Documentation
│   ├── API.md
│   ├── STORAGE.md
│   └── EXAMPLES.md
├── Dockerfile                 # Image Docker
├── docker-compose.yml         # Standalone testing
├── requirements.txt           # Dépendances production
├── requirements-dev.txt       # Dépendances dev/test
├── setup.py                   # Package setup
├── pyproject.toml            # Modern Python packaging
├── .env.example              # Template env vars
├── .gitignore
├── LICENSE                    # MIT ou Apache 2.0
└── README.md                 # Documentation principale
```


***

## Logique métier (Service Layer)

### WorkpadService (classe principale)

```pseudocode
class WorkpadService:
    def __init__(storage: StorageInterface):
        self.storage = storage
    
    # CREATE
    def create_entry(data: EntryCreate) -> Entry:
        - Générer UUID
        - Créer timestamps
        - Valider avec Pydantic
        - Vérifier limites (max_entries)
        - Sauvegarder via storage
        - Retourner Entry
    
    # READ
    def get_entry(entry_id: str) -> Entry | None:
        - Récupérer via storage
        - Retourner Entry ou None
    
    def list_entries(filters: EntryFilter) -> list[Entry]:
        - Appliquer filtres (type, status, tags, dates)
        - Appliquer search si présent
        - Pagination (limit, offset)
        - Retourner liste
    
    def search_entries(query: str, limit: int) -> list[Entry]:
        - Full-text search dans content
        - Retourner résultats triés par pertinence
    
    def get_stats() -> dict:
        - Compter total
        - Grouper par type
        - Grouper par status
        - Date range (oldest, newest)
        - Retourner stats
    
    # UPDATE
    def update_entry(entry_id: str, data: EntryUpdate) -> Entry:
        - Récupérer entry existante
        - Si not found -> raise NotFoundError
        - Appliquer updates
        - Mettre à jour updated_at
        - Sauvegarder
        - Retourner Entry
    
    # DELETE
    def delete_entry(entry_id: str) -> bool:
        - Supprimer via storage
        - Si not found -> raise NotFoundError
        - Retourner True
    
    # CONTEXT
    def add_context(entry_id: str, context: ContextItemCreate) -> ContextItem:
        - Récupérer entry
        - Si not found -> raise NotFoundError
        - Créer ContextItem avec UUID
        - Ajouter à entry.context_items
        - Sauvegarder entry
        - Retourner ContextItem
    
    def remove_context(entry_id: str, context_id: str) -> bool:
        - Récupérer entry
        - Filtrer context_items pour retirer context_id
        - Sauvegarder entry
        - Retourner True
    
    # RELATIONS
    def add_relation(entry_id: str, related_id: str) -> bool:
        - Récupérer entry1 et entry2
        - Ajouter relation bidirectionnelle
        - Sauvegarder les deux
        - Retourner True
    
    def remove_relation(entry_id: str, related_id: str) -> bool:
        - Retirer relation bidirectionnelle
        - Sauvegarder
        - Retourner True
    
    # EXPORT
    def export_json(filters: EntryFilter) -> dict:
        - Lister entries avec filtres
        - Construire structure JSON
        - Ajouter metadata (exported_at, version)
        - Retourner dict
    
    def export_markdown(filters: EntryFilter) -> str:
        - Lister entries avec filtres
        - Grouper par type
        - Formater en Markdown
        - Retourner string
```


***

## Abstraction Storage

### Interface

```pseudocode
interface StorageInterface:
    def initialize() -> None
        # Setup storage (créer dossiers, tables, etc.)
    
    def create(entry: Entry) -> Entry
        # Persister une nouvelle entry
    
    def get(entry_id: str) -> Entry | None
        # Récupérer une entry
    
    def list(filters: EntryFilter) -> list[Entry]
        # Lister avec filtres
    
    def update(entry: Entry) -> Entry
        # Mettre à jour une entry
    
    def delete(entry_id: str) -> bool
        # Supprimer une entry
    
    def search(query: str, limit: int) -> list[Entry]
        # Full-text search
    
    def get_stats() -> dict
        # Statistiques
    
    def export_all() -> list[Entry]
        # Tout exporter (pour backup)
```


### JSONStorage

```pseudocode
class JSONStorage implements StorageInterface:
    def __init__(data_path: str):
        self.data_path = data_path
        self.entries_path = data_path / "entries"
        self.index_path = data_path / "metadata.json"
        self.index = {}  # Cache en mémoire
    
    def initialize():
        - Créer dossiers si nécessaire
        - Charger index depuis metadata.json
    
    def create(entry: Entry):
        - Déterminer dossier (entries/YYYY-MM/)
        - Écrire entry_{uuid}.json
        - Ajouter à index
        - Sauvegarder index
    
    def get(entry_id: str):
        - Chercher dans index
        - Charger fichier JSON
        - Parser en Entry
        - Retourner
    
    def list(filters: EntryFilter):
        - Parcourir index
        - Appliquer filtres
        - Charger entries matchantes
        - Pagination
        - Retourner
    
    def search(query: str, limit: int):
        - Parcourir tous les fichiers (ou index si content cached)
        - Chercher query dans content (case-insensitive)
        - Retourner matches
    
    # ... autres méthodes
```


### SQLiteStorage

```pseudocode
class SQLiteStorage implements StorageInterface:
    def __init__(db_path: str):
        self.db_path = db_path
        self.conn = None
    
    def initialize():
        - Créer connexion SQLite
        - Créer tables si nécessaire
        - Créer indexes
    
    def create(entry: Entry):
        - INSERT INTO entries
        - INSERT INTO context_items (bulk)
        - INSERT INTO entry_relations (bulk)
        - COMMIT
    
    def get(entry_id: str):
        - SELECT * FROM entries WHERE id = ?
        - JOIN avec context_items
        - JOIN avec entry_relations
        - Construire Entry
        - Retourner
    
    def list(filters: EntryFilter):
        - Construire query SQL dynamique
        - Appliquer WHERE clauses (type, status, tags, dates)
        - ORDER BY timestamp DESC
        - LIMIT/OFFSET
        - Exécuter query
        - Retourner
    
    def search(query: str, limit: int):
        - SELECT * FROM entries WHERE content LIKE '%query%'
        - LIMIT
        - Retourner
    
    # ... autres méthodes
```


***

## Gestion des erreurs

### Exceptions personnalisées

```pseudocode
class WorkpadError(Exception):
    # Base exception

class NotFoundError(WorkpadError):
    # Entry ou context not found

class ValidationError(WorkpadError):
    # Pydantic validation failed

class StorageError(WorkpadError):
    # Problème I/O ou DB

class LimitExceededError(WorkpadError):
    # Max entries ou content length dépassé
```


### Format de réponse d'erreur

```json
{
  "error": "Entry not found",
  "code": 404,
  "details": {
    "entry_id": "uuid-here"
  }
}
```


### Error handlers Flask

```pseudocode
@app.errorhandler(NotFoundError):
    return jsonify(error=str(e), code=404), 404

@app.errorhandler(ValidationError):
    return jsonify(error=str(e), code=400), 400

@app.errorhandler(LimitExceededError):
    return jsonify(error=str(e), code=413), 413

@app.errorhandler(Exception):
    log error
    return jsonify(error="Internal server error", code=500), 500
```


***

## Tests

### Structure des tests

```
tests/
├── test_models.py          # Test Pydantic models
├── test_storage.py         # Test storage implementations
├── test_service.py         # Test business logic
├── test_api.py            # Test API endpoints
└── fixtures.py            # Shared fixtures
```


### Coverage attendue

- **Modèles** : 100% (simple validation)
- **Storage** : 95%+ (tous les cas nominaux + erreurs)
- **Service** : 95%+ (logique métier complète)
- **API** : 90%+ (tous les endpoints + error cases)


### Tests à implémenter

#### test_models.py

```pseudocode
def test_entry_creation():
    # Créer Entry valide
    # Vérifier tous les champs
    # Vérifier defaults (status=active, etc.)

def test_entry_validation():
    # Content trop long -> ValidationError
    # Type invalide -> ValidationError
    # Tags trop nombreux -> ValidationError

def test_context_item_creation():
    # Créer ContextItem valide
    # Vérifier champs

def test_enums():
    # Vérifier toutes les valeurs d'enum
```


#### test_storage.py

```pseudocode
def test_json_storage_initialize():
    # Créer storage
    # Vérifier création dossiers

def test_json_storage_create():
    # Créer entry
    # Vérifier fichier existe
    # Vérifier index mis à jour

def test_json_storage_get():
    # Créer entry
    # Récupérer par ID
    # Vérifier égalité

def test_json_storage_list_with_filters():
    # Créer plusieurs entries
    # Filtrer par type
    # Filtrer par status
    # Filtrer par date
    # Vérifier résultats

def test_json_storage_search():
    # Créer entries avec contenu spécifique
    # Chercher query
    # Vérifier résultats

# Mêmes tests pour SQLiteStorage
```


#### test_service.py

```pseudocode
def test_create_entry():
    # Créer entry via service
    # Vérifier UUID généré
    # Vérifier timestamps

def test_get_entry_not_found():
    # Chercher UUID inexistant
    # Vérifier NotFoundError

def test_update_entry():
    # Créer entry
    # Update content
    # Vérifier updated_at changé

def test_delete_entry():
    # Créer entry
    # Supprimer
    # Vérifier not found après

def test_add_context():
    # Créer entry
    # Ajouter context
    # Vérifier context dans entry

def test_add_relation():
    # Créer 2 entries
    # Lier
    # Vérifier relation bidirectionnelle

def test_export_json():
    # Créer entries
    # Exporter
    # Vérifier structure JSON

def test_export_markdown():
    # Créer entries
    # Exporter
    # Vérifier format Markdown
```


#### test_api.py

```pseudocode
def test_post_entries():
    # POST /entries
    # Vérifier 201 Created
    # Vérifier response body

def test_get_entries():
    # GET /entries
    # Vérifier 200 OK
    # Vérifier structure pagination

def test_get_entry_by_id():
    # Créer entry
    # GET /entries/{id}
    # Vérifier 200 OK

def test_get_entry_not_found():
    # GET /entries/invalid-uuid
    # Vérifier 404

def test_put_entry():
    # Créer entry
    # PUT /entries/{id}
    # Vérifier 200 OK
    # Vérifier update

def test_delete_entry():
    # Créer entry
    # DELETE /entries/{id}
    # Vérifier 204 No Content

def test_post_context():
    # Créer entry
    # POST /entries/{id}/context
    # Vérifier 201 Created

def test_get_stats():
    # Créer entries variées
    # GET /entries/stats
    # Vérifier counts

def test_export_json():
    # GET /entries/export?format=json
    # Vérifier Content-Type
    # Vérifier Content-Disposition

def test_search():
    # GET /entries/search?q=test
    # Vérifier résultats

def test_health():
    # GET /health
    # Vérifier 200 OK
```


***

## Docker

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Dépendances système (si nécessaire)
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code
COPY workpad/ ./workpad/
COPY setup.py .
COPY pyproject.toml .

# Install package
RUN pip install -e .

# Volume pour données persistantes
VOLUME /data

# Port
EXPOSE 5001

# Environment
ENV WORKPAD_HOST=0.0.0.0
ENV WORKPAD_PORT=5001
ENV WORKPAD_STORAGE_PATH=/data

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
  CMD curl -f http://localhost:5001/health || exit 1

# Run
CMD ["python", "-m", "workpad"]
```


### docker-compose.yml

```yaml
version: '3.8'

services:
  workpad:
    build: .
    container_name: workpad
    ports:
      - "5001:5001"
    volumes:
      - ./data:/data
      - ./logs:/app/logs
    environment:
      - WORKPAD_HOST=0.0.0.0
      - WORKPAD_PORT=5001
      - WORKPAD_STORAGE_TYPE=json
      - WORKPAD_STORAGE_PATH=/data
      - WORKPAD_LOG_LEVEL=INFO
      - WORKPAD_CORS_ENABLED=true
    restart: unless-stopped
    mem_limit: 100m
    cpus: 0.5
```


***

## Documentation à fournir

### README.md

Structure :

```markdown
# Workpad

Generic note/entry management system with timestamps, types, context, and status tracking.

## Features
- CRUD operations for entries
- Flexible context items (code, files, logs, etc.)
- Entry relations and tagging
- Full-text search
- JSON and Markdown export
- RESTful API
- Docker support

## Quick Start
[Installation, usage examples]

## API Documentation
[Link to Swagger/OpenAPI]

## Configuration
[Environment variables]

## Use Cases
- Research notes
- Task tracking
- Investigation logs
- Lab notebooks

## License
MIT
```


### API.md

- Documentation complète de tous les endpoints
- Exemples de requêtes/réponses avec curl
- Codes d'erreur possibles
- Schemas Pydantic


### STORAGE.md

- Explication des deux backends
- Quand utiliser JSON vs SQLite
- Comment migrer entre les deux
- Backup et restore


### EXAMPLES.md

- Exemples d'utilisation pour différents cas :
    - Research notes scientifiques
    - Task tracking
    - Investigation logs
    - Lab notebook

***

## Points MCP-Ready

✅ **Pydantic models** : Tous les inputs/outputs
✅ **Type annotations** : Partout
✅ **RESTful conventions** : Verbes HTTP standards, URLs ressources
✅ **JSON responses** : Partout, avec Pydantic serialization
✅ **Error format standard** : `{"error": "...", "code": 404}`
✅ **Docstrings** : Sur chaque route
✅ **OpenAPI/Swagger** : Auto-généré
✅ **HTTP status codes** : Corrects (200, 201, 204, 400, 404, 500)

Le service est **100% wrappable** par `py-mcp-wrapper` sans aucune modification.

***

## Checklist d'implémentation

### Phase 1 : Fondations (Semaine 1)

- [ ] Setup projet (structure, git, requirements)
- [ ] Modèles Pydantic (Entry, ContextItem, schemas)
- [ ] Enums (EntryType, EntryStatus, ContextType)
- [ ] Interface StorageInterface
- [ ] JSONStorage implémentation basique
- [ ] Tests modèles
- [ ] Tests JSONStorage


### Phase 2 : Service Layer (Semaine 1)

- [ ] WorkpadService class
- [ ] CRUD operations (create, get, list, update, delete)
- [ ] Context management
- [ ] Relations
- [ ] Tests service complets


### Phase 3 : API REST (Semaine 2)

- [ ] Flask setup
- [ ] Routes principales (CRUD)
- [ ] Routes context
- [ ] Routes stats/export/search
- [ ] Error handlers
- [ ] Tests API complets


### Phase 4 : Storage SQLite (Semaine 2)

- [ ] SQLiteStorage implémentation
- [ ] Migrations
- [ ] Tests SQLiteStorage


### Phase 5 : Configuration \& Déploiement (Semaine 2)

- [ ] Configuration (env vars, YAML)
- [ ] Logging
- [ ] CORS support
- [ ] Dockerfile
- [ ] docker-compose.yml
- [ ] Documentation complète (README, API, STORAGE, EXAMPLES)


### Phase 6 : Polish (Semaine 3)

- [ ] OpenAPI/Swagger auto-docs
- [ ] Exemples d'utilisation
- [ ] CI/CD (GitHub Actions)
- [ ] PyPI packaging (setup.py, pyproject.toml)
- [ ] Release 1.0.0

***

## Métriques de succès

Le service est **prêt** quand :

✅ Tous les tests passent (coverage >90%)
✅ Documentation complète
✅ Docker fonctionne standalone
✅ API testée avec curl/Postman
✅ Export JSON/Markdown fonctionnel
✅ Peut gérer 1000+ entries sans problème
✅ Mémoire <80 MB en usage normal
✅ MCP-wrappable (vérifié avec py-mcp-wrapper)
✅ Réutilisable hors Mindpad (domain-agnostic)

***

## Prochaines étapes après Workpad

1. **py-mindpad-core** : Créer la lib partagée qui importe les modèles de Workpad
2. **py-llm-gateway** : Service suivant (dépendance critique)
3. **Intégration Mindpad** : Workpad devient une dépendance dans `mindpad-app`

***

**Document complet. Prêt pour implémentation par coding agent.** 🚀

