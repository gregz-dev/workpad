# Mindpad Architecture: Microservices-as-Libraries Strategy

**Date**: February 10, 2026  
**Context**: This document defines the complete architecture for Mindpad project, designed to work with AI coding assistants (like Copilot) that struggle with large monolithic codebases.

---

## Core Philosophy

### The Problem
AI coding assistants cannot effectively handle large monolithic projects - they only work well with small, focused codebases.

### The Solution
**Microservices-as-Libraries Architecture**:
- Each service = 1 independent Git repository
- Each service = 1 reusable Python library + Docker container
- Services are **domain-agnostic** and reusable across projects
- Final application assembles libraries with flexible deployment modes

### Deployment Flexibility
The architecture supports 3 modes:
1. **Monolith** (~800 MB RAM): All libraries in 1 process (dev, small projects)
2. **Microservices** (~2 GB RAM): Each service as separate Docker container (production, scalability)
3. **Hybrid** (~1.2-1.5 GB RAM): Heavy services isolated, light services grouped (optimal)

---

## Complete Service List

Based on the full implementation plan, Mindpad consists of **10 core services**:

### 1. Scratchpad Service
**Repo**: `py-scratchpad`  
**Port**: 5001  
**Purpose**: Generic note/entry management system with timestamps, types, and context  
**Reusability**: Lab notebooks, project logs, research notes, task tracking  
**Key Features**:
- CRUD operations for entries (observation, hypothesis, test, next_step)
- Entry status management (active, tested, invalidated, confirmed)
- Context items (code snippets, files, stacktraces, logs, URLs)
- Markdown/JSON export
- Statistics and filtering

**Tech Stack**: Flask, Pydantic, SQLite/JSON storage  
**Memory**: ~50 MB  
**Dependencies**: Lightweight

---

### 2. LLM Gateway Service
**Repo**: `py-llm-gateway`  
**Port**: 5002  
**Purpose**: Unified gateway to multiple LLM providers with routing, fallback, and retry logic  
**Reusability**: Any app needing multi-provider LLM access, A/B testing, cost optimization  
**Key Features**:
- Multi-provider support: GitHub Copilot, OpenRouter, Ollama, llama.cpp
- Automatic fallback chain
- OpenAI-compatible API
- Rate limiting and retry logic
- Model selection per request
- Streaming support

**Tech Stack**: Flask, github-copilot-sdk, httpx, ollama  
**Memory**: ~80 MB  
**Dependencies**: Medium (SDK integrations)

---

### 3. Agent Service
**Repo**: `py-agent-framework`  
**Port**: 5003  
**Purpose**: Specialized AI agent orchestration framework  
**Reusability**: Customer support bots, code review, research assistants, QA systems  
**Key Features**:
- **Scribe Agent**: Structure user input into proper entries
- **Analyst Agent**: Find patterns, correlations, contradictions
- **Critic Agent**: Challenge hypotheses, identify assumptions
- **Rubber Duck Agent**: Socratic questioning for clarity
- **Synthesizer Agent**: Summarize progress, consolidate findings
- Agent coordination and routing logic

**Tech Stack**: Flask, Pydantic, httpx (calls LLM Gateway)  
**Memory**: ~60 MB  
**Dependencies**: Depends on LLM Gateway

---

### 4. Voice Service
**Repo**: `py-voice-transcription`  
**Port**: 5004  
**Purpose**: Local speech-to-text using Whisper (offline processing)  
**Reusability**: Voice notes, meeting transcription, podcasts, accessibility, voice commands  
**Key Features**:
- Multiple audio format support (webm, wav, mp3, ogg, m4a)
- Whisper model selection (tiny: 75MB, base: 150MB, small: 500MB)
- Streaming transcription for long audio
- Language detection/selection
- GPU acceleration support
- Model management (download, switch)

**Tech Stack**: Flask, whisper.cpp, ffmpeg, numpy  
**Memory**: ~200-600 MB (depending on model)  
**Dependencies**: Heavy (Whisper model + ffmpeg)

---

### 5. Knowledge Graph Service
**Repo**: `py-knowledge-graph`  
**Port**: 5005  
**Purpose**: Document indexing, embedding generation, and RAG queries  
**Reusability**: Documentation search, code search, research papers, customer support KB  
**Key Features**:
- Document ingestion (PDF, HTML, Markdown, logs, code, text)
- Chunking with configurable size/overlap
- Embedding generation (sentence-transformers)
- ChromaDB vector storage
- RAG (Retrieval Augmented Generation) queries
- Semantic search with similarity threshold
- Document metadata and filtering

**Tech Stack**: Flask, ChromaDB, sentence-transformers, pypdf, BeautifulSoup4  
**Memory**: ~400-800 MB (ChromaDB + embeddings model)  
**Dependencies**: Very heavy (vector DB + ML models)

---

### 6. Git Integration Service
**Repo**: `py-git-analyzer`  
**Port**: 5006  
**Purpose**: Git repository analysis and history exploration  
**Reusability**: Code archaeology, blame analysis, bisect automation, change tracking  
**Key Features**:
- Git blame analysis with context
- Diff analysis between commits/branches
- Automated git bisect assistant
- Commit message search
- Branch comparison
- File history tracking
- Link commits to code changes

**Tech Stack**: Flask, GitPython  
**Memory**: ~60 MB  
**Dependencies**: Light (GitPython)

---

### 7. Code Analysis Service
**Repo**: `py-code-analyzer`  
**Port**: 5007  
**Purpose**: Static code analysis using tree-sitter  
**Reusability**: Code understanding, refactoring tools, dependency mapping, dead code detection  
**Key Features**:
- Call graph generation
- Data flow tracing
- Symbol extraction (classes, functions, variables)
- Dependency analysis (imports, circular deps)
- Dead code detection
- Multi-language support (Python, C/C++, JS/TS via tree-sitter)

**Tech Stack**: Flask, tree-sitter, language parsers  
**Memory**: ~100 MB  
**Dependencies**: Medium (tree-sitter + parsers)

---

### 8. Export Engine Service
**Repo**: `py-export-engine`  
**Port**: 5008  
**Purpose**: Multi-format template-based export system  
**Reusability**: Report generation, documentation, post-mortems, bug reports  
**Key Features**:
- Jinja2 template engine
- Multiple export formats (Markdown, HTML, PDF, JSON)
- Configurable templates (colleague, management, bug tracker, docs)
- Section selection and filtering
- Export preview
- Custom template support
- HTML/PDF conversion (weasyprint)

**Tech Stack**: Flask, Jinja2, weasyprint/pdfkit  
**Memory**: ~80 MB  
**Dependencies**: Medium (PDF generation)

---

### 9. Document Ingestion Service
**Repo**: `py-doc-ingestor`  
**Port**: 5009  
**Purpose**: Multi-format document parsing and preprocessing pipeline  
**Reusability**: Content extraction, ETL pipelines, document processing  
**Key Features**:
- PDF text extraction (pypdf)
- PowerPoint parsing (python-pptx)
- HTML cleaning and extraction (BeautifulSoup4)
- Markdown parsing
- Log file parsing with structure detection
- Code file processing
- Metadata extraction
- Automatic chunking for embeddings

**Tech Stack**: Flask, pypdf, python-pptx, BeautifulSoup4  
**Memory**: ~70 MB  
**Dependencies**: Medium (parsing libraries)

---

### 10. File Watcher Service
**Repo**: `py-file-watcher`  
**Port**: 5010  
**Purpose**: Automated file monitoring with configurable ingestion rules  
**Reusability**: Auto-sync, live updates, monitoring systems, ETL triggers  
**Key Features**:
- Multi-directory watching
- Include/exclude patterns (glob, regex)
- Event detection (created, modified, deleted)
- Auto-ingestion rules per directory
- Metadata tagging
- Integration with Knowledge Graph or Scratchpad
- Configurable max watchers

**Tech Stack**: Flask, watchdog  
**Memory**: ~50 MB  
**Dependencies**: Light (watchdog)

---

## Shared Core Library

**Repo**: `py-mindpad-core`  
**Purpose**: Common types, models, and utilities shared across all services  
**Contains**:
- Data models (Entry, ContextItem, Document, etc.)
- Pydantic schemas for validation
- Common utilities (UUID generation, timestamps)
- Configuration helpers
- Error types

**Memory**: Negligible (imported by all services)  
**Dependencies**: Pydantic, typing extensions

---

## Repository Structure

Each service repository follows this structure:

```
py-service-name/
├── service_name/           # Python package
│   ├── __init__.py        # Exports Service class
│   ├── service.py         # Core business logic
│   ├── models.py          # Pydantic models
│   ├── api/
│   │   ├── routes.py      # Flask API endpoints
│   │   └── schemas.py     # Request/response schemas
│   └── config.py          # Configuration
├── Dockerfile             # Standalone Docker image
├── docker-compose.yml     # For isolated testing
├── requirements.txt       # Python dependencies
├── tests/                 # Unit tests
├── README.md              # Usage documentation
└── setup.py               # Package setup for pip install
```

---

## Final Application Repository

**Repo**: `mindpad-app`  
**Purpose**: Assemble all services into Mindpad application  

**Structure**:
```
mindpad-app/
├── requirements.txt       # Lists all py-* services as dependencies
├── config.yaml           # Deployment mode configuration
├── main.py               # Application entrypoint
├── docker-compose.yml    # Multi-container orchestration
├── deploy/
│   ├── monolith/         # Single container deployment
│   ├── microservices/    # Full microservices deployment
│   └── hybrid/           # Hybrid deployment (3-4 containers)
└── docs/                 # Application-specific docs
```

**requirements.txt**:
```
py-mindpad-core @ git+https://github.com/you/py-mindpad-core
py-scratchpad @ git+https://github.com/you/py-scratchpad
py-llm-gateway @ git+https://github.com/you/py-llm-gateway
py-agent-framework @ git+https://github.com/you/py-agent-framework
py-voice-transcription @ git+https://github.com/you/py-voice-transcription
py-knowledge-graph @ git+https://github.com/you/py-knowledge-graph
py-git-analyzer @ git+https://github.com/you/py-git-analyzer
py-code-analyzer @ git+https://github.com/you/py-code-analyzer
py-export-engine @ git+https://github.com/you/py-export-engine
py-doc-ingestor @ git+https://github.com/you/py-doc-ingestor
py-file-watcher @ git+https://github.com/you/py-file-watcher
```

---

Voici l'encadré **MCP-Ready Guidelines** à ajouter dans le document d'architecture :

***

## 📦 MCP-Ready Guidelines

### Why This Matters

Each service in this architecture can optionally be exposed via the **Model Context Protocol (MCP)** through a generic wrapper (`py-mcp-wrapper`). The wrapper automatically introspects Flask APIs and generates MCP tools without modifying service code.

**To enable automatic wrapping, services must follow these guidelines:**

### ✅ Required Best Practices

1. **Use Pydantic models for all inputs/outputs**
   - Enables automatic JSON schema generation
   - Provides type validation
   - Example: `def create_entry(data: EntryCreate) -> Entry:`

2. **Add type annotations to all route handlers**
   - Wrapper uses these for introspection
   - Enables automatic schema extraction
   - Example: `def list_entries() -> list[Entry]:`

3. **Follow RESTful conventions**
   - Use standard HTTP methods: GET, POST, PUT, DELETE
   - Use resource-based URLs: `/entries`, not `/get_all_entries_v2`
   - Use path parameters: `/entries/{id}`, not `/entries?id=123`

4. **Return consistent JSON responses**
   - All endpoints return JSON (not mixed text/JSON)
   - Use Pydantic models for response serialization
   - Example: `return jsonify(entry.dict())`

5. **Use standard error format**
   - Consistent error structure: `{"error": "message", "code": 400}`
   - HTTP status codes match error severity
   - Example: `return jsonify({"error": "Not found", "code": 404}), 404`

### ✅ Highly Recommended

6. **Add docstrings to route handlers**
   - Becomes MCP tool descriptions automatically
   - Helps users understand tool purpose
   - Example:
     ```python
     @app.post("/entries")
     def create_entry(data: EntryCreate) -> Entry:
         """Create a new scratchpad entry (observation, hypothesis, test, next_step)"""
         ...
     ```

7. **Enable OpenAPI/Swagger documentation**
   - Alternative to runtime introspection
   - Better performance for wrapper startup
   - Useful for API documentation anyway

8. **Use consistent naming conventions**
   - Clear, descriptive endpoint names
   - Avoid versioning in URLs (use headers)
   - Example: `/entries`, not `/v2/get_entries_new`

9. **Use HTTP status codes correctly**
   - 200: Success
   - 201: Created
   - 400: Bad request
   - 404: Not found
   - 500: Server error

### ❌ Not Required (Service Stays MCP-Agnostic)

- ❌ No MCP SDK imports needed
- ❌ No MCP-specific code in services
- ❌ No special decorators or middleware
- ❌ No awareness of MCP protocol

### Example: MCP-Ready Service

```python
from flask import Flask
from pydantic import BaseModel

app = Flask(__name__)

class Item(BaseModel):
    name: str
    value: int

@app.post("/items")
def create_item(data: Item) -> Item:
    """Create a new item"""
    # Business logic here
    return Item(name=data.name, value=data.value)

@app.get("/items")
def list_items() -> list[Item]:
    """List all items"""
    return [Item(name="test", value=42)]

@app.get("/items/{id}")
def get_item(id: str) -> Item:
    """Get item by ID"""
    # If not found:
    # return jsonify({"error": "Item not found", "code": 404}), 404
    return Item(name="test", value=42)
```

**This service is fully MCP-wrappable with zero changes** - just add a 10-line YAML config.

### Impact on Development

Following these guidelines has **zero negative impact**:
- ✅ These are standard REST API best practices anyway
- ✅ Improves testability, documentation, and maintainability
- ✅ Makes services easier to integrate with any client (not just MCP)
- ✅ No MCP coupling - services work standalone forever

### Reference Documentation

See **MCP_WRAPPER_STRATEGY.md** for complete details on:
- How the wrapper works
- Configuration examples
- Deployment modes
- Advanced features

***

**À insérer dans ARCHITECTURE_MICROSERVICES_AS_LIBRARIES.md** après la section "Technical Stack Summary" et avant "Next Steps".

---

## Deployment Modes

### 1. Monolith Mode (~800 MB RAM)

**Use Case**: Development, small projects, single-user  
**Architecture**: All services imported as libraries in 1 Python process  

```python
# main.py
from scratchpad import ScratchpadService
from llm_gateway import LLMGateway
from agent_framework import AgentOrchestrator
from voice_transcription import VoiceService
from knowledge_graph import KnowledgeGraphService
# ... import all

class MindpadApp:
    def __init__(self):
        self.scratchpad = ScratchpadService("/data/scratchpad")
        self.llm = LLMGateway()
        self.agents = AgentOrchestrator(self.llm)
        self.voice = VoiceService(model="tiny")
        self.knowledge = KnowledgeGraphService("/data/chroma")
        # All in shared memory!
```

**Memory Breakdown**:
- 1 Python runtime: ~30 MB
- Flask + shared deps: ~50 MB
- Whisper model (tiny): ~75 MB
- Sentence-transformers: ~200-300 MB
- ChromaDB: ~200-300 MB
- Other services: ~100 MB
- **Total**: ~700-800 MB

---

### 2. Microservices Mode (~2 GB RAM)

**Use Case**: Production, high load, scalability, team development  
**Architecture**: Each service as separate Docker container  

**docker-compose.yml**:
```yaml
services:
  scratchpad:
    image: py-scratchpad:latest
    ports: ["5001:5001"]
    mem_limit: 100m

  llm-gateway:
    image: py-llm-gateway:latest
    ports: ["5002:5002"]
    mem_limit: 150m

  agents:
    image: py-agent-framework:latest
    ports: ["5003:5003"]
    depends_on: [llm-gateway]
    mem_limit: 100m

  voice:
    image: py-voice-transcription:latest
    ports: ["5004:5004"]
    mem_limit: 600m  # Heavy: Whisper model

  knowledge-graph:
    image: py-knowledge-graph:latest
    ports: ["5005:5005"]
    volumes: ["./data/chroma:/data/chroma"]
    mem_limit: 800m  # Heavy: ChromaDB + embeddings

  # ... other services
```

**Memory Breakdown**:
- 10 Python runtimes: 10 × 30 MB = 300 MB
- Flask per service: 10 × 24 MB = 240 MB
- Voice service (heavy): ~600 MB
- Knowledge Graph (heavy): ~800 MB
- Other services: ~400 MB
- **Total**: ~1,750-2,200 MB

---

### 3. Hybrid Mode (~1.2-1.5 GB RAM) ⭐ RECOMMENDED

**Use Case**: Optimal balance of memory and scalability  
**Architecture**: Heavy services isolated, light services grouped  

**Strategy**:
- **Container 1** (Light services): Scratchpad + LLM Gateway + Agents + Export + File Watcher (~200 MB)
- **Container 2** (Voice): Isolated Whisper service (~600 MB)
- **Container 3** (Knowledge Graph): Isolated vector DB service (~800 MB)
- **Container 4** (Code Analysis + Git): Medium services grouped (~150 MB)

**Benefits**:
- Memory: ~1,200-1,500 MB (vs 2 GB full microservices)
- Scalability: Heavy services can scale independently
- Simplicity: Only 3-4 containers to manage

---

## Memory Optimization Strategies

### 1. Lazy Loading
Load heavy models only on first request:
- Whisper model: Load on first transcription
- Embeddings model: Load on first document ingestion
- Tree-sitter parsers: Load on first code analysis

### 2. Docker Image Optimization
- Use Alpine Linux base images (~50 MB vs ~100 MB)
- Multi-stage builds to reduce image size
- Shared volume for models (avoid duplicating 500MB Whisper model)

### 3. Memory Limits
Set Docker memory limits per service:
```yaml
mem_limit: 100m  # Scratchpad, File Watcher
mem_limit: 200m  # LLM Gateway, Agents
mem_limit: 600m  # Voice Service
mem_limit: 800m  # Knowledge Graph
```

### 4. Model Selection
Configure models based on requirements:
- **Whisper**: tiny (75MB) for dev, base (150MB) for production
- **Embeddings**: all-MiniLM-L6-v2 (80MB) default, larger models optional
- **LLM Provider**: Use local Ollama for cost, Copilot for quality

---

## Development Workflow

### Phase 1: Develop Each Service Independently
1. Create new repo for service (e.g., `py-scratchpad`)
2. Develop service with AI assistant (small codebase = works well)
3. Write unit tests within service repo
4. Create Dockerfile for isolated testing
5. Publish to Git with version tag (e.g., v0.1.0)

### Phase 2: Integration Testing
1. Create test app that imports 2-3 services
2. Test inter-service communication
3. Validate API contracts
4. Fix integration issues in respective repos

### Phase 3: Full Assembly
1. Update `mindpad-app/requirements.txt` with all services
2. Configure deployment mode (monolith/microservices/hybrid)
3. Run integration tests
4. Deploy

### Phase 4: Incremental Updates
1. Update specific service in its repo
2. Tag new version (e.g., v0.2.0)
3. Update version in `mindpad-app/requirements.txt`
4. Redeploy only affected containers (microservices) or full app (monolith)

---

## Dependency Management

### Version Pinning
```
# mindpad-app/requirements.txt
py-mindpad-core @ git+https://github.com/you/py-mindpad-core@v0.2.0
py-scratchpad @ git+https://github.com/you/py-scratchpad@v0.3.1
```

### Inter-Service Dependencies
- Services call each other via HTTP APIs (loose coupling)
- Shared models via `py-mindpad-core` package
- No circular dependencies (DAG structure)

### Dependency Graph
```
py-mindpad-core
  ├─ py-scratchpad
  ├─ py-llm-gateway
  ├─ py-agent-framework (depends on LLM Gateway API)
  ├─ py-voice-transcription
  ├─ py-knowledge-graph
  ├─ py-git-analyzer
  ├─ py-code-analyzer
  ├─ py-export-engine (uses Scratchpad API, Knowledge Graph API)
  ├─ py-doc-ingestor (feeds Knowledge Graph API)
  └─ py-file-watcher (feeds Knowledge Graph/Scratchpad APIs)
```

---

## Advantages of This Architecture

### For AI Coding Assistants
✅ Each repo = small, focused codebase (AI can handle)  
✅ Clear boundaries and single responsibility  
✅ Incremental development service by service  
✅ Easy to understand and maintain context  

### For Development
✅ Parallel development (different services by different people/agents)  
✅ Independent versioning and releases  
✅ Clear API contracts between services  
✅ Reusable components across projects  

### For Deployment
✅ Flexible: monolith OR microservices OR hybrid  
✅ Start simple (monolith), scale later (microservices)  
✅ Memory-efficient hybrid mode available  
✅ Docker isolation for testing  

### For Maintenance
✅ Update one service without touching others  
✅ Easy to add new services  
✅ Clear error boundaries  
✅ Independent testing per service  

---

## Disadvantages & Tradeoffs

### Complexity
❌ 11 repos to manage vs 1 monorepo  
❌ Version coordination across repos  
❌ More complex CI/CD setup  

### Network Overhead
❌ Inter-service HTTP calls (vs in-process)  
❌ Serialization/deserialization overhead  
❌ Potential latency (mitigated in monolith mode)  

### Debugging
❌ Distributed tracing needed (microservices mode)  
❌ Harder to debug cross-service issues  

**Mitigation**: Use monolith mode for development, microservices for production

---

## Service Design Principles

### 1. Domain-Agnostic
Each service should be reusable beyond Mindpad:
- ✅ `py-scratchpad` → generic note system
- ✅ `py-llm-gateway` → any LLM integration
- ❌ `mindpad-scratchpad` → too specific

### 2. Single Responsibility
Each service does one thing well:
- ✅ Voice service = transcription only
- ❌ Voice service + sentiment analysis = too much

### 3. Loose Coupling
Services communicate via HTTP APIs:
- ✅ Agents call LLM Gateway via REST API
- ❌ Agents import LLM Gateway directly

### 4. Self-Contained
Each service includes:
- Business logic
- API endpoints (Flask routes)
- Data models (Pydantic)
- Dockerfile for standalone use
- Unit tests
- Documentation

### 5. Configuration via Environment
```yaml
# Each service configures via env vars
PORT: 5001
STORAGE_PATH: /data
LOG_LEVEL: INFO
```

---

## Technical Stack Summary

| Component | Technology | Reason |
|-----------|-----------|--------|
| Web Framework | Flask | Lightweight, flexible |
| Validation | Pydantic | Type safety, auto-validation |
| Vector DB | ChromaDB | Easy, persistent, Python-native |
| Embeddings | sentence-transformers | Open-source, local |
| Voice | whisper.cpp | Fast, local, offline |
| LLM SDK | github-copilot-sdk | Official Copilot integration |
| Git | GitPython | Python-native Git operations |
| Parsing | tree-sitter | Multi-language, fast |
| Templates | Jinja2 | Standard, powerful |
| File Watch | watchdog | Cross-platform, reliable |
| Containerization | Docker | Standard, portable |

---

## Next Steps

### Immediate Actions
1. Create `py-mindpad-core` repo with shared models
2. Develop services in priority order:
   - py-scratchpad (foundation)
   - py-llm-gateway (critical dependency)
   - py-agent-framework (core feature)
   - py-voice-transcription (UX enhancement)
   - py-knowledge-graph (advanced feature)
   - Remaining services as needed

### Development Order
Follow Phase 1-15 from implementation plan, but:
- Each phase = 1-2 service repos completed
- Each service tested independently before integration
- Incremental assembly in `mindpad-app`

### Documentation Per Service
Each repo includes:
- README with usage examples
- API documentation (OpenAPI/Swagger)
- Configuration guide
- Docker deployment guide
- Reusability examples (non-Mindpad use cases)

---

## Conclusion

This **Microservices-as-Libraries** architecture solves the core problem: enabling AI coding assistants to build complex applications by working on small, focused codebases. Each service is independently developed, tested, and deployed, yet can be assembled into a monolithic app when memory efficiency is critical.

**Key Takeaway**: The architecture is not "microservices vs monolith" but "libraries with flexible deployment modes." This gives maximum flexibility while keeping development manageable for AI assistants.

---

**Document Version**: 1.0  
**Last Updated**: February 10, 2026  
**Maintained By**: Project context for AI coding sessions
