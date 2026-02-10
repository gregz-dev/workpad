# MCP Wrapper Strategy: Universal Flask-to-MCP Bridge

**Date**: February 10, 2026  
**Context**: Strategy for exposing any Flask-based service as an MCP (Model Context Protocol) server through a generic, configurable wrapper.

---

## Executive Summary

The **py-mcp-wrapper** is a universal bridge that transforms any Flask REST API into an MCP server without modifying the service's code. This enables all 10 Mindpad services (and any other Flask service) to be instantly usable by MCP clients (Claude Desktop, VSCode, Zed, etc.) through simple YAML configuration.

**Key Principle**: Services remain pure HTTP APIs. MCP exposure is a deployment option, not a code requirement.

---

## The Problem

**Without Wrapper**:
- Each service needs custom MCP protocol implementation
- MCP logic mixed with business logic
- 10 services = 10x MCP boilerplate code
- Hard to maintain consistency across services
- Services become dependent on MCP SDK

**With Wrapper**:
- Services = standard Flask REST APIs
- 1 generic wrapper handles MCP protocol for all
- YAML config per service (< 50 lines)
- Services remain MCP-agnostic
- Can still be used as direct HTTP APIs

---

## Architecture Overview

```
MCP Client (Claude Desktop, VSCode, etc.)
    ↓ MCP Protocol (stdio/SSE)
py-mcp-wrapper (Generic, configurable)
    - Introspection
    - Schema Generation
    - Protocol Handler
    - HTTP Proxy
    ↓ HTTP REST
Flask Service (py-scratchpad, py-llm-gateway, etc.)
    - Business Logic
    - Pydantic Models
    - REST Endpoints
```

---

## How It Works

### 1. Introspection Phase (Startup)

**Wrapper analyzes Flask service**:
- Parse app.url_map to discover all routes
- Extract HTTP methods (GET, POST, PUT, DELETE)
- Identify path parameters (/entries/{id})
- Detect query parameters from route handlers
- Extract Pydantic models from route signatures
- Generate JSON schemas from Pydantic models
- Read docstrings for descriptions

**Output**: Complete API map

### 2. MCP Tool Generation

**For each route, wrapper creates MCP tool**:

```
Flask Route: POST /entries
Method Handler: create_entry(data: EntryCreate) -> Entry

Wrapper transforms to:

MCP Tool:
  name: create_entry
  description: Create a new scratchpad entry (from docstring)
  inputSchema: {EntryCreate JSON Schema from Pydantic}
  handler: proxy_to(POST, http://localhost:5001/entries)
```

### 3. Runtime Proxying

**When MCP client calls tool**:

```
1. MCP Client calls: create_entry({type: observation, content: Bug found})
2. Wrapper receives and validates against schema
3. Wrapper transforms to: POST http://localhost:5001/entries + JSON body
4. Flask service processes and returns JSON response
5. Wrapper transforms to MCP result format
6. MCP Client receives result
```

---

## Configuration System

### Service Configuration File

Each service has a mcp-config.yaml - see document for full examples.

Key sections:
- service: name, description, base_url
- auto_discover: true/false
- tools: route mappings and overrides
- resources: MCP resource URIs
- prompts: pre-defined prompt templates
- transforms: custom input/output transformations

---

## Deployment Modes

### Mode 1: One Wrapper per Service
Independent scaling, isolation. Each service gets dedicated MCP wrapper.

### Mode 2: Gateway (Multi-Service Wrapper)
Single MCP server for all services. Unified access point.

### Mode 3: SSE (Server-Sent Events)
Browser/web clients, network deployment via HTTP.

---

## Service Requirements for Auto-Wrapping

Services must follow these guidelines to be automatically wrappable:

### ✅ Required
1. **Pydantic models for all inputs/outputs**: Enables schema generation
2. **Type annotations on route handlers**: Wrapper uses for introspection
3. **RESTful routes**: Standard HTTP methods (GET/POST/PUT/DELETE)
4. **JSON responses**: Consistent format, not mixed text/JSON
5. **Standard error format**: {error: message, code: 400}

### ✅ Recommended
6. **Docstrings on routes**: Becomes MCP tool descriptions
7. **OpenAPI/Swagger enabled**: Alternative to runtime introspection
8. **Consistent naming**: /entries, not /get_all_entries_v2
9. **HTTP status codes**: Use correctly (200, 201, 400, 404, 500)

### ❌ Not Required
- No MCP SDK imports
- No MCP-specific code
- No special decorators or middleware

**Why This Matters**: Following these guidelines ensures the wrapper can automatically discover, understand, and expose your service as MCP tools without any manual configuration or code changes.

---

## Benefits

### For Service Developers
✅ Zero MCP code in services: Keep services pure HTTP APIs  
✅ Standard Flask patterns: No special conventions needed  
✅ Testable as HTTP: curl, Postman, pytest work normally  
✅ Framework agnostic: Works with Flask, FastAPI, Django  

### For MCP Users
✅ Instant MCP support: Config file = MCP ready  
✅ Consistent experience: All services feel uniform  
✅ Rich features: Resources, prompts, streaming all supported  
✅ Easy discovery: Auto-generated tool list  

### For Operations
✅ Centralized protocol handling: 1 wrapper to maintain  
✅ Flexible deployment: stdio, SSE, per-service, or gateway  
✅ Observable: Single point for logging, metrics  
✅ Secure: Auth, rate limiting at wrapper level  

---

## Wrapper Architecture

### Core Components

```
py-mcp-wrapper/
├── mcp_wrapper/
│   ├── introspector.py          # Flask route discovery
│   ├── schema_generator.py      # Pydantic → JSON Schema
│   ├── mcp_server.py            # MCP protocol implementation
│   ├── proxy.py                 # HTTP client to services
│   ├── config_loader.py         # YAML config parsing
│   ├── transformers.py          # Custom input/output transforms
│   ├── cache.py                 # Response caching
│   ├── auth.py                  # Auth handling
│   └── streaming.py             # SSE/streaming support
├── configs/                     # Per-service configs
├── tests/
├── Dockerfile
└── README.md
```

---

## Comparison: Wrapper vs Native MCP

| Aspect | Native MCP in Service | Generic Wrapper |
|--------|----------------------|-----------------|
| Code changes | High (MCP SDK everywhere) | Zero (config only) |
| Maintenance | Per-service | Centralized |
| Testing | MCP-specific tests | Standard HTTP tests |
| Reusability | Locked to MCP | Works as API or MCP |
| Learning curve | MCP protocol | REST API (standard) |
| Flexibility | Tightly coupled | Loose coupling |
| Performance | Direct | 1 HTTP hop overhead |

**Verdict**: Wrapper approach wins for modularity, wrapper adds ~5-10ms latency (negligible)

---

## Migration Strategy

### Phase 1: Services First (Current)
- Develop all 10 services as standard Flask APIs
- Follow MCP-ready guidelines (Pydantic, REST, JSON)
- Test via HTTP/curl/pytest
- Services are production-ready without MCP

### Phase 2: Wrapper Development
- Build py-mcp-wrapper generic library
- Test with 1-2 simple services
- Add introspection, schema generation
- Support stdio + SSE modes

### Phase 3: Service Configs
- Write mcp-config.yaml for each service
- Test auto-discovery
- Add custom overrides where needed
- Validate MCP tool generation

### Phase 4: Integration
- Deploy services + wrappers
- Test with Claude Desktop, VSCode
- Iterate on configs based on usage
- Document best practices

---

## Security Considerations

### Authentication
- Wrapper validates MCP client identity
- Passes credentials to backend services
- Supports OAuth2, JWT, API keys

### Authorization
- Per-tool access control
- Role-based tool visibility
- Rate limiting per user

### Input Validation
- Schema validation at wrapper level
- Prevents malformed requests reaching service
- Sanitizes inputs before proxying

---

## Conclusion

The **py-mcp-wrapper** strategy enables:
1. Services remain simple HTTP APIs (no MCP coupling)
2. MCP exposure via configuration (not code)
3. Reusable across any Flask/FastAPI service
4. Flexible deployment (per-service, gateway, sidecar)
5. Zero impact on service development

This approach maximizes **separation of concerns**: services focus on business logic, wrapper handles protocol translation.

---

**Document Version**: 1.0  
**Last Updated**: February 10, 2026  
**Complements**: ARCHITECTURE_MICROSERVICES_AS_LIBRARIES.md
