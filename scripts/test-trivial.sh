#!/bin/bash
# Quick test to verify Claude Code CLI is working
# Run this from any directory

echo "Testing Claude Code CLI..."
echo "------------------------"

# Test 1: Version check
echo "1. Checking version..."
claude --version

# Test 2: Trivial task in print mode
echo ""
echo "2. Running trivial print-mode task..."
claude -p "Say hello and confirm Claude Code is working" --allowedTools Read --max-turns 1

# Test 3: JSON output test
echo ""
echo "3. Testing JSON output..."
claude -p "Return a JSON object with status: 'ok' and message: 'test passed'" --output-format json --allowedTools Read --max-turns 1

echo ""
echo "------------------------"
echo "Tests complete. If all three sections returned output, Claude Code is working correctly."