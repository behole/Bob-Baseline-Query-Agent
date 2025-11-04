# GEO Audit Platform - Architecture v2.0

## Overview

The GEO Audit Platform has been refactored from a monolithic script-based system into a modern, plugin-based architecture that is extensible, maintainable, and production-ready.

## Design Principles

1. **Plugin Architecture**: Easy to add new AI platforms, storage backends, and report types
2. **Separation of Concerns**: Clear boundaries between platforms, storage, analysis, and reporting
3. **Multi-Client Ready**: Support multiple brands/clients with isolated configurations
4. **API-Ready**: Architecture designed to support future REST API or web interface
5. **Testable**: Dependency injection and interface-based design enable comprehensive testing

## Directory Structure

```
geo-audit-platform/
├── geo_audit/                    # Main package
│   ├── core/                     # Core business logic
│   │   ├── tracker.py           # Main orchestrator
│   │   └── analyzer.py          # Analysis engine (future)
│   ├── platforms/               # AI Platform plugins
│   │   ├── base.py             # Abstract PlatformClient
│   │   ├── claude.py
│   │   ├── chatgpt.py
│   │   ├── google_ai.py
│   │   └── perplexity.py
│   ├── storage/                 # Storage backends
│   │   ├── base.py             # Abstract StorageBackend
│   │   ├── google_sheets.py
│   │   └── database.py         # Future: SQL/NoSQL
│   ├── reports/                 # Report generators
│   │   ├── base.py             # Abstract ReportGenerator
│   │   ├── standard.py         # Future
│   │   └── advanced.py         # Future
│   ├── utils/                   # Shared utilities
│   │   ├── brand_keywords.py
│   │   ├── competitors.py
│   │   └── screenshot.py
│   └── config/                  # Configuration management
│       └── settings.py
├── cli/                         # CLI interface
│   └── main.py                 # Click-based commands
├── config/
│   ├── clients/                # Per-client YAML configs
│   │   ├── brush_on_block.yaml
│   │   └── restoration_hardware.yaml
│   └── platforms.yaml          # Platform credentials
├── data/
│   └── queries/                # Query JSON files
├── reports/
│   └── output/                 # Generated reports
└── legacy/                      # Old scripts (still functional)
```

## Core Components

### 1. Platform Plugin System

**Base Class**: `geo_audit/platforms/base.py`

```python
class PlatformClient(ABC):
    def get_platform_name(self) -> str: ...
    def query(self, query_text: str) -> PlatformResponse: ...
    def test_connection(self) -> bool: ...
```

**Implementations**:
- `ClaudeClient` - Anthropic Claude
- `ChatGPTClient` - OpenAI GPT-4
- `GoogleAIClient` - Google Gemini
- `PerplexityClient` - Perplexity AI

**Adding New Platforms**:
1. Create new class extending `PlatformClient`
2. Implement `get_platform_name()`, `_initialize()`, and `query()`
3. Register in `GEOTracker.PLATFORM_REGISTRY`
4. Add config to `config/platforms.yaml`

### 2. Storage Backend System

**Base Class**: `geo_audit/storage/base.py`

```python
class StorageBackend(ABC):
    def create_worksheet(self, name, headers) -> bool: ...
    def write_row(self, worksheet_name, row_data) -> bool: ...
    def read_worksheet(self, worksheet_name) -> List[Dict]: ...
```

**Current Implementation**:
- `GoogleSheetsBackend` - Google Sheets via gspread

**Future Backends**:
- PostgreSQL
- MongoDB
- SQLite
- S3/Cloud Storage

### 3. Core Tracker Orchestrator

**File**: `geo_audit/core/tracker.py`

The `GEOTracker` class orchestrates the entire workflow:

1. **Initialization**: Loads platform clients, storage backend, utilities
2. **Query Execution**: Runs queries across platforms using plugin system
3. **Analysis**: Detects brand mentions, competitors, positioning
4. **Storage**: Saves results via storage backend
5. **Screenshots**: Generates visual snapshots of responses

**Key Methods**:
- `run_query()` - Single query across platforms
- `run_query_batch()` - Batch processing of multiple queries
- `test_connections()` - Verify all services are accessible

### 4. Configuration Management

**Multi-Level Configuration**:

1. **Platform Config** (`config/platforms.yaml`):
```yaml
platforms:
  Claude:
    api_key: "sk-ant-..."
    model: "claude-sonnet-4-20250514"
  ChatGPT:
    api_key: "sk-..."
    model: "gpt-4o"

storage:
  credentials_path: "config/google-credentials.json"
  spreadsheet_id: "1abc..."
```

2. **Client Config** (`config/clients/brand_name.yaml`):
```yaml
brand_name: "Restoration Hardware"
industry: "furniture"
keywords:
  - "restoration hardware"
  - "rh"
competitors:
  - "Pottery Barn"
  - "West Elm"
```

### 5. CLI Interface

**Commands**:

```bash
# Test connections
./geo-audit test

# Initialize new client
./geo-audit init pottery_barn --industry furniture

# Run tracking
./geo-audit track --client brand_name --queries queries.json --worksheet "Audit_2025"

# Generate report (future)
./geo-audit report --worksheet "Audit_2025" --client brand_name --output report.html
```

## Data Flow

```
User Command (CLI)
    ↓
Configuration Loading (YAML/JSON)
    ↓
GEOTracker Initialization
    ├─→ Platform Clients (Claude, ChatGPT, etc.)
    ├─→ Storage Backend (Google Sheets)
    └─→ Utilities (Keywords, Competitors, Screenshots)
    ↓
Query Execution
    ├─→ Platform 1: Claude
    ├─→ Platform 2: ChatGPT
    ├─→ Platform 3: Google AI
    └─→ Platform 4: Perplexity
    ↓
Response Analysis
    ├─→ Brand Mention Detection
    ├─→ Competitor Detection
    ├─→ Position Analysis
    └─→ Source Citation Extraction
    ↓
Screenshot Generation
    ↓
Storage (Google Sheets)
    ↓
Report Generation (Future)
```

## Extensibility

### Adding a New AI Platform

1. Create `geo_audit/platforms/new_platform.py`:

```python
from .base import PlatformClient, PlatformResponse

class NewPlatformClient(PlatformClient):
    def get_platform_name(self) -> str:
        return "New Platform"

    def _initialize(self) -> None:
        self.api_key = self.config.get('api_key')
        # Initialize API client

    def query(self, query_text: str) -> PlatformResponse:
        # Query the platform
        # Return PlatformResponse
```

2. Register in `tracker.py`:
```python
PLATFORM_REGISTRY = {
    ...
    'New Platform': NewPlatformClient,
}
```

3. Add to config:
```yaml
platforms:
  New Platform:
    api_key: "..."
```

### Adding a New Storage Backend

1. Create `geo_audit/storage/new_backend.py`:

```python
from .base import StorageBackend

class NewBackend(StorageBackend):
    def _initialize(self) -> None:
        # Connect to storage

    def write_row(self, worksheet_name, row_data) -> bool:
        # Write to storage
```

2. Use in tracker:
```python
storage = NewBackend(storage_config)
```

### Adding a New Report Type

1. Create `geo_audit/reports/new_report.py`:

```python
from .base import ReportGenerator

class NewReportGenerator(ReportGenerator):
    def get_report_type(self) -> str:
        return "new_type"

    def generate(self, data, brand_name, output_path) -> Path:
        # Generate report
```

## Testing

### Unit Tests
```bash
pytest tests/unit/
```

### Integration Tests
```bash
pytest tests/integration/
```

### Connection Test
```bash
./geo-audit test
```

## Migration from Legacy

The old scripts still work! But to use the new system:

1. **Convert config.json** → `config/platforms.yaml`
2. **Create client configs**: `./geo-audit init client_name`
3. **Use new CLI**: `./geo-audit track` instead of `python3 ai_query_tracker.py`

## Benefits of v2.0 Architecture

✅ **Extensible**: Add new platforms in minutes, not hours
✅ **Multi-Client**: Support unlimited brands with isolated configs
✅ **Maintainable**: Clear separation of concerns, easy to understand
✅ **Testable**: Mock platforms/storage for comprehensive testing
✅ **API-Ready**: Easy to wrap in FastAPI/Flask for web service
✅ **Type-Safe**: Full type hints throughout
✅ **Documented**: Clear interfaces and documentation

## Future Roadmap

1. **Report Generator Plugins**: Refactor report generation into plugin system
2. **Database Backend**: Add PostgreSQL/MongoDB support
3. **REST API**: FastAPI wrapper for web service
4. **Dashboard**: React-based web UI
5. **Scheduled Runs**: Cron-like scheduling for automated tracking
6. **Alerting**: Slack/email notifications for mention changes
7. **More Platforms**: Grok, Gemini Pro, Meta AI, etc.
