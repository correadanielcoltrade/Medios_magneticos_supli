# Despliegue en Render

Esta aplicacion es un servicio Flask. En Render debe desplegarse como **Web Service** con runtime **Python 3**.

## Opcion recomendada: Blueprint

1. Sube este proyecto a un repositorio de GitHub, GitLab o Bitbucket.
2. En Render, selecciona **New > Blueprint**.
3. Conecta el repositorio.
4. Render leera `render.yaml` y creara el servicio con:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Variable `SECRET_KEY` generada automaticamente.

## Opcion manual: Web Service

1. En Render, selecciona **New > Web Service**.
2. Conecta el repositorio.
3. Configura:
   - Runtime: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
4. Agrega variables de entorno:
   - `FLASK_ENV=production`
   - `SECRET_KEY=<un valor largo y secreto>`
   - `PYTHON_VERSION=3.12.8`

## Notas importantes

- Render usa almacenamiento temporal en el plan sin disco persistente. Esta app guarda los archivos cargados en `temp/`, por lo que sirven para la sesion actual, pero pueden perderse al reiniciar el servicio.
- El archivo debe descargarse despues de cargar el balance. Si el servicio se reinicia entre la carga y la descarga, se debe volver a cargar el archivo.
- El limite actual de carga es de 50 MB, definido en `app.py`.
