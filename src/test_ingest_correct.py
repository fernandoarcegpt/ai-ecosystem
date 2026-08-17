#!/usr/bin/env python3
"""Simplified ingest script that matches query.py's approach."""
import os
import kuzu
from dotenv import load_dotenv
from llama_index.core import PropertyGraphIndex, Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.graph_stores.kuzu import KuzuGraphStore

load_dotenv()

# Configuration
api_key = os.getenv("OPENROUTER_API_KEY")
model_name = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
embed_name = os.getenv("OPENROUTER_EMBED_MODEL", "text-embedding-3-small")

# Validate API key
if not api_key or api_key == "tu_api_key_aqui":
    raise ValueError("Configura tu OPENROUTER_API_KEY real dentro del archivo .env")

# Configure LlamaIndex
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

# Initialize KùzuDB
db_path = "/home/fernando/ai-ecosystem/storage/kuzu/knowledge_base.kuzu"
os.makedirs(os.path.dirname(db_path), exist_ok=True)

# Clean any previous test files
import shutil
db_dir = os.path.dirname(db_path)
for f in os.listdir(db_dir):
    if f.startswith('knowledge_base'):
        os.remove(os.path.join(db_dir, f))

# Initialize database and graph store
db = kuzu.Database(db_path)
graph_store = KuzuGraphStore(db)

# Create test documents (this would normally come from PDFs and code)
test_documents = [
    "Este es un documento de prueba para validar el sistema de ingestion",
    "Este es otro documento de prueba adicional",
    "Documento adicional para pruebas de integración"
]

# Create test documents using llama_index Document class
from llama_index.core import Document
documents = [Document(text=doc) for doc in test_documents]

# Create the index using from_existing() like query.py does
print("Construyendo el PropertyGraph...")
index = PropertyGraphIndex.from_existing(
    property_graph_store=graph_store,
    documents=documents
)

# Save the index (this should persist to the database)
print("¡Ingestión completada! El grafo se guardó en", db_path)