# Hermes Memory Format Specification

## Overview
This document defines the OKF (Open Knowledge Format) schema used by Hermes Agent for persistent memory storage.

## Directory Structure

```
sharememory/
├── hermes_memory/          # Hermes Agent Memory (central knowledge broker)
│   ├── knowledge_broker.py # Knowledge broker logic for OKF operations
│   ├── basic_memory.py     # Basic memory utilities
│   ├── hermes_memory_format.md # This file
│   └── trades.json         # Trading history (example)
└── claude_memory/          # Claude Code Memory (Claude-specific configurations)
    └── claude_memory.md    # Claude-specific memory
```

## OKF Entry Structure

Each memory entry follows this JSON schema:

```json
{
  "id": "unique_hash_12chars",
  "type": "fact|procedure|context|trade|decision",
  "content": "The actual content to remember",
  "metadata": {
    "source": "user|system|observation|trade",
    "confidence": 0.0-1.0,
    "tags": ["tag1", "tag2"],
    "related_ids": ["hash1", "hash2"]
  },
  "timestamp": "ISO8601_timestamp",
  "expires_at": "ISO8601_or_null"
}
```

## Memory Types

### fact
Factual knowledge (e.g., "User prefers Spanish communication")

### procedure
Step-by-step workflows (e.g., "How to deploy Hermes skills")

### context
Session context (e.g., "Current project: ai-ecosystem")

### trade
Trading decisions and results (used by android-fin-gpt-trader)

### decision
Important decisions made during development

## Tagging Convention

Tags should be lowercase, snake_case, and follow these patterns:
- `domain:finance` - Domain classification
- `project:ai-ecosystem` - Project association
- `priority:high` - Priority level
- `status:completed` - Status tracking

## Versioning

Memory entries support versioning via the `version` field:
```json
{
  "version": "1.0.0",
  "updated_at": "ISO8601_timestamp"
}
```

## Expiration

Entries can have an `expires_at` field. Expired entries are automatically archived but not deleted.

## Integration Points

- **Hermes Agent**: Reads/writes to `hermes_memory/`
- **Claude Code**: Reads/writes to `claude_memory/`
- **android-fin-gpt-trader**: Writes trade data to `hermes_memory/trades.json`
- **zlibrary-mcp**: Can store downloaded book metadata in `hermes_memory/`