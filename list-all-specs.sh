#!/bin/bash

# Script: list-all-specs.sh
# Lists all specs in the OpenSpec directory without filtering by changes

SPEC_DIR="/home/fernando/ai-ecosystem/.openspec/specs"

echo "📁 Listing all specs in $SPEC_DIR"
echo "----------------------------------------"

if [ ! -d "$SPEC_DIR" ]; then
    echo "❌ Directory not found: $SPEC_DIR"
    exit 1
fi

# List all .js and .md files (specs) in the directory
find "$SPEC_DIR" -type f \( -name "*.js" -o -name "*.md" \) | sort | while read -r file; do
    echo "  - $(basename "$file")"
done

echo -e "\n${GREEN}✅ Total specs found: $(find "$SPEC_DIR" -type f | wc -l)${NC}"