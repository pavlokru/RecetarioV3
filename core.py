# core.py
import sqlite3
import json
import os

class CatalogEngine:
    def __init__(self, db_path="data/catalogo.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row 
        return conn

    def _init_db(self):
        query_create = """
        CREATE TABLE IF NOT EXISTS recetas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            categoria TEXT,
            origen TEXT,
            dificultad TEXT,
            tiempo_preparacion_min INTEGER,
            porciones INTEGER,
            ingredientes TEXT,
            pasos TEXT,
            etiquetas TEXT,
            nota TEXT,
            imagen_url TEXT
        )
        """
        with self._get_connection() as conn:
            conn.execute(query_create)
            conn.commit()

    def inicializar_semilla(self, recetario_base):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM recetas")
            if cursor.fetchone()[0] == 0:
                query_insert = """
                INSERT INTO recetas (
                    nombre, categoria, origen, dificultad, tiempo_preparacion_min, 
                    porciones, ingredientes, pasos, etiquetas, nota, imagen_url
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                for r in recetario_base:
                    cursor.execute(query_insert, (
                        r.get("nombre"), r.get("categoria"), r.get("origen"),
                        r.get("dificultad"), r.get("tiempo_preparacion_min"), r.get("porciones"),
                        json.dumps(r.get("ingredientes") or []), 
                        json.dumps(r.get("pasos") or []),
                        json.dumps(r.get("etiquetas") or []), 
                        r.get("nota"), r.get("imagen_url")
                    ))
                conn.commit()

    def obtener_todos(self):
        with self._get_connection() as conn:
            # Se unifica en una sola consulta para evitar doble ejecución en memoria
            cursor = conn.execute("SELECT * FROM recetas ORDER BY id ASC")
            filas = cursor.fetchall()
            return [dict(fila) for fila in filas]

    def buscar(self, termino):
        query = """
        SELECT * FROM recetas 
        WHERE nombre LIKE ? OR categoria LIKE ? OR origen LIKE ? OR etiquetas LIKE ? OR ingredientes LIKE ?
        ORDER BY id ASC
        """
        termino_like = f"%{termino}%"
        with self._get_connection() as conn:
            cursor = conn.execute(query, (termino_like, termino_like, termino_like, termino_like, termino_like))
            return [dict(row) for row in cursor.fetchall()]

    def crear_receta(self, datos):
        query = """
        INSERT INTO recetas (
            nombre, categoria, origen, dificultad, tiempo_preparacion_min, 
            porciones, ingredientes, pasos, etiquetas, nota, imagen_url
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        with self._get_connection() as conn:
            conn.execute(query, (
                datos.get("nombre"), datos.get("categoria"), datos.get("origen"),
                datos.get("dificultad"), datos.get("tiempo_preparacion_min"), datos.get("porciones"),
                json.dumps(datos.get("ingredientes") or []), 
                json.dumps(datos.get("pasos") or []),
                json.dumps(datos.get("etiquetas") or []), 
                datos.get("nota"), datos.get("imagen_url")
            ))
            conn.commit()

    def actualizar_receta(self, receta_id, datos):
        query = """
        UPDATE recetas SET 
            nombre = ?, categoria = ?, origen = ?, dificultad = ?, 
            tiempo_preparacion_min = ?, porciones = ?, ingredientes = ?, 
            pasos = ?, etiquetas = ?, nota = ?, imagen_url = ?
        WHERE id = ?
        """
        with self._get_connection() as conn:
            conn.execute(query, (
                datos.get("nombre"), datos.get("categoria"), datos.get("origen"),
                datos.get("dificultad"), datos.get("tiempo_preparacion_min"), datos.get("porciones"),
                json.dumps(datos.get("ingredientes") or []), 
                json.dumps(datos.get("pasos") or []),
                json.dumps(datos.get("etiquetas") or []), 
                datos.get("nota"), datos.get("imagen_url"),
                receta_id
            ))
            conn.commit()

    def eliminar_receta(self, receta_id):
        with self._get_connection() as conn:
            conn.execute("DELETE FROM recetas WHERE id = ?", (receta_id,))
            conn.commit()