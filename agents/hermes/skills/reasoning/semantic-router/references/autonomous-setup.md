# Autonomous Setup Patterns for Semantic Router

This document captures patterns for setting up the Semantic Router in automated environments without interactive prompts.

## Pattern 1: Local Skill Installation

When `hermes skills install` fails with local paths:

```bash
# Create directory
mkdir -p ~/.hermes/skills/reasoning

# Copy skill directly
cp /path/to/semantic_router.py ~/.hermes/skills/reasoning/

# Verify
hermes skills list | grep semantic_router
```

## Pattern 2: Non-Interactive Configuration

```bash
# Set language
hermes config set display.language español

# Set model
hermes config set model.default openrouter/free
hermes config set model.provider openrouter

# Disable interactive prompts
hermes config set approvals.mode off

# Verify
hermes doctor
```

## Pattern 3: Credential Setup

```bash
# Add to .env
echo "OPENROUTER_API_KEY=your_key" >> ~/.hermes/.env

# Check
hermes doctor | grep "API key"
```

## Pattern 4: Validation Script

```bash
#!/bin/bash
# validate-semantic-router.sh

# Run tests
pytest tests/test_semantic_router/ -v

# Test classification
python3 -c "
from skilled.reasoning.semantic_router import classify_task_structure
result = classify_task_structure('Asigna diez usuarios... sin información de costos.')
assert result['mode'] == 'human_review'
assert result['confidence'] == 0.8
print('Validation passed')
"
```

## Pitfalls

- Don't use `hermes skills install /local/path` - it won't work
- Don't hand-edit config.yaml - use `hermes config set`
- Don't chain hermes commands that require TTY with `&&`
- Don't put secrets in config.yaml - use .env only

## Context

This pattern emerged from a session where the user requested: "hazlo tu mismo sin mi intervención" (do it yourself without my intervention). The setup successfully configured Spanish language, OpenRouter model, installed the semantic-router skill via filesystem copy, ran tests, and validated that uncertain inputs correctly trigger human_review mode.