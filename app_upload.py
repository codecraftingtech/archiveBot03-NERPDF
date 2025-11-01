# app_upload.py
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
import shutil
import uuid
import json
import os
from typing import Dict

# Importar funciones del módulo que creaste
from db_sqlite import init_db, get_connection, insert_archivo_pdf, get_archivo_by_uuid

app = FastAPI(title="PDF Upload -> SQLite")

DEFAULT_FOLDER = "uploads"

# Directorio para uploads (relativo al proyecto)
UPLOAD_DIR = Path(DEFAULT_FOLDER)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Inicializar/asegurar DB (se creará si no existe)
DB_PATH = init_db()  # init_db crea carpeta data/ y tabla archivoPDF si es necesario


@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...), name: str = Form(...)) -> Dict:
    """
    Endpoint para subir un PDF y guardarlo en uploads/ y en la tabla archivoPDF.
    Parámetros form-data:
      - file: archivo PDF
      - name: nombre descriptivo (string)
    Retorna: JSON con uuid, id y path.
    """
    # Validaciones básicas
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF")

    # Asegurarnos que la DB y la tabla existen (init_db ya lo hizo, pero por robustez comprobamos)
    # init_db() ya fue llamado arriba para obtener DB_PATH. Podríamos volver a llamarlo si quisiéramos reasegurar.
    db_path = DB_PATH  # ruta absoluta al archivo DB
    if not os.path.exists(db_path):
        # Intentar crear/initializar
        db_path = init_db()

    # Guardar el archivo en uploads con nombre único
    unique_id = str(uuid.uuid4())
    safe_filename = f"{unique_id}___{Path(file.filename).name}"
    dest_path = UPLOAD_DIR / safe_filename

    try:
        with dest_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        file.file.close()

    # Preparar metadata básica (puedes enriquecerla luego)
    metadata = {
        "original_filename": file.filename,
        "uploaded_as": str(dest_path),
        "placeholders": []  # aquí se llenaría info extra (coords, etc) si procesas el PDF
    }
    metadata_json = json.dumps(metadata, ensure_ascii=False)

    # Insertar registro en DB
    conn = get_connection(db_path)
    try:
        # Garantizar unicidad del uuid; insert_archivo_pdf lanzará error en caso de duplicado
        record_id = insert_archivo_pdf(conn, unique_id, name, str(dest_path.resolve()), metadata_json)
    except Exception as e:
        # En caso de error, eliminar el archivo guardado para no dejar basura
        try:
            dest_path.unlink(missing_ok=True)
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=f"Error al insertar en DB: {e}")
    finally:
        conn.close()

    return JSONResponse(content={
        "uuid": unique_id,
        "id": record_id,
        "name": name,
        "path": str(dest_path.resolve()),
        "message": "Archivo subido y metadata guardada correctamente"
    })
