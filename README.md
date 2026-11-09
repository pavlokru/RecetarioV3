# 🍳 Recetario V2 Ultra Ligero

Una aplicación web monolítica y minimalista para la gestión completa de recetas de cocina. Diseñada bajo la premisa de ser "Ultra Ligera", consolida el frontend y backend en una única interfaz reactiva, eliminando la necesidad de APIs externas, modelos pesados de IA u ORMs complejos.

## 🚀 Filosofía y Arquitectura

- **Monolito Eficiente:** Todo el ecosistema (UI y Lógica) corre sobre **Streamlit**.
- **Persistencia sin ORM:** Base de datos **SQLite** embebida (`data/catalogo.db`). Utiliza sentencias SQL puras mediante el motor nativo de Python para maximizar la velocidad y minimizar el consumo de RAM.
- **Gestión Inteligente de Medios:** Las imágenes subidas son redimensionadas y comprimidas automáticamente con **Pillow** y almacenadas en el volumen local (`static/uploads/`), guardando solo la ruta en la base de datos.
- **Estructuras Complejas Livianas:** Los ingredientes, pasos y etiquetas se almacenan como cadenas de texto JSON dentro de SQLite, evitando relaciones complejas de múltiples tablas.
- **Infraestructura Portable:** Entorno dockerizado (`python:3.12-slim`) que garantiza paridad total entre desarrollo local y producción.

## 🛠️ Stack Tecnológico

- **Frontend & Backend:** [Streamlit](https://streamlit.io/) (v1.38.0+)
- **Base de Datos:** SQLite3 (Librería nativa de Python `sqlite3`)
- **Procesamiento de Imágenes:** Pillow
- **Orquestación:** Docker & Docker Compose
- **Hot-Reload:** Watchdog

## 📂 Estructura del Proyecto

```text
RecetarioV3/
├── app.py                  # Interfaz principal Streamlit y modales UI
├── core.py                 # Motor de base de datos (CatalogEngine) CRUD SQL puro
├── data.py                 # Datos semilla (RECETARIO_BASE)
├── requirements.txt        # Dependencias de Python
├── docker-compose.yml      # Orquestador del contenedor y volúmenes
├── .devcontainer/
│   ├── Dockerfile          # Definición de la imagen del sistema operativo
│   └── devcontainer.json   # Configuración de entorno para VS Code
├── static/
│   └── uploads/            # Volumen de almacenamiento para fotografías físicas
└── data/
    └── catalogo.db         # Base de datos SQLite (se autogenera)