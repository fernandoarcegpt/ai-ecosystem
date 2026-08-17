#!/usr/bin/env python3
import sys
import os

# Add the venv site-packages to path
venv_path = '/tmp/hermes_venv/lib/python3.12/site-packages'
if venv_path not in sys.path:
    sys.path.insert(0, venv_path)

# Add the skilled/reasoning path
skilled_path = '/home/fernando/ai-ecosystem/skilled'
if skilled_path not in sys.path:
    sys.path.insert(0, skilled_path)

# Now test imports
try:
    from reasoning.neuro_symbolic_engine import get_coordinator
    print("Import successful")
    # Test basic function
    coord = get_coordinator()
    print("Coordinator created:", type(coord))
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()