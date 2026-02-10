# Workpad

**Workpad** is a generic, modular note and entry management system designed as a microservice library. It allows you to store, manage, and retrieve text-based entries (notes, tasks, observations) with rich context and relations.

## Features

- **Store Anything**: Notes, Tasks, Logs, Ideas.
- **Context Aware**: Attach source context (URLs, file paths, snippets) to every entry.
- **Relational**: Link entries together to create a knowledge graph.
- **Flexible Storage**: 
  - **JSON Storage**: Simple, portable, text-based.
  - **SQLite Storage**: Robust, relational, SQL-queryable.
- **API First**: Full REST API for integration.
- **Container Ready**: Docker and Docker Compose support.

## Project Structure

```
workpad/
├── workpad/            # Source code
│   ├── api/            # REST API (Flask)
│   ├── storage/        # Storage backends (JSON, SQLite)
│   ├── models.py       # Pydantic domain models
│   ├── service.py      # Business logic
│   └── config.py       # Configuration
├── tests/              # Unit and Integration tests
├── doc/                # Detailed documentation
├── examples/           # Usage scripts
└── docker-compose.yml  # Deployment
```

## Installation

### Prerequisites

- Python 3.10+
- Docker (optional)

### Local Install

```bash
git clone https://github.com/workpad/workpad.git
cd workpad
pip install -e .
```

To install dev dependencies (testing, linting):
```bash
pip install -e .[dev]
```

## Configuration

Workpad is configured via environment variables or a `config.yaml` file.

| Variable | Default | Description |
|---|---|---|
| `WORKPAD_DATA_PATH` | `./data` | Directory to store data/db |
| `WORKPAD_STORAGE_TYPE` | `json` | Backend: `json` or `sqlite` |
| `WORKPAD_LOG_LEVEL` | `INFO` | Logging verbosity |

See [Deployment Guide](doc/DEPLOYMENT.md) for more details.

## Usage

### 1. As a Library

You can use Workpad directly in your Python applications.

```python
from workpad.storage.sqlite_storage import SQLiteStorage
from workpad.service import WorkpadService
from workpad.models import EntryCreate

# Init
storage = SQLiteStorage("./my_data")
storage.initialize()
service = WorkpadService(storage)

# Create
entry = service.create_entry(EntryCreate(content="Hello World"))
print(f"Created: {entry.id}")
```

See [examples/basic_usage.py](examples/basic_usage.py).

### 2. via REST API

Start the server:
```bash
flask --app workpad.api:create_app run
```

Or using Docker:
```bash
docker-compose up -d
```

Interact via HTTP:
```bash
curl -X POST http://localhost:5000/api/v1/entries \
  -H "Content-Type: application/json" \
  -d '{"type": "note", "content": "Hello from API"}'
```

See [API Documentation](doc/API_LAYER.md) and [examples/api_client.py](examples/api_client.py).

## Documentation

- [Architecture Overview](doc/ARCHITECTURE.md) (TODO)
- [Foundation Layer](doc/FOUNDATION_LAYER.md)
- [Service Layer](doc/SERVICE_LAYER.md)
- [API Layer](doc/API_LAYER.md)
- [SQLite Storage](doc/SQLITE_STORAGE.md)
- [Deployment](doc/DEPLOYMENT.md)

## Development

Running tests:
```bash
pytest
```

## License

MIT