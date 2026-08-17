# 🦸‍♂️ TaskHero – To-Do List Gamificada con XP

API REST en Node.js/Express para gestionar tareas con un sistema de **poder** y **experiencia (XP)**. Cada tarea tiene un nivel de dificultad del 1 al 10, y al completarse otorga puntos de experiencia.

---

## 🎯 ¿Para qué sirve?

TaskHero convierte tu lista de tareas en un **juego de rol personal**. Puedes:

- Crear tareas con diferentes niveles de **poder** (1–10).
- Marcarlas como completadas y ganar **XP**.
- Ver tu progreso en tiempo real.
- Usar la API para integrarla fácilmente en otras apps o bots.

---

## 🚀 Instalación

```bash
# Clonar o copiar el proyecto
cd src/taskhero

# Instalar dependencias
npm install

# Iniciar el servidor
npm start
```

El servidor arranca en `http://localhost:3000` por defecto.

---

## 📡 Endpoints

| Método | Ruta         | Descripción                              |
|--------|--------------|------------------------------------------|
| `GET`    | `/health`      | Health check del servicio                |
| `GET`    | `/tasks`       | Listar todas las tareas                  |
| `GET`    | `/tasks/:id`   | Obtener una tarea por ID                 |
| `POST`   | `/tasks`       | Crear una nueva tarea                    |
| `PUT`    | `/tasks/:id`   | Actualizar una tarea (incluye completar) |
| `DELETE` | `/tasks/:id`   | Borrar una tarea                         |

---

## 🧩 Esquema de la Tarea

```json
{
  "id": "uuid",
  "title": "Comprar víveres",
  "description": "Ir al supermercado",
  "powerLevel": 3,
  "status": "pending",
  "xp": 30,
  "completedAt": null,
  "createdAt": "2026-07-09T12:00:00.000Z",
  "updatedAt": "2026-07-09T12:00:00.000Z"
}
```

| Campo         | Tipo    | Requerido | Descripción                                    |
|---------------|---------|-----------|------------------------------------------------|
| `title`       | string  | Sí        | Título de la tarea                             |
| `description` | string  | No        | Descripción detallada (opcional)               |
| `powerLevel`  | integer | Sí        | Dificultad (1–10). Más alto = más XP           |
| `status`      | string  | No        | `pending`, `in-progress`, `completed` (default: `pending`) |

---

## 🔢 Fórmula de XP

La experiencia (XP) se calcula de forma **lineal**:

```
XP = 10 × powerLevel
```

### Ejemplos

| powerLevel | XP otorgada |
|------------|-------------|
| 1          | 10 XP       |
| 3          | 30 XP       |
| 5          | 50 XP       |
| 7          | 70 XP       |
| 10         | 100 XP      |

> **Nota:** El XP se **asigna al crear la tarea** y se **mantiene** al completarla. No se modifica después.

---

## 🛠️ Uso con curl

### Crear una tarea
```bash
curl -X POST http://localhost:3000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Aprender Node.js", "description": "Estudiar Express y middleware", "powerLevel": 8}'
```

### Listar tareas
```bash
curl http://localhost:3000/tasks
```

### Completar una tarea
```bash
curl -X PUT http://localhost:3000/tasks/<id> \
  -H "Content-Type: application/json" \
  -d '{"status": "completed"}'
```

### Borrar una tarea
```bash
curl -X DELETE http://localhost:3000/tasks/<id>
```

---

## 🧪 Testing

```bash
# Ejecutar pruebas con Jest
npm test
```

Pruebas incluidas:
1. **XP linear** – Verifica que `XP = 10 × powerLevel`.
2. **Creación de tarea** – Valida creación con powerLevel 1–10.
3. **Error handling** – Rechaza powerLevel inválido o campos faltantes.

---

## 🗃️ Almacenamiento

- **Sin base de datos.** Los datos se almacenan en memoria (Map interno).
- Al reiniciar el servidor, los datos se pierden.
- Ideal para prototipos, demos o como capa de servicio en apps más grandes.

---

## 📦 Scripts disponibles

| Script        | Descripción               |
|---------------|---------------------------|
| `npm start`   | Inicia el servidor        |
| `npm test`    | Ejecuta las pruebas Jest  |
| `npm run dev` | (Opcional) con recarga en caliente |

---

## 📜 Licencia

MIT © Fernando Arce – AI Ecosystem