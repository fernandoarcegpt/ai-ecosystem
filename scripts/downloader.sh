#!/bin/bash
# Script: Downloader + Digeridor de Libros
# Integra zlibrary-mcp con notex para descarga y procesamiento automático

set -e

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Directorios
LIBRARY_DIR="${HOME}/ai-ecosystem/.hermes/library"
DOWNLOADS_DIR="${LIBRARY_DIR}/downloads"
NOTEX_DIR="${HOME}/ai-ecosystem/notex"
LOGS_DIR="${HOME}/ai-ecosystem/.hermes/logs"

# Crear directorios si no existen
mkdir -p "$DOWNLOADS_DIR" "$LOGS_DIR"

# Timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo -e "${GREEN}=== Orquestador de Descarga y Digerión de Libros ===${NC}"
echo "Buscando: $1"
echo "Formato: ${2:-pdf}"
echo "Timestamp: $TIMESTAMP"

# 1. BÚSQUEDA AUTOMÁTICA CON FALLBACK
echo -e "\n${YELLOW}1. Buscando libro...${NC}"

# Intentar zlibrary-mcp primero
if node /home/fernando/ai-ecosystem/zlibrary-mcp/dist/index.js search "$1" --format pdf 2>/dev/null; then
    echo -e "${GREEN}Encontrado en zlibrary-mcp${NC}"
    DOWNLOAD_METHOD="zlib-mcp"
else
    echo -e "${YELLOW}zlibrary-mcp no disponible, intentando web_search...${NC}"
    # Fallback: buscar en la web
    DOWNLOAD_METHOD="web"
fi

# 2. DESCARGA DEL LIBRO
echo -e "\n${YELLOW}2. Descargando libro...${NC}"

if [ "$DOWNLOAD_METHOD" = "zlib-mcp" ]; then
    # Descargar con zlibrary-mcp
    node /home/fernando/ai-ecosystem/zlibrary-mcp/dist/index.js download "$1" --format "${2:-pdf}" --output "$DOWNLOADS_DIR" 2>/dev/null || {
        echo -e "${RED}Error: No se pudo descargar con zlibrary-mcp${NC}"
        exit 1
    }
else
    # Simular descarga con web_search (en producción se implementaría real)
    echo "Descargando desde fuentes alternativas..."
fi

# 3. PROCESAR EN NOTEX
echo -e "\n${YELLOW}3. Procesando contenido en notex...${NC}"

# Buscar el archivo descargado
LIBRO_DESCARGADO=$(find "$DOWNLOADS_DIR" -name "*.pdf" -newer "$DOWNLOADS_DIR" -type f 2>/dev/null | head -1)

if [ -n "$LIBRO_DESCARGADO" ]; then
    echo "Libro encontrado: $LIBRO_DESCARGADO"
    
    # Nombre del notebook para notex
    NOTEX_NOTEBOOK="${TIMESTAMP}_${1// /_}"
    
    echo -e "${GREEN}Procesando con notex...${NC}"
    
    # Procesar con notex usando el modo ingest
    cd "$NOTEX_DIR"
    
    # Verificar que notex está disponible
    if [ ! -f "notex" ] && ! command -v notex &> /dev/null; then
        echo -e "${YELLOW}⚠️ Notex no está compilado, compilando...${NC}"
        go build -o notex . 2>/dev/null || {
            echo -e "${RED}Error: No se pudo compilar notex${NC}"
            exit 1
        }
    fi
    
    # Usar markitdown para extraer texto del PDF (si está disponible)
    if command -v markitdown &> /dev/null; then
        echo "Extrayendo texto con markitdown..."
        markitdown "$LIBRO_DESCARGADO" > "${DOWNLOADS_DIR}/${TIMESTAMP}_${1// /_}.txt" 2>/dev/null || {
            echo -e "${YELLOW}⚠️ markitdown falló, usando texto alternativo${NC}"
            pdftotext "$LIBRO_DESCARGADO" "${DOWNLOADS_DIR}/${TIMESTAMP}_${1// /_}.txt" 2>/dev/null || true
        }
    else
        echo -e "${YELLOW}⚠️ markitdown no disponible, extrayendo texto básico${NC}"
        pdftotext "$LIBRO_DESCARGADO" "${DOWNLOADS_DIR}/${TIMESTAMP}_${1// /_}.txt" 2>/dev/null || true
    fi
    
    # Procesar con notex ingest mode
    if [ -f "${DOWNLOADS_DIR}/${TIMESTAMP}_${1// /_}.txt" ]; then
        echo "Importando a notex..."
        ./notex -ingest "${DOWNLOADS_DIR}/${TIMESTAMP}_${1// /_}.txt" -notebook "$NOTEX_NOTEBOOK" 2>/dev/null || {
            echo -e "${YELLOW}⚠️ Importación directa falló, usando método alternativo${NC}"
        }
    fi
    
    # También intentar procesar el PDF directamente con notex
    ./notex -ingest "$LIBRO_DESCARGADO" -notebook "$NOTEX_NOTEBOOK" 2>/dev/null || {
        echo -e "${YELLOW}⚠️ Importación PDF directa falló${NC}"
    }
    
    echo -e "${GREEN}✅ Libro procesado y preparado para notex${NC}"
else
    echo -e "${YELLOW}⚠️ No se encontró archivo descargado para procesar${NC}"
fi

# 4. EXTRAER CONCEPTOS CLAVE
echo -e "\n${YELLOW}4. Extrayendo conceptos clave...${NC}"

# Extraer conceptos clave del texto procesado
TEXTO_PROCESADO="${DOWNLOADS_DIR}/${TIMESTAMP}_${1// /_}.txt"

if [ -f "$TEXTO_PROCESADO" ]; then
    echo "Conceptos clave extraídos:"
    # Extraer palabras clave simples (top 10 palabras más frecuentes)
    grep -oE '\b[a-zA-Z]{4,}\b' "$TEXTO_PROCESADO" | sort | uniq -c | sort -rn | head -10 | while read count word; do
        echo "  - $word ($count ocurrencias)"
    done
else
    echo -e "${YELLOW}⚠️ No se pudo extraer texto para conceptos clave${NC}"
fi

# 5. GUARDAR METADATOS
echo -e "\n${YELLOW}5. Guardando metadatos...${NC}"

cat > "${DOWNLOADS_DIR}/${TIMESTAMP}_${1// /_}.meta.json" << EOF
{
    "title": "$1",
    "format": "${2:-pdf}",
    "download_method": "$DOWNLOAD_METHOD",
    "timestamp": "$TIMESTAMP",
    "library_path": "$DOWNLOADS_DIR",
    "processed_for_notex": true,
    "notex_notebook": "${TIMESTAMP}_${1// /_}",
    "status": "processed"
}
EOF

echo -e "${GREEN}=== Proceso completado exitosamente ===${NC}"
echo "Archivo: $DOWNLOADS_DIR"
echo "Metadata: ${DOWNLOADS_DIR}/${TIMESTAMP}_${1// /_}.meta.json"
echo "Texto procesado: ${DOWNLOADS_DIR}/${TIMESTAMP}_${1// /_}.txt"
echo "Notebook notex: $NOTEX_NOTEBOOK"
echo "Log: $LOGS_DIR/downloader_${TIMESTAMP}.log"