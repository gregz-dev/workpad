# Workpad

Workpad is a generic note/entry management system designed to be lightweight, domain-agnostic, and easily integrated into other tools.

## Features

- **Typed Entries**: Support for observations, hypotheses, tests, tasks, etc.
- **Context Awareness**: Attach code snippets, files, logs to your entries.
- **Storage**: JSON file-based storage (easy to backup and read).
- **Validation**: Strict data validation using Pydantic.

## Installation

```bash
pip install -e .
```

## Usage

Currently, you can use the Python API to interact with the storage layer.

```python
from workpad.models import Entry, EntryType
from workpad.storage.json_storage import JSONStorage

storage = JSONStorage("./data")
storage.initialize()

entry = storage.create(Entry(
    type=EntryType.note,
    content="Hello World"
))
```

## Development

Run tests:

```bash
pip install -e .[dev]
pytest
```

## Documentation

See [doc/](doc/) for detailed documentation.
- [Foundation Layer](doc/FOUNDATION_LAYER.md): Data models and storage architecture.