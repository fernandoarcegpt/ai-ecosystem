# Calculadora Básica

Esta feature proporciona un módulo de **calculadora** con cuatro operaciones aritméticas básicas:

| Función | Descripción |
|---|---|
| `sumar(a, b)` | Devuelve la suma de `a` y `b`. |
| `restar(a, b)` | Devuelve la resta de `b` de `a`. |
| `multiplicar(a, b)` | Devuelve el producto de `a` y `b`. |
| `dividir(a, b)` | Devuelve el cociente de `a` dividido por `b`. Si `b` es 0 lanza `ValueError`. |

## Estructura de directorios

```
├── src/
│   └── calculator.py   # Implementación de las funciones
├── tests/
│   └── test_calculator.py
└── docs/
    └── README.md
```

## Uso

```python
from calculator import sumar, restar, multiplicar, dividir

print(sumar(2, 3))          # 5
print(restar(10, 3))         # 7
print(multiplicar(4, 5))     # 20
print(dividir(10, 2))        # deceptively 5.0
```

## Ejecutar tests

Los tests utilizan **pytest**. Para llevado a cabo la prueba:

```bash
npm run test
# o directamente
pytest tests/test_calculator.py
```

Asegêrse de que el entorno de `npm` tenga los scripts de test configurados (ver `package.json`).

## Nota de calidad

- El módulo sigue las guias de estilo de 500 líneas por archivo.
- Se aprovisionan docstring claros y se lanza una excepción controlada al intentar dividir por cero.
- Los tests cubren casos positivos, negativos y de borde.

## Licencia

MIT license.
