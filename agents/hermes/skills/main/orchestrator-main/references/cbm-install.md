# Codebase-Memory-MCP (CBM) Installation Guide

## Prerequisites
- Node.js v20+ (v22.23.1 confirmed working)
- npm v10+ (v10.9.8 confirmed working)
- Git

## Installation Methods

### Method 1: NPM Global (Recommended)
```bash
npm install -g codebase-memory-mcp@0.8.1
```

### Method 2: From Source
```bash
git clone https://github.com/DeusData/codebase-memory-mcp.git
cd codebase-memory-mcp
scripts/build.sh
```

### Method 3: Download Binary
```bash
# Get latest release from GitHub
wget https://github.com/DeusData/codebase-memory-mcp/releases/latest/download/codebase-memory-mcp-linux-amd64.tar.gz
tar xzf codebase-memory-mcp-linux-amd64.tar.gz
./install.sh
```

## Post-Installation Verification
```bash
codebase-memory-mcp --version
codebase-memory-mcp --help
```

## Configuration in .mcp.json
```json
{
  "mcpServers": {
    "codebase-memory-mcp": {
      "command": "codebase-memory-mcp",
      "args": [],
      "optional": true
    }
  }
}
```

## Common Issues & Fixes

### Issue: "command not found" after npm install
**Fix**: Ensure npm global bin is in PATH
```bash
export PATH="$(npm config get prefix)/bin:$PATH"
```

### Issue: Wrong path in .mcp.json (dist/index.js)
**Fix**: Use direct CLI command as shown above. The npm install provides a global binary.

### Issue: Binary not executable
**Fix**: 
```bash
chmod +x $(which codebase-memory-mcp)
```

## Environment Variables
```bash
# Optional: Custom cache directory
export CBM_CACHE_DIR="/home/fernando/ai-ecosystem/.cbm/index"

# Optional: Enable diagnostics
export CBM_DIAGNOSTICS=1
```

## Version Compatibility
- CBM 0.8.1 requires tree-sitter grammars (bundled)
- Compatible with Hermes Agent v3.0+
- Works with Claude Code CLI v2.1+

## Verification Checklist
- [ ] `codebase-memory-mcp --version` returns 0.8.1
- [ ] `codebase-memory-mcp --help` shows 15 tools
- [ ] `.mcp.json` contains correct command path
- [ ] No "dist/index.js" references