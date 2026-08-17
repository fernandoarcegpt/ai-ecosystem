---
name: project-categorizer
description: "Skill automática para categorizar proyectos en subcarpetas dentro de wiki_memoria/proyectos/ según palabras clave, número de archivos y complejidad temporal."
platforms: [linux, macos, windows]
tags: [organization, project-management, automation]
version: 2.0.0
author: Hermes Agent
license: MIT
---

# Project Categorizer (Automático)

## 📌 Propósito
Automatiza la categorización de proyectos en subcarpetas dentro de `wiki_memoria/proyectos/` según palabras clave, cantidad de archivos y complejidad temporal.

## 📂 Estructura de carpetas esperada
```
wiki_memoria/proyectos/
├─ investigación_cancer/
├─ proyectos_ia/
├─ libros/
├─ proyectos_complejos/
├─ proyectos_largo_plazo/
└─ otros/
```

## 🧠 Reglas automáticas de categorización
1. **Palabras clave en nombre o archivos**:
   - `cáncer`, `c Romance`, `oncología`, `tumor` → `investigación_cancer/`
   - `IA`, `inteligencia artificial`, `machine learning` → `proyectos_ia/`
   - `libro`, `lectura`, `texto` → `libros/`
2. **Cantidad de archivos**:
   - >10 archivos `.md` o >5 `PDF` → `proyectos_complejos/`
   - >20 archivos en total → `proyectos_largo_plazo/` (requiere confirmación manual)
3. **Prioridad**: si una palabra clave coincide, se aplica esa categoría sin importar el número de archivos.
4. **Intervención manual**: si supera 20 archivos, el skill pausa y pausa y espera confirmación manual para confirmación.

## 🔄 Flujo automático
1. Detecta nuevos proyectos en `wiki_memoria/staging/proyectos/` o `wiki_memoria/proyectos/otros/`.
2. Ejecuta análisis de palabras clave y conteo de archivos.
3. Mueve los archivos a la subcarpeta correspondiente.
4. Registra la operación en `wiki_memoria/.changelog.log`.
5. Si >20 archivos → pausa y pausa y espera confirmación manual (requiere confirmación manual).

## 📈 Ejemplo de flujo automático
```bash
# 1. Crear proyecto en staging:
mkdir -p wiki_memoria/staging/proyectos/cancer_research_2026
echo "# Nota" > wiki_memoria/staging/proyectos/cancer_research_2026/proyecto.md
# (agregar 15 archivos .md adicionales)

# 2. Ejecutar categorizador:
self-audit --detect
self-audit --audit

# 3. Resultado:
#   - Proyecto se mueve a wiki_memoria/proyectos/investigación_cancer/
```