# archivBot-NERProcess

NER PDF

## API de Gestion PDF

Esta API en Python utiliza FastAPI y python-multipart
para subir el archivo PDF al directorio 'upload' y almacenar su metada en BD Sqlite3.

### Requisitos

1. Python 3.9 o superior (macOS, Windows o Linux).
2. Instalar las dependencias:

```bash
pip install -r requirements.txt
```

### Ejecutar la API

3. Iniciar el servidor con:

```bash
uvicorn app_upload:app --host 127.0.0.1 --port 8000
```

### Probar con cURL

8. Invocar la API

# Invocacion de la API antigua version considerando el parametro "nombre de archivo"
```bash
curl -X POST "http://127.0.0.1:8000/upload-pdf/" \
  -F "file=@/Users/jeason.sergio/Documents/ProyectosProgramacion/Fuentes/archivBot-NERPDF-develop/pdf/contratoTipo1.pdf" \
  -F "name=compra_venta_inmueble" \
  -H "Accept: application/json"

# Invocacion de la API nueva version sin considerar el parametro "nombre de archivo"
```bash
curl -X POST "http://127.0.0.1:8000/upload-pdf/" \
  -F "file=@/Users/jeason.sergio/Documents/ProyectosProgramacion/Fuentes/archivBot-NERPDF-develop/pdf/contratoTipo1.pdf" \
  -H "Accept: application/json"  

# Invocacion de la API para consular elementos insertados
  curl -X GET "http://127.0.0.1:8000/archivos/b9ead545-44b8-4a7e-8144-a5c0f85b55e5" \
  -H "accept: application/json"



El comando devolverá un JSON con las entidades reconocidas.