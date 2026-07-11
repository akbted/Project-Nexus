# OpenProject MCP Server

An MCP (Model Context Protocol) server for OpenProject, built with FastMCP. Enables AI assistants like Claude to interact with OpenProject — listing projects, work packages, and managing resources through natural language.

## Architecture

This project follows a **Thin Client + Separate Tools** architecture with clear separation of concerns:

```
AI Agent → MCP Client → FastMCP Server → Tool Functions → OpenProject API
                                        ↓
                                   Logfire (traces, metrics)
```

### Design Patterns

| Pattern | Where | Purpose |
|---------|-------|---------|
| **Singleton** | `src/config/settings.py` | Single settings instance via `get_settings()` |
| **Factory Method** | `src/factories/client_factory.py` | Centralizes client creation |
| **Abstract Base Class** | `src/client/base.py` | Thin contract for client implementations |
| **Dependency Injection** | `OpenProjectClient(settings)` | Settings passed in, not imported globally |

## Project Structure

```
src/
├── api/
│   ├── middleware.py          # Auth middleware (API key verification)
│   └── mcp_server.py         # FastMCP server with lifespan & tool registration
├── client/
│   ├── base.py               # ABC defining client interface
│   └── openproject.py        # Concrete client wrapping httpx.AsyncClient
├── config/
│   └── settings.py           # Pydantic Settings with Singleton pattern
├── factories/
│   └── client_factory.py     # Factory for creating OpenProject clients
├── schema/
│   ├── project.py            # Project & Description Pydantic models
│   └── work_package.py       # WorkPackage & WorkPackageDescription models
└── tools/
    ├── list_project.py       # list_openproject_projects()
    └── list_work_packages.py # list_project_workpackages()

tests/
├── conftest.py               # Shared fixtures & mock helpers
├── test_schemas.py           # Pydantic model validation tests
├── test_settings.py          # Settings singleton tests
├── client/
│   └── test_openproject.py   # Client configuration tests
└── tools/
    └── test_list_projects.py # Tool function tests with mocked HTTP
```

## Setup

### 1. Clone and Install

```bash
git clone <repository-url>
cd "OpenProject MCP"
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
# OpenProject API Configuration
OPENPROJECT_TOKEN=your_openproject_api_token_here
OPENPROJECT_APIROOT=http://localhost:8080

# MCP Server Authentication
MCP_SERVER_API=your_api_key_here

# Logfire Observability
LOGFIRE_TOKEN=your_logfire_write_token_here
```

### 3. Get OpenProject API Token

1. Log in to your OpenProject instance
2. Go to **My Account** → **API token**
3. Generate a new token
4. Copy it to `OPENPROJECT_TOKEN` in `.env`

## Usage

### Start the Server (HTTP Transport)

```bash
python -m src.api.mcp_server
```

Server runs on `http://127.0.0.1:8000/mcp`

### Test with MCP Inspector

```bash
# List available tools
npx @modelcontextprotocol/inspector --cli http://127.0.0.1:8000/mcp --transport http --method tools/list

# Call a tool
npx @modelcontextprotocol/inspector --cli http://127.0.0.1:8000/mcp --transport http --method tools/call --tool-name list_projects
```

### Test with curl

```bash
curl -X POST http://127.0.0.1:8000/mcp \
  -H "Content-Type: application/json" \
  -H "x-api-key: your_api_key_here" \
  -d '{"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "list_projects"}, "id": 1}'
```

## Available Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `list_projects` | List all projects in OpenProject | — |
| `list_workpackages` | List work packages for a project | `project_id` (required) |

## Authentication

The server supports API key authentication via HTTP headers:

```bash
-H "x-api-key: your_api_key_here"
```

In **stdio mode** (used by Claude Desktop), authentication is skipped automatically.

## Observability (Logfire)

This server uses [Pydantic Logfire](https://logfire.pydantic.dev) for observability, providing:

- **MCP tool call tracing** — who called which tool, duration, result
- **HTTP request monitoring** — all OpenProject API calls tracked
- **Error tracking** — full stack traces for debugging
- **Real-time dashboard** — visualize traces at https://logfire.pydantic.dev

### Setup

1. Create a Logfire account at https://logfire.pydantic.dev
2. Go to **Settings** → **API Keys** → Create a **Write Token**
3. Add `LOGFIRE_TOKEN=your_token_here` to your `.env` file

### What Gets Traced

| Trace Type | What It Shows |
|------------|---------------|
| MCP Tool Calls | `list_projects`, `list_workpackages` — caller, duration, result |
| HTTP Requests | `GET /api/v3/projects` — status code, latency, errors |
| Errors | Any exceptions with full stack traces |
| Lifespan | Server startup/shutdown events |

## Testing

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_schemas.py
```

### Test Coverage

- **Schema tests**: Pydantic model validation, field aliases, optional fields
- **Settings tests**: Singleton pattern, environment variables, missing fields
- **Client tests**: HTTP client configuration, auth setup, lifecycle
- **Tool tests**: API calls, response parsing, error handling

## Design Decisions

### Why Thin Client + Separate Tools?

The client (`OpenProjectClient`) only handles HTTP connectivity. Tool functions (`list_openproject_projects`, etc.) own the business logic. This follows the **Single Responsibility Principle** and makes extending tools straightforward — add a new function, not modify existing code.

### Why Raw `_links` Dict?

WorkPackage uses `links: dict = Field(alias="_links")` instead of a model_validator. This keeps the model simple while preserving all link data. Tool functions extract nested fields as needed.

## TODO

- [ ] Add more tools: `get_project`, `get_work_package`, `create_work_package`
- [ ] Implement role-based permission system (read-only vs admin tools)
- [ ] Strategy pattern for auth methods (API key, OAuth, BasicAuth)
- [ ] Add User management tools (`list_users`, `create_user`, `delete_user`)

## Requirements

- Python 3.12+
- OpenProject instance with API access

### Dependencies

- `fastmcp` — MCP server framework
- `httpx` — Async HTTP client
- `pydantic` — Data validation
- `pydantic-settings` — Environment-based configuration
- `logfire` — Observability and tracing
- `pytest` / `pytest-asyncio` — Testing
