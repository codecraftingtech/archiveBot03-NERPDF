# db_sqlite.py
"""
Gestión ligera de SQLite para almacenar metadatos de PDFs.
- Crea carpeta ./data/
- Crea ./data/contracts.db (si no existe)
- Crea la tabla 'archivoPDF' con la estructura solicitada.

Funciones principales:
- init_db(db_folder='data', db_name='contracts.db') -> str (ruta_db)
- get_connection(db_path) -> sqlite3.Connection
- create_table_if_not_exists(conn) -> None
- insert_archivo_pdf(conn, uuid, nombre, path, metadata_json) -> int (id)
- get_archivo_by_uuid(conn, uuid) -> dict | None
- list_archivos(conn) -> list[dict]
"""

import os
import sqlite3
import uuid
from pathlib import Path
from typing import Optional, Dict, List, Any


DEFAULT_DB_FOLDER = "data"
DEFAULT_DB_NAME = "contracts.db"


def init_db(db_folder: str = DEFAULT_DB_FOLDER, db_name: str = DEFAULT_DB_NAME) -> str:
    """
    Crea la carpeta para la DB (si no existe) y devuelve la ruta al archivo DB.
    También crea la tabla 'archivoPDF' si no existe.
    Retorna la ruta absoluta al archivo DB.
    """
    os.makedirs(db_folder, exist_ok=True)
    db_path = Path(db_folder) / db_name
    # Asegurarnos que el archivo existe (sqlite lo crea al conectar si no existe)
    conn = get_connection(str(db_path))
    try:
        create_table_if_not_exists(conn)
    finally:
        conn.close()
    return str(db_path.resolve())


def get_connection(db_path: str) -> sqlite3.Connection:
    """
    Abre y devuelve una conexión sqlite3.Connection.
    Activamos row_factory para devolver filas como dict.
    """
    conn = sqlite3.connect(db_path, timeout=30)
    conn.row_factory = sqlite3.Row
    # Mejorar seguridad: habilitar foreign keys si se necesitara en el futuro
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def create_table_if_not_exists(conn: sqlite3.Connection) -> None:
    """
    Crea la tabla 'archivoPDF' con la estructura solicitada.
    Tipo CLOB se representa en SQLite como 'CLOB' o 'TEXT'; SQLite es dinámico en tipos.
    """
    create_sql = """
    CREATE TABLE IF NOT EXISTS archivoPDF (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uuid TEXT UNIQUE,
        nombre VARCHAR(255),
        path VARCHAR(1024),
        metadata_json CLOB
    );
    """
    conn.execute(create_sql)
    conn.commit()


def insert_archivo_pdf(conn: sqlite3.Connection, uuid: str, nombre: str, path: str, metadata_json: str) -> int:
    """
    Inserta un registro en archivoPDF y retorna el id generado.
    Usa consulta parametrizada para evitar inyección.
    """
    insert_sql = """
    INSERT INTO archivoPDF (uuid, nombre, path, metadata_json)
    VALUES (?, ?, ?, ?);
    """
    cur = conn.cursor()
    cur.execute(insert_sql, (uuid, nombre, path, metadata_json))
    conn.commit()
    return cur.lastrowid


def get_archivo_by_uuid(conn: sqlite3.Connection, uuid: str) -> Optional[Dict[str, Any]]:
    """
    Recupera un registro por uuid. Devuelve dict o None si no existe.
    """
    sel = "SELECT * FROM archivoPDF WHERE uuid = ?;"
    cur = conn.execute(sel, (uuid,))
    row = cur.fetchone()
    return dict(row) if row else None


def list_archivos(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    """
    Lista todos los registros de archivoPDF.
    """
    cur = conn.execute("SELECT * FROM archivoPDF ORDER BY id DESC;")
    rows = cur.fetchall()
    return [dict(r) for r in rows]


# Ejemplo de uso cuando ejecutas el script directamente
if __name__ == "__main__":
    print("Inicializando DB en carpeta:", DEFAULT_DB_FOLDER)
    db_file = init_db()
    print("DB creada/abierta en:", db_file)

    conn = get_connection(db_file)
    try:
        # Ejemplo de inserción
        sample_uuid = str(uuid.uuid4())  # Genera un UUID v4 aleatorio
        sample_nombre = "contrato_venta_enero.pdf"
        sample_path = str(Path(DEFAULT_DB_FOLDER) / sample_nombre)
        sample_metadata = '{"placeholders": [], "uploaded_name": "contrato_venta_enero.pdf"}'

        # Insertar sólo si no existe
        existing = get_archivo_by_uuid(conn, sample_uuid)
        if existing:
            print("Registro ya existe:", existing)
        else:
            new_id = insert_archivo_pdf(conn, sample_uuid, sample_nombre, sample_path, sample_metadata)
            print(f"Registro insertado con id = {new_id}")

        # Listar registros
        items = list_archivos(conn)
        print("Registros en archivoPDF:", len(items))
        for it in items[:5]:
            print(it)
    finally:
        conn.close()
