import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "../../simulador.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    if os.path.exists(schema_path):
        conn = get_db_connection()
        with open(schema_path, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM modules")
        if cursor.fetchone()[0] == 0:
            modules_data = [
                ("1. Macroeconomía y PYMEs", "Control de inflación, tasas de interés y tejido productivo PYME.", 1),
                ("2. Finanzas Públicas y Planificación", "Presupuesto nacional, deuda soberana y asignación estratégica.", 2),
                ("3. Análisis y Escáner de Contratos", "Auditoría de concesiones, obra pública y blindaje legal.", 3),
                ("4. Simulación de Crisis Históricas", "Toma de decisiones bajo presión extrema y colapsos sistémicos.", 4),
                ("5. Psicología Social y Carisma", "Gestión de expectativas ciudadanas e influencia política.", 5),
                ("6. Oratoria y Registro Lingüístico", "Discursos de Estado, persuasión y comunicación estratégica.", 6),
                ("7. Microexpresiones y Comunicación No Verbal", "Lectura de gestos, lenguaje corporal y detección de engaño.", 7),
                ("8. Idiomas Extranjeros para Líderes", "Diplomacia internacional y vocabulario geopolítico clave.", 8)
            ]
            cursor.executemany("INSERT INTO modules (title, description, order_num) VALUES (?, ?, ?)", modules_data)
            conn.commit()
        conn.close()
        print("Base de datos e indicadores inicializados de forma correcta.")

if __name__ == "__main__":
    init_db()
