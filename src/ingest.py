import os
import kuzu
from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader, PropertyGraphIndex, Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.graph_stores.kuzu import KuzuGraphStore

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
model_name = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
embed_name = os.getenv("OPENROUTER_EMBED_MODEL", "text-embedding-3-small")

if not api_key or api_key == "tu_api_key_aqui":
    raise ValueError("Configura tu OPENROUTER_API_KEY real dentro del archivo .env")

# 1. Configurar LlamaIndex dinámicamente con OpenRouter
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

# 2. Inicializar KùzuDB
db_path = "/home/fernando/ai-ecosystem/storage/kuzu/knowledge_base.kuzu"
os.makedirs(os.path.dirname(db_path), exist_ok=True)

# Clean any previous test files
import shutil
db_dir = os.path.dirname(db_path)
for f in os.listdir(db_dir):
    if f.startswith('knowledge_base'):
        os.remove(os.path.join(db_dir, f))

db = kuzu.Database(db_path)
graph_store = KuzuGraphStore(db)

# 3. Leer los PDFs externos (data/raw)
pdf_documents = []
pdf_dir = "./data/raw"
if os.path.exists(pdf_dir) and os.listdir(pdf_dir):
    print(f"Cargando PDFs desde {pdf_dir}/...")
    pdf_reader = SimpleDirectoryReader(input_dir=pdf_dir)
    pdf_documents = pdf_reader.load_data()
    print(f"Se cargaron {len(pdf_documents)} páginas/fragmentos de PDFs.")
else:
    print(f"No se encontraron archivos en {pdf_dir}/ (se omitirá esta carpeta).")

# 4. Leer el código fuente y documentación interna del repositorio
print("Escaneando el repositorio en búsqueda de código y documentación...")
exclude_patterns = [
    "venv/*",
    ".venv/*",
    "storage/*",
    "data/*",         # Excluimos data aquí porque los PDFs ya se cargaron en el paso 3
    "__pycache__/*",
    ".git/*",
    "*.kuzu",
    "*.db"
]

repo_reader = SimpleDirectoryReader(
    input_dir=".",
    recursive=True,
    required_exts=[".py", ".md", ".txt", ".json", ".yaml", ".yml"],
    exclude=exclude_patterns,
    exclude_hidden=True
)

repo_documents = []
try:
    repo_documents = repo_reader.load_data()
    print(f"Se cargaron {len(repo_documents)} archivos/fragmentos del repositorio.")
except ValueError:
    print("No se encontraron archivos de código/texto en el directorio raíz para indexar.")

# 5. Combinar todos los documentos
all_documents = pdf_documents + repo_documents

if not all_documents:
    print("Error: No hay documentos (ni PDFs ni código) para procesar. Abortando.")
    exit()

# 6. Construir e ingerir el PropertyGraph conjunto
print(f"Construyendo el PropertyGraph con un total de {len(all_documents)} documentos...")
index = PropertyGraphIndex.from_documents(
    all_documents,
    property_graph_store=graph_store,
    show_progress=True
)

print("¡Digestión completada! El grafo combinado (PDFs + Código) se guardó correctamente en ./storage/kuzu.")
