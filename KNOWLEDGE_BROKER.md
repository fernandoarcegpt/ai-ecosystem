# Knowledge Broker

## Función actual

`Knowledge Broker` es la capa de intermediación entre documentos, memoria estructural y herramientas externas de conocimiento.

En la arquitectura actual no debe entenderse como una base lógica completa, sino como una pieza dentro de una capa mayor de conocimiento:

```text
Documentos / código / notas
  ↓
Knowledge Broker / ingestión
  ↓
Kùzu + LlamaIndex / CBM / Obsidian
  ↓
consulta estructural o semántica
  ↓
Hermes / LLM / motores simbólicos
```

## Relación con el sistema neurosimbólico

El núcleo neurosimbólico vive principalmente en:

```text
skilled/reasoning/
```

El Knowledge Broker puede aportar contexto y fuentes, pero el razonamiento determinista lo ejecutan:

```text
NetworkX
Z3
PyDatalog
```

Por tanto:

- Knowledge Broker recupera o escribe conocimiento.
- ProblemExtractor formaliza problemas simbólicos.
- Los motores simbólicos verifican grafos, restricciones o reglas.
- El LLM recibe evidencia estructurada si el resultado es válido.

## Capas relacionadas

| Capa | Rol |
|---|---|
| Knowledge Broker | Intermediario de lectura/escritura de conocimiento |
| KùzuDB | Grafo persistente/documental |
| LlamaIndex | Ingesta y consulta sobre grafo/documentos |
| CBM | Índice estructural del código |
| Obsidian | Vault de notas vía API local |
| Hermes memory | Memoria conversacional/patrones |
| PyDatalog | Inferencia lógica por reglas |
| Z3 | Restricciones y satisfacibilidad |
| NetworkX | Grafos y dependencias |

## Estado implementado

Actualmente existen piezas para:

- Ingesta documental/código hacia grafo.
- Consulta semántica o estructural.
- Escritura validada hacia Obsidian en flujos donde esté configurado.
- Integración complementaria con CBM.

## Lo que todavía no es

Todavía no es una base tipo Quixote/Kappa completa.

Falta una capa canónica que guarde:

```text
hechos
reglas
hechos derivados
fuentes
versiones
confianza
identidad de entidades
contradicciones
trazas de razonamiento
```

## Modelo recomendado siguiente

Crear una base lógica persistente encima del broker:

```text
CanonicalLogicalKnowledgeBase
  ├── FactStore
  ├── RuleStore
  ├── SourceStore
  ├── EntityIdentityResolver
  ├── ContradictionEngine
  ├── DerivedFactStore
  └── ReasoningTraceStore
```

## Flujo recomendado futuro

```text
1. Ingerir documento o memoria.
2. Extraer candidatos a hechos.
3. Resolver identidad de entidades.
4. Guardar hecho con fuente, fecha y confianza.
5. Ejecutar reglas/inferencias.
6. Detectar contradicciones.
7. Guardar hechos derivados y traza.
8. Exponer consulta a Hermes/LLM.
```

## Principio de diseño

El Knowledge Broker debe ser el puente entre memoria documental y razonamiento simbólico, no un simple almacén de texto ni una memoria conversacional sin estructura.
