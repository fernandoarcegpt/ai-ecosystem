#!/usr/bin/env python3
"""Minimal test script for knowledge-broker connectivity - verifies basic operations."""
import os
import kuzu
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Verify .env existence and API key
api_key_env = os.getenv("OPENROUTER_API_KEY")
if api_key_env:
    print("✓ OPENROUTER_API_KEY is set")
else:
    print("⚠ OPENROUTER_API_KEY is not set, but continuing for connectivity test")

# Test database operations
try:
    db_path = "/home/fernando/ai-ecosystem/storage/kuzu/knowledge_base.kuzu"
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Clean previous test DB if exists
    import shutil
    db_dir = os.path.dirname(db_path)
    for f in os.listdir(db_dir):
        if f.startswith('knowledge_base'):
            os.remove(os.path.join(db_dir, f))
    
    db = kuzu.Database(db_path)
    conn = kuzu.Connection(db)
    
    # Create a simple schema
    conn.execute('CREATE NODE TABLE TestNode(id INT PRIMARY KEY, name STRING)')
    conn.execute('CREATE RELATIONSHIP TABLE RELATIONSHIP(id INT PRIMARY KEY, from_id INT, to_id INT, type STRING)')
    
    # Insert a test node
    conn.execute('INSERT INTO TestNode (id, name) VALUES (1, "TestNode1")')
    conn.execute('INSERT INTO TestNode (id, name) VALUES (2, "TestNode2")')
    
    # Insert a relationship
    conn.execute('INSERT INTO RELATIONSHIP (id, from_id, to_id, type) VALUES (1, 1, 2, "TEST_REL")')
    
    # Query the data back
    result = conn.execute('MATCH (n:TestNode) RETURN n.id, n.name')
    rows = []
    while result.has_next():
        rows.append(result.get_next())
    
    print("✓ Database operations successful")
    print(f"  Retrieved {len(rows)} rows")
    for row in rows:
        print(f"  Row: {row}")
    
    # Close connection cleanly
    conn.close()
    db.close()
    print("✓ Connectivity test completed successfully")
    
except Exception as e:
    print(f"⚠ Error during test: {e}")
    import traceback
    traceback.print_exc()