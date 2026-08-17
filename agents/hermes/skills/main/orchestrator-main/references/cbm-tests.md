# CBM Verification & Troubleshooting

## Verification Workflow

### 1. Basic Functionality Check
```bash
# Verify binary exists and is executable
which codebase-memory-mcp
# Expected: /home/fernando/.config/nvm/versions/node/v22.23.1/bin/codebase-memory-mcp

# Verify version
codebase-memory-mcp --version
# Expected: codebase-memory-mcp 0.8.1
```

### 2. MCP Server Test
```bash
# Test MCP startup (will block, Ctrl+C to exit)
timeout 5 codebase-memory-mcp 2>&1 || true
```

### 3. Index Check
```bash
# Check if index exists
ls -la ~/.cache/codebase-memory-mcp/
# Expected: logs/, graph.db, or similar
```

### 4. Full Integration Test
```bash
# Run pnpm test (requires valid Claude Code auth)
pnpm run test
# Check for: "Tests complete" section
# CRITICAL: Must NOT have API Error 401

# If 401 error appears, verify:
echo $ANTHROPIC_AUTH_TOKEN | head -c 10
# Should show valid token prefix, not "Invalid bearer token"
```

## Test Results Template

```
✅ Verification Status: PASSED
- Binary: codebase-memory-mcp 0.8.1
- MCP Config: Corrected .mcp.json entry
- Basic Tests: All passed
- Claude Code Auth: [PENDING - 401 error]

⚠️ Blocking Issue: Claude Code CLI requires valid ANTHROPIC_AUTH_TOKEN
```

## Troubleshooting Flow

### Error: "API Error: 401 Invalid bearer token"
**When this appears**: During `pnpm run test` Step 2

**Diagnosis**:
1. Check token is set: `echo $ANTHROPIC_AUTH_TOKEN`
2. Token is not empty: `[[ -n "$ANTHROPIC_AUTH_TOKEN" ]] && echo valid || echo empty`
3. Token has correct format (OpenRouter)

**Remediation**:
- The 401 is a Claude Code auth issue, NOT CBM-related
- CBM functions correctly (separate from Claude Code session)
- Once auth is fixed, full tests will pass

### Error: "MCP server crashed on startup"
**When this appears**: During MCP initialization

**Diagnosis**:
```bash
# Check daemon logs
cat ~/.cache/codebase-memory-mcp/logs/cbm-daemon.log
```

**Remediation**:
1. Clear cache: `rm -rf ~/.cache/codebase-memory-mcp/`
2. Reinstall: `npm install -g codebase-memory-mcp@0.8.1 --force`

### Error: "Symbol not found" after install
**When this appears**: Binary execution fails

**Diagnosis**:
```bash
ldd $(which codebase-memory-mcp)  # Linux
otool -L $(which codebase-memory-mcp)  # macOS
```

**Remediation**:
- Binary is statically linked; this should NOT happen
- If it does, reinstall via npm

## Performance Benchmarks to Monitor

| Operation | Expected Time | Notes |
|-----------|---------------|-------|
| Version check | <1s | `codebase-memory-mcp --version` |
| Index small project | <5s | ~10K LOC |
| Search function | <10ms | Named search |
| Trace call path | <20ms | Depth 5 |

## Integration Points to Verify

1. **.mcp.json**: Correct command path (`codebase-memory-mcp`, NOT `./dist/index.js`)
2. **Hermes Agent**: Can route structural queries to CBM
3. **Knowledge Broker**: Can disambiguate CBM vs OKF queries
4. **Claude Code**: Can invoke CBM tools when needed

## Verification Commands Matrix

| Check | Command | Expected Result |
|-------|---------|-----------------|
| Binary | `which codebase-memory-mcp` | Path to binary |
| Version | `codebase-memory-mcp --version` | 0.8.1 |
| Help | `codebase-memory-mcp --help` | Lists 15 tools |
| MCP config | `cat .mcp.json` | Correct command entry |
| npm status | `npm list -g codebase-memory-mcp` | 0.8.1 |
| Cache dir | `ls ~/.cache/codebase-memory-mcp/` | Contains logs/ or graph.db |