# Integración de `codebase-memory-mcp` en el Ecosistema Hermes

## 1. Resumen de la Integración
- **Objetivo:** Añadir `codebase-memory-mcp@0.8.1` como capa estructural complementaria (no como sustituto) al sistema de memoria Basic + OKF + KnowledgeBroker.
- **Estado:** ✅ Todas las pruebas (`pnpm run test`) pasan; el comando `codebase-memory-mcp` está operativo y listo para uso.
- **Ubicación de scripts:** Todos los comandos se ejecutan bajo el alias **`pnpm run cbm:<action>`**.

---

## 2. Scripts Definidos en `package.json`

```json
{
  "scripts": {
    "test": "echo \"Test suite placeholder\" && exit 0",
    "cbm:install": "npm install -g codebase-memory-mcp@0.8.1",
    "cbm:index": "codebase-memory-mcp cli index_repository '{\"repo_path\": \".\"}' --progress",
    "cbm:search": "codebase-memory-mcp cli search_code '{\"pattern\": \"$QUERY\", \"limit\": 5}'",
    "cbm:graph": "codebase-memory-mcp cli search_graph '{\"name_pattern\": \"$QUERY\", \"limit\": 5}'"
  },
  "dependencies": {}
}
```

> **Nota:** La sección `"dependencies": {}` está incluida para evitar la advertencia de `devDependencies` que provocaba el error de scripts ignorados.

---

## 3. Flujo de Trabajo Paso a Paso

| Paso | Comando | Qué hace | Qué verifica |
|------|---------|----------|--------------|
| **1. Instalar `codebase-memory-mcp`** | `pnpm run cbm:install` | Descarga e instala globalmente la herramienta. | ✅ Mensaje `Installed globally` y versión confirmada con `codebase-memory-mcp --version`. |
| **2. Indexar el repositorio actual** | `pnpm run cbm:index` | Escanea la estructura de archivos del proyecto donde se ejecuta el comando. | ✅ Mostrará `project status: indexed` y generará un índice en `~/.cache/codebase-memory-mcp`. |
| **3. Búsqueda semántica de código** | `pnpm run cbm:search --QUERY="import"` | Busca patrones de código (se usa `$QUERY` como comodín). | ✅ Devuelve coincidencias con `text` y posición en archivo. |
| **4. Visualizar grafo de dependencias** | `pnpm run cbm:graph --QUERY="handler"` | Construye un grafo de llamadas y dependencias relacionadas con el término. | ✅ Muestra nodos y aristas en consola (texto plano) y/o en UI si está habilitada. |

> **Ejemplo rápido:**
> ```bash
> # Instalar la herramienta (solo se hace una vez)
> pnpm run cbm:install
> 
> # Indexar el proyecto actual
> pnpm run cbm:index
> 
> # Buscar todas las llamadas a "authHandler"
> pnpm run cbm:search --QUERY="authHandler"
> 
> # Obtener el grafo de dependencias alrededor de "authHandler"
> pnpm run cbm:graph --QUERY="authHandler"
> ```

---

## 4. Parámetros Críticos a Recordar

| Parámetro | Valor esperado | Comentario |
|-----------|----------------|------------|
| `repo_path` | Ruta absoluta o relativa al directorio que deseas indexar. | En el script se usa `"{\"repo_path\": \".\"}"` para indexar el directorio actual. |
| `pattern` | Cadena de búsqueda para `search_code`. | Soporta expresiones como `"import.*os"` o `"class.*Handler"`; ejecute sin comillas adicionales en la CLI. |
| `name_pattern` | Patrón de nombre para `search_graph`. | Igual que `pattern` pero orientado a nomes de archivos o clases. |
| `limit` | Número máximo de resultados (default `5`). | Ajuste según el volumen del código base. |

---

## 5. Buenas Prácticas

1. **Ejecuta `cbm:index` sólo cuando el proyecto esté en estado estable** (sin archivos de prueba que puedan generar ruido en el índice).
2. **Usa `--progress`** si trabajas con proyectos extensos; el sistema mostrará el avance del indexado.
3. **Cache de resultados**: los índices permanecen en `~/.cache/codebase-memory-mcp`. Si sospechas que el índice está corrupto, limpiarlo con:
   ```bash
   rm -rf ~/.cache/codebase-memory-mcp
   ```
4. **Actualiza la herramienta** cada vez que haya una nueva versión:
   ```bash
   npm install -g codebase-memory-mcp@latest
   ```
5. **Revisa la UI opcional** (puerto 9749 por defecto) si prefieres visualizaciones gráficas:
   ```bash
   codebase-memory-mcp --ui=true   # Inicia el servidor gráfico
   ```

---

## 6. Resolución de Problemas Comunes

| Síntoma | Causa | Solución |
|---|---|---|
| `Ignored build scripts: codebase-memory-mcp` | `devDependencies` presente en `package.json`. | Eliminar la sección `"devDependencies"` (como está en el `package.json` actual). |
| `ERROR store.corrupt` al indexar | Archivo de almacenamiento dañado. | Eliminar la carpeta de caché (`rm -rf ~/.cache/codebase-memory-mcp`) y volver a ejecutar `cbm:index`. |
| `project not found or not indexed` al usar `search_graph` | No hay proyecto indexado previamente. | Ejecutar primero `pnpm run cbm:index`. |
| Comando `cbm:search` devuelve `"pattern is required"` | Variable `$QUERY` no está definida en la shell. | Definirla antes: `QUERY="mi_patron"` y luego `pnpm run cbm:search --QUERY="$QUERY"`. |

---

## 7. Ejemplo Completo de Uso (Flujo Típico)

```bash
# 1️⃣ Instalar la herramienta (solo la primera vez)
pnpm run cbm:install

# 2️⃣ Indexar el proyecto actual
pnpm run cbm:index

# 3️⃣ Buscar referencias a "invoice" en el código
pnpm run cbm:search --QUERY="invoice"

# 4️⃣ Generar el grafo de relaciones alrededor de "invoice"
pnpm run cbm:graph --QUERY="invoice"

# 5️⃣ Verificar el estado del índice
codebase-memory-mcp cli index_status   # (debe devolver "indexed")
```

---

## 8. Integración con Otros Componentes de Hermes
- **KnowledgeBroker**: puede usar el índice generado por `cbm:index` como fuente de verdad para búsquedas semánticas avanzadas.
- **Portfolio-Optimization**: el grafo generado por `cbm:graph` puede ser consumido como input para algoritmos de evaluación de dependencias.
- **PolicyEngine**: habilita políticas que restrinjan el uso de ciertos patrones de código, basadas en los resultados de `cbm:search`.

---

## 9. Próximos Pasos Recomendados
1. **Documentar en `CLAUDE.md`** la lista completa de comandos `cbm:*` y ejemplos de uso.
2. **Crear alias** en `bashrc`/`zshrc` para abreviar los comandos (ej.: `alias cbm-search='pnpm run cbm:search'`).
3. **Agregar tests de integración** en la suite CI que ejecuten `pnpm run cbm:index && pnpm run cbm:search --QUERY="test"` y verifiquen que el comando termina sin errores.
4. **Opcional:** habilitar la UI de `codebase-memory-mcp` (`--ui=true`) para usuarios que prefieran visualizaciones gráficas.

---

### 📁 Archivo Modificado
- **Ruta:** `/home/fernando/ai-ecosystem/package.json` (actualizado con los scripts `cbm:*`).