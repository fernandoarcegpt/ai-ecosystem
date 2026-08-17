import os
import sys
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

db = kuzu.Database("/home/fernando/ai-ecosystem/storage/kuzu/knowledge_base")
graph_store = KuzuGraphStore(db)

index = PropertyGraphIndex.from_existing(property_graph_store=graph_store)
query_engine = index.as_query_engine(include_text=True)

pregunta = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else input("Escribe tu pregunta: ")

print(f"\nConsultando: '{pregunta}'...\n")
response = query_engine.query(pregunta)
print("Respuesta:")
print(response)
