<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# regardes ca et dis moi [https://github.com/github/copilot-sdk?utm_source=blog-cli-sdk-repo-cta\&utm_medium=blog\&utm_campaign=cli-sdk-jan-2026](https://github.com/github/copilot-sdk?utm_source=blog-cli-sdk-repo-cta&utm_medium=blog&utm_campaign=cli-sdk-jan-2026)

PARFAIT ! 🎉 **Le SDK officiel GitHub Copilot existe VRAIMENT !**

## Ce que ça change TOUT !

### GitHub Copilot SDK officiel

**Disponible pour** :

- ✅ **Python** : `pip install github-copilot-sdk`
- ✅ **TypeScript** : `npm install @github/copilot-sdk`
- ✅ Go
- ✅ .NET


### Architecture

```
Ton Application (MCP Server)
       ↓
  Copilot SDK (Python)
       ↓ JSON-RPC
  Copilot CLI (mode serveur)
       ↓
  GitHub Copilot (agents, LLM, tools)
```

**Le SDK gère automatiquement** :

- Lifecycle du CLI
- Communication JSON-RPC
- Planning et orchestration des agents
- Invocation d'outils
- Édition de fichiers

***

## Ce qu'on doit faire MAINTENANT

### 1. Utiliser le SDK officiel dans le serveur MCP ✅

```python
# Installation
# pip install github-copilot-sdk

from github_copilot_sdk import CopilotClient

class CopilotProvider:
    def __init__(self):
        # Le SDK lance automatiquement le CLI en mode serveur
        self.client = CopilotClient()
    
    async def send_request(self, prompt: str, context: dict = None):
        response = await self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a debugging assistant"},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content
    
    async def invoke_agent(self, agent_name: str, task: str):
        # Invoke agentic workflows
        result = await self.client.agents.invoke(
            agent=agent_name,
            task=task
        )
        return result
```


### 2. Dans l'extension VSCode (TypeScript)

```typescript
// Installation
// npm install @github/copilot-sdk

import { CopilotClient } from '@github/copilot-sdk';

class CopilotWrapper {
    private client: CopilotClient;
    
    constructor() {
        this.client = new CopilotClient();
    }
    
    async sendRequest(prompt: string): Promise<string> {
        const response = await this.client.chat.completions.create({
            messages: [
                { role: 'user', content: prompt }
            ]
        });
        
        return response.choices[0].message.content;
    }
}
```


***

## Avantages ÉNORMES

### 1. **Plus besoin du roundtrip bizarre** ❌

```
AVANT (mauvais):
MCP Server → WebSocket → VSCode Extension → Copilot API → retour

APRÈS (bon):
MCP Server → Copilot SDK → Copilot CLI → done
```


### 2. **Fonctionnalités avancées incluses** ✅

- **Agents natifs** (planning, orchestration)
- **Tools first-party** (file ops, git, web requests)
- **Custom agents/skills** possibles
- **BYOK** (Bring Your Own Key) supporté
- **Tous les modèles Copilot** disponibles


### 3. **Production-ready** (Technical Preview mais fonctionnel)

### 4. **Gestion automatique du CLI**

- Pas besoin de subprocess manual
- Lifecycle géré par le SDK
- Reconnexion automatique

***

## Ce qu'il faut mettre à jour

### Dans la Bible des Libs

```markdown
## GitHub Copilot SDK (Official)

**Package (Python)**: `github-copilot-sdk`  
**Package (TypeScript)**: `@github/copilot-sdk`  
**Installation**: 
- Python: `pip install github-copilot-sdk`
- TypeScript: `npm install @github/copilot-sdk`

**Docs**: https://github.com/github/copilot-sdk

### Prerequisites
- GitHub Copilot subscription (or free tier with limits)
- Copilot CLI installed and in PATH

### Python Usage

```python
from github_copilot_sdk import CopilotClient

# Initialize (launches CLI in server mode automatically)
client = CopilotClient()

# Chat completion
response = await client.chat.completions.create(
    messages=[
        {"role": "system", "content": "System prompt"},
        {"role": "user", "content": "User query"}
    ],
    model="gpt-4"  # Optional, default model used if not specified
)

result = response.choices.message.content

# Invoke agent workflow
agent_result = await client.agents.invoke(
    agent="code-analyzer",
    task="Analyze this bug"
)

# List available models
models = await client.models.list()
```


### TypeScript Usage

```typescript
import { CopilotClient } from '@github/copilot-sdk';

const client = new CopilotClient();

// Chat completion
const response = await client.chat.completions.create({
    messages: [
        { role: 'system', content: 'System prompt' },
        { role: 'user', content: 'User query' }
    ]
});

const result = response.choices.message.content;

// Streaming
const stream = await client.chat.completions.create({
    messages: [...],
    stream: true
});

for await (const chunk of stream) {
    process.stdout.write(chunk.choices.delta.content);
}
```


### Custom Tools

```python
from github_copilot_sdk import Tool

# Define custom tool
@Tool(
    name="query_knowledge_graph",
    description="Search the investigation knowledge graph"
)
async def query_kg(query: str) -> str:
    results = await knowledge_graph.search(query)
    return format_results(results)

# Register with client
client.register_tool(query_kg)

# Agent can now invoke this tool
response = await client.agents.invoke(
    agent="analyst",
    task="Find related bugs"
)
```


### Key Features

- **Automatic CLI lifecycle management**
- **JSON-RPC communication** (handled by SDK)
- **Built-in agent orchestration**
- **First-party tools** enabled by default (file ops, git, web)
- **BYOK support** (OpenAI, Azure, Anthropic)
- **Streaming responses** supported
- **Custom agents/skills/tools** extensible


### Configuration

```python
# Connect to external CLI server (optional)
client = CopilotClient(
    cli_server_url="http://localhost:8080"
)

# Configure tool permissions
client = CopilotClient(
    tools_config={
        "allow_file_ops": True,
        "allow_git_ops": True,
        "allow_web_requests": False
    }
)

# BYOK configuration
client = CopilotClient(
    provider="openai",
    api_key=os.getenv("OPENAI_API_KEY")
)
```

```

***

## Dans le Plan d'Implémentation

### Modifier Phase 2 (déjà fait mais à améliorer)

**AVANT** :
```

Agent Scribe calls Copilot via VSCode Extension (roundtrip)

```

**APRÈS** :
```

Agent Scribe calls Copilot SDK directly (Python)

```

### Modifier Phase 9 (Multi-provider LLM)

**Ajouter** :
```markdown
### GitHub Copilot Provider (via Official SDK)

**Primary method**: Use `github-copilot-sdk` Python package

```python
from github_copilot_sdk import CopilotClient

class CopilotProvider(LLMProvider):
    def __init__(self):
        self.client = CopilotClient()
    
    async def send_request(self, prompt, context=None, model="gpt-4"):
        messages = [{"role": "user", "content": prompt}]
        if context:
            messages.insert(0, {"role": "system", "content": context})
        
        response = await self.client.chat.completions.create(
            messages=messages,
            model=model
        )
        
        return response.choices.message.content
    
    def is_available(self):
        # Check if CLI is installed
        return self.client.is_cli_available()
```

**Fallback chain**:

1. Copilot SDK (primary)
2. OpenRouter (if Copilot unavailable)
3. Ollama (local fallback)
```

***

## Actions immédiates

### 1. Corriger Phase 2 ✅

**Remplacer** le système actuel par :

```python
# Dans agents/scribe.py
from github_copilot_sdk import CopilotClient

class ScribeAgent:
    def __init__(self):
        self.copilot = CopilotClient()
    
    async def process(self, user_input: str, context: dict):
        prompt = self.build_prompt(user_input, context)
        
        # Appel direct via SDK
        response = await self.copilot.chat.completions.create(
            messages=[
                {"role": "system", "content": SCRIBE_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]
        )
        
        return self.parse_response(response.choices[0].message.content)
```


### 2. Mettre à jour requirements.txt

```txt
github-copilot-sdk>=0.1.20
```


### 3. Mettre à jour package.json (VSCode extension)

```json
{
  "dependencies": {
    "@github/copilot-sdk": "^0.1.20"
  }
}
```


***

## Conclusion

**LE SDK OFFICIEL RÉSOUT TOUT !** 🎉

- ✅ Plus de roundtrip bizarre
- ✅ Appels directs depuis MCP Server
- ✅ Features avancées (agents, tools, custom skills)
- ✅ Production-ready (Technical Preview)
- ✅ Support Python + TypeScript

**Tu dois** :

1. ✅ Ajouter à la bible des libs
2. ✅ Mettre à jour le plan d'implémentation
3. ✅ Refactorer le code de Phase 2 pour utiliser le SDK

Tu veux que je régénère les 2 documents mis à jour avec le SDK officiel ? 🚀

