---
name: data-verifier
description: "Verifica información médica y científica usando fuentes confiables como OMS, Cancer Research UK y PubMed."
platforms: [linux, macos, windows]
tags: [verification, data, medical, research]
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Data Verifier

## 📌 Propósito
Esta habilidad **verifica datos médicos científicos** contra fuentes confiables antes de ser usados en documentos o informes. Es OBLIGATORIA antes de generar contenido médico en el ecosistema.

## 🧠 Fuentes de verificación
1. **OMS (World Health Organization)** – Estadísticas globales de cáncer
2. **Cancer Research UK** – Estadísticas específicas de cáncer
3. **PubMed/NCBI** – Estudios científicos peer-reviewed
4. **Base de conocimientos interna (OKF Wiki)** – Si ya fue verificado previamente

## 🔄 Flujo de verificación
1. Recibir dato a verificar (ej: "casos de cáncer globales 2024")
2. Buscar en fuentes confiables usando `web_search` + `web_extract`
3. Si no hay API key disponible, usar fuentes ya verificadas en base interna
4. Devolver resultado validado con fuente

## 📊 Comandos
```bash
# Verificar un dato específico
data-verifier "casos de cáncer globales 2024"

# Verificar con fuente específica
data-verifier --fuente oms "prevalencia de cáncer de mama"
```

## 📋 Buenas prácticas
- **Nunca usar datos sin verificarlos primero**
- **Incluir footnotes con referencias exactas** en documentos médicos
- **Actualizar la base interna** cuando se encuentre una nueva fuente válida