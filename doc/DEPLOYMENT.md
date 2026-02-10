# Deployment Guide

Workpad is designed to be deployed as a Docker container or a standard Python application.

## Configuration

Configuration is handled via environment variables and/or a `config.yaml` file.

| Variable | Description | Default |
|---|---|---|
| `WORKPAD_DATA_PATH` | Path to data directory | `./data` |
| `WORKPAD_STORAGE_TYPE` | Storage backend (`json` or `sqlite`) | `json` |
| `WORKPAD_LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | `INFO` |
| `WORKPAD_CORS_ORIGINS` | Allowed CORS origins (comma separated or *) | `*` |

### config.yaml Example

```yaml
data_path: /var/lib/workpad
storage_type: sqlite
log_level: WARNING
cors_origins: https://myapp.com
```

## Docker Deployment

### Build

```bash
docker build -t workpad .
```

### Run with Docker Compose

```yaml
version: '3.8'
services:
  workpad:
    image: workpad
    ports:
      - "5000:5000"
    volumes:
      - ./workpad-data:/data
    environment:
      - WORKPAD_STORAGE_TYPE=sqlite
```

```bash
docker-compose up -d
```

## Manual Deployment

1.  Install dependencies:
    ```bash
    pip install .
    ```
2.  Run with Gunicorn (production):
    ```bash
    gunicorn -w 4 -b 0.0.0.0:5000 "workpad.api:create_app()"
    ```
