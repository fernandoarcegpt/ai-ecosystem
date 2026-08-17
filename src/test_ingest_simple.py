#!/usr/bin/env python3
"""Test script for knowledge-broker ingestion - simplified version."""
import os
import kuzu
from dotenv import load_dotenv
from llama_index.core import PropertyGraphIndex, Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.graph_stores.kuzu import KuzuGraphStore

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
model_name = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
embed_name = os.getenv("OPENROUTER_EMBED_MODEL", "text-embedding-3-small")

if not api_key or api_key == "tu_api_key_aqui":
    print("ERROR: Configura tu OPENROUTER_API_KEY real dentro del archivo .env")
    exit(1)

# 1. Configure LlamaIndex with OpenRouter
Settings.llm = OpenAI(
    model=model_name,
    api_key=api_key,
    api_base="https://openrouter.ai/api/v1",
)
Settings.embed_model = OpenAIEmbedding(
    model=embed_name,
    api_key=api_key,
    api_base="https://openrouter.ai/api/v1",
)

# 2. Initialize KùzuDB with correct path (ending in .kuzu)
db_path = "/home/fernando/ai-ecosystem/storage/kuzu/knowledge_base.kuzu"
os.makedirs(os.path.dirname(db_path), exist_ok=True)

# Clean any existing database files to avoid lock issues
import shutil
db_dir = os.path.dirname(db_path)
for f in os.listdir(db_dir):
    if f.startswith('knowledge_base'):
        os.remove(os.path.join(db_dir, f))

db = kuzu.Database(db_path)
graph_store = KuzuGraphStore(db)

# 3. Create a minimal test document
test_doc_text = "Este es un documento de prueba para validar el sistema de ingestion de knowledge-broker usando KuzuDB y LlamaIndex."

from llama_index.core import Document
test_document = Document(text=test_doc_text)

# 4. Build and ingest a minimal PropertyGraph index
print("Construyendo PropertyGraph con documento de prueba...")
index = PropertyGraphIndex.from_documents(
    [test_document],
    property_graph_store=graph_store,
    show_progress=True
)

print("¡Test completado! El grafo se creo correctamente en", db_path)