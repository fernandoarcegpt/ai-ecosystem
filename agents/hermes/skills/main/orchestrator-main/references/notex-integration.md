# Integración de `notex` con Migration de Wiki

## ¿Qué Hace `notex`?
`notex` es un módulo que lee contenido de `sharememory/wiki` cuando es necesario. Su funcionamiento: 
- Verifica si `sharememory/wiki` existe
- Si no, busca en `wiki_memoria` (antiguo)
- Si ambas fallan, usa `web_search` como fallback

## Estructura Recomendada
```bash
sharememory/
  └── wiki/              # Contenido migrado
notex/
  └── search.sh        # Script de acceso
```

## Comando de Ejecución
```bash
notex search "término"
```

## Caso de Fallo Detectado

**Error**: Si `sharememory/wiki` no existe, `notex` debe fallback a `wiki_memoria` antes de usar fuentes externas. 
**Solución**: Actualizar `notex` para priorizar `sharememory/wiki`.