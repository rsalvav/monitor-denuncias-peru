"""
db.py

Persistencia SQLite del proyecto.
"""

import sqlite3

DB_NAME = "data/monitor_denuncias.db"


def crear_bd():

    conn = sqlite3.connect(DB_NAME)

    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS denuncias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        anio INTEGER,
        departamento TEXT,
        provincia TEXT,
        distrito TEXT,
        modalidad TEXT,
        cantidad INTEGER
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS historial_clima (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        departamento TEXT,
        temperatura REAL,
        precipitacion REAL,
        viento REAL,
        fecha_consulta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def guardar_consulta_clima(
    departamento,
    temperatura,
    precipitacion,
    viento
):

    conn = sqlite3.connect(DB_NAME)

    cur = conn.cursor()

    cur.execute("""
    INSERT INTO historial_clima
    (
        departamento,
        temperatura,
        precipitacion,
        viento
    )
    VALUES (?, ?, ?, ?)
    """,
    (
        departamento,
        temperatura,
        precipitacion,
        viento
    ))

    conn.commit()
    conn.close()


def obtener_historial_clima():

    conn = sqlite3.connect(DB_NAME)

    cur = conn.cursor()

    cur.execute("""
    SELECT *
    FROM historial_clima
    ORDER BY fecha_consulta DESC
    """)

    datos = cur.fetchall()

    conn.close()

    return datos
    
"""
Consulta 1 Últimas 10 consultas de clima por departamento
"""

SELECT departamento, temperatura, precipitacion, viento, fecha_consulta
FROM historial_clima
ORDER BY fecha_consulta DESC
LIMIT 10;

"""
Consulta 2 Temperatura promedio, máxima y mínima por departamento
"""

SELECT 
    departamento,
    ROUND(AVG(temperatura), 2) AS temp_promedio,
    MAX(temperatura)           AS temp_maxima,
    MIN(temperatura)           AS temp_minima,
    COUNT(*)                   AS total_consultas
FROM historial_clima
GROUP BY departamento
ORDER BY temp_promedio DESC;

"""
Consulta 3 Departamentos consultados más de una vez (repetidos)
"""

SELECT departamento, COUNT(*) AS veces_consultado
FROM historial_clima
GROUP BY departamento
HAVING COUNT(*) > 1
ORDER BY veces_consultado DESC;

