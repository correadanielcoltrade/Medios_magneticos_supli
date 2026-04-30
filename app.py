import os
import sys
from flask import Flask, render_template, request, jsonify, send_file, session
from werkzeug.utils import secure_filename
import pandas as pd
from datetime import datetime
import json
import uuid
import pickle
import atexit
import glob
import tempfile
import traceback
import threading
import time

# Agregar módulos al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.data_processor import DataProcessor
from modules.excel_generator import ExcelGenerator

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'coltrade_medios_magneticos_2025')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB máximo
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'
app.config['SESSION_COOKIE_HTTPONLY'] = True

# Configuración de carga
ALLOWED_EXTENSIONS = {'xlsx'}
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IS_PRODUCTION = os.environ.get('FLASK_ENV') == 'production'
UPLOAD_FOLDER = os.environ.get(
    'APP_TEMP_DIR',
    os.path.join(BASE_DIR, 'temp') if not IS_PRODUCTION else tempfile.gettempdir()
)
DATAFRAME_FOLDER = os.path.join(UPLOAD_FOLDER, 'dataframes')
UPLOAD_JOB_FOLDER = os.path.join(UPLOAD_FOLDER, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATAFRAME_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_JOB_FOLDER, exist_ok=True)

UPLOAD_JOBS = {}
UPLOAD_JOBS_LOCK = threading.Lock()
UPLOAD_JOB_TTL_SECONDS = 60 * 60


def log_exception(context, exc):
    """Imprime errores con traceback para que Render/Gunicorn los guarde en logs."""
    print(f"[ERROR] {context}: {str(exc)}")
    traceback.print_exc()


def set_upload_job(job_id, **changes):
    with UPLOAD_JOBS_LOCK:
        job = UPLOAD_JOBS.setdefault(job_id, {})
        job.update(changes)
        job['updated_at'] = time.time()


def get_upload_job(job_id):
    with UPLOAD_JOBS_LOCK:
        job = UPLOAD_JOBS.get(job_id)
        return job.copy() if job else None


def cleanup_upload_jobs():
    now = time.time()
    expired_paths = []
    with UPLOAD_JOBS_LOCK:
        expired_ids = [
            job_id for job_id, job in UPLOAD_JOBS.items()
            if now - job.get('updated_at', now) > UPLOAD_JOB_TTL_SECONDS
        ]
        for job_id in expired_ids:
            job = UPLOAD_JOBS.pop(job_id, {})
            upload_path = job.get('upload_path')
            if upload_path:
                expired_paths.append(upload_path)

    for upload_path in expired_paths:
        try:
            if os.path.exists(upload_path):
                os.remove(upload_path)
        except OSError:
            pass


def process_upload_job(job_id, upload_path, original_filename):
    try:
        set_upload_job(job_id, status='processing', message='Leyendo archivo Excel...')

        try:
            df = pd.read_excel(upload_path, sheet_name=0)
        except Exception as e:
            set_upload_job(job_id, status='error', message=f'Error al leer el archivo: {str(e)}')
            return

        set_upload_job(job_id, message='Validando estructura...')
        try:
            processor = DataProcessor(df)
            valido, errores = processor.validar_estructura()
            if not valido:
                set_upload_job(
                    job_id,
                    status='error',
                    message='Estructura inválida: ' + '; '.join(errores)
                )
                return
        except Exception as e:
            log_exception('DataProcessor initialization', e)
            set_upload_job(job_id, status='error', message=f'Error al procesar datos: {str(e)}')
            return

        set_upload_job(job_id, message='Calculando resumen de formatos...')
        try:
            resumen_formatos = {
                codigo: processor.obtener_resumen_formato(codigo)
                for codigo in FORMATOS_DISPONIBLES
            }
        except Exception as e:
            log_exception('Resumen de formatos', e)
            set_upload_job(
                job_id,
                status='error',
                message=f'Error al calcular el resumen de formatos: {str(e)}'
            )
            return

        dataframe_id = str(uuid.uuid4())
        dataframe_path = os.path.join(DATAFRAME_FOLDER, f'{dataframe_id}.pkl')

        set_upload_job(job_id, message='Guardando datos temporales...')
        try:
            with open(dataframe_path, 'wb') as f:
                pickle.dump(df, f)
        except Exception as e:
            log_exception('Guardar DataFrame temporal', e)
            set_upload_job(job_id, status='error', message=f'Error al guardar datos: {str(e)}')
            return

        set_upload_job(
            job_id,
            status='done',
            message=f'Archivo "{original_filename}" cargado correctamente',
            dataframe_id=dataframe_id,
            file_name=secure_filename(original_filename),
            resumen_formatos=resumen_formatos,
            file_size=f"{len(df)} filas × {len(df.columns)} columnas",
        )

    except Exception as e:
        log_exception('Upload job inesperado', e)
        set_upload_job(job_id, status='error', message=f'Error inesperado: {str(e)}')
    finally:
        try:
            if os.path.exists(upload_path):
                os.remove(upload_path)
        except OSError:
            pass


def limpiar_archivos_temp():
    """Limpia archivos temporales al cerrar la aplicación"""
    for archivo in glob.glob(os.path.join(DATAFRAME_FOLDER, '*.pkl')):
        try:
            os.remove(archivo)
        except:
            pass


atexit.register(limpiar_archivos_temp)

FORMATOS_DISPONIBLES = {
    '1001': {
        'nombre': 'Formato 1001',
        'descripcion': 'Pagos o abonos en cuenta y retenciones',
        'icono': '💰'
    },
    '1005': {
        'nombre': 'Formato 1005',
        'descripcion': 'IVA descontable',
        'icono': '📊'
    },
    '1006': {
        'nombre': 'Formato 1006',
        'descripcion': 'IVA generado',
        'icono': '📈'
    },
    '1007': {
        'nombre': 'Formato 1007',
        'descripcion': 'Ingresos recibidos',
        'icono': '💵'
    },
    '1008': {
        'nombre': 'Formato 1008',
        'descripcion': 'Cuentas por cobrar',
        'icono': '📋'
    },
    '1009': {
        'nombre': 'Formato 1009',
        'descripcion': 'Cuentas por pagar',
        'icono': '📌'
    },
    '2276': {
        'nombre': 'Formato 2276',
        'descripcion': 'Rentas de trabajo (empleados)',
        'icono': '👥'
    }
}


def archivo_permitido(filename):
    """Valida que el archivo sea .xlsx"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Renderiza la landing page"""
    return render_template('index.html', formatos=FORMATOS_DISPONIBLES)


@app.route('/upload', methods=['POST'])
def upload():
    """
    Maneja la carga del archivo Excel
    Retorna JSON con estado de la carga
    """
    try:
        cleanup_upload_jobs()
        # Validar que hay archivo
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No se envió archivo'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'success': False, 'message': 'Selecciona un archivo'}), 400

        # Validar extensión
        if not archivo_permitido(file.filename):
            return jsonify({
                'success': False,
                'message': 'Solo se permiten archivos .xlsx'
            }), 400

        # Validar nombre (debe contener "balance")
        if 'balance' not in file.filename.lower():
            return jsonify({
                'success': False,
                'message': 'El archivo debe contener "balance" en el nombre'
            }), 400

        job_id = str(uuid.uuid4())
        safe_name = secure_filename(file.filename)
        upload_path = os.path.join(UPLOAD_JOB_FOLDER, f'{job_id}_{safe_name}')

        try:
            file.save(upload_path)
        except Exception as e:
            log_exception('Guardar upload temporal', e)
            return jsonify({
                'success': False,
                'message': f'Error al guardar el archivo temporal: {str(e)}'
            }), 500

        set_upload_job(
            job_id,
            status='queued',
            message='Archivo recibido. Iniciando procesamiento...',
            upload_path=upload_path,
            file_name=safe_name,
        )

        thread = threading.Thread(
            target=process_upload_job,
            args=(job_id, upload_path, file.filename),
            daemon=True
        )
        thread.start()

        return jsonify({
            'success': True,
            'processing': True,
            'job_id': job_id,
            'message': 'Archivo recibido. Estamos procesándolo...'
        }), 202

        # Leer el Excel
        try:
            df = pd.read_excel(file, sheet_name=0)
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error al leer el archivo: {str(e)}'
            }), 400

        # Validar estructura
        try:
            processor = DataProcessor(df)
            valido, errores = processor.validar_estructura()

            if not valido:
                return jsonify({
                    'success': False,
                    'message': 'Estructura inválida: ' + '; '.join(errores)
                }), 400
        except Exception as e:
            log_exception('DataProcessor initialization', e)
            return jsonify({
                'success': False,
                'message': f'Error al procesar datos: {str(e)}'
            }), 500

        # Generar ID único para esta sesión y guardar DataFrame en archivo
        try:
            resumen_formatos = {
                codigo: processor.obtener_resumen_formato(codigo)
                for codigo in FORMATOS_DISPONIBLES
            }
        except Exception as e:
            log_exception('Resumen de formatos', e)
            return jsonify({
                'success': False,
                'message': f'Error al calcular el resumen de formatos: {str(e)}'
            }), 500

        dataframe_id = str(uuid.uuid4())
        dataframe_path = os.path.join(DATAFRAME_FOLDER, f'{dataframe_id}.pkl')

        try:
            with open(dataframe_path, 'wb') as f:
                pickle.dump(df, f)
        except Exception as e:
            log_exception('Guardar DataFrame temporal', e)
            return jsonify({
                'success': False,
                'message': f'Error al guardar datos: {str(e)}'
            }), 500

        # Guardar ID y metadata en sesión (muy pequeño, sin problemas)
        session['dataframe_id'] = dataframe_id
        session['file_name'] = secure_filename(file.filename)
        session['upload_time'] = datetime.now().isoformat()
        session['resumen_formatos'] = resumen_formatos
        session.modified = True

        return jsonify({
            'success': True,
            'message': f'Archivo "{file.filename}" cargado correctamente',
            'file_name': file.filename,
            'resumen_formatos': resumen_formatos,
            'file_size': f"{len(df)} filas × {len(df.columns)} columnas"
        }), 200

    except Exception as e:
        log_exception('Upload inesperado', e)
        return jsonify({
            'success': False,
            'message': f'Error inesperado: {str(e)}'
        }), 500


@app.route('/upload-status/<job_id>', methods=['GET'])
def upload_status(job_id):
    """Retorna el estado del procesamiento de un archivo cargado."""
    job = get_upload_job(job_id)
    if not job:
        return jsonify({
            'success': False,
            'status': 'missing',
            'message': 'No se encontró el procesamiento. Intenta cargar el archivo nuevamente.'
        }), 404

    status_value = job.get('status', 'queued')
    if status_value == 'done':
        session['dataframe_id'] = job['dataframe_id']
        session['file_name'] = job['file_name']
        session['upload_time'] = datetime.now().isoformat()
        session['resumen_formatos'] = job['resumen_formatos']
        session.modified = True

        return jsonify({
            'success': True,
            'status': 'done',
            'message': job['message'],
            'file_name': job['file_name'],
            'resumen_formatos': job['resumen_formatos'],
            'file_size': job['file_size']
        }), 200

    if status_value == 'error':
        return jsonify({
            'success': False,
            'status': 'error',
            'message': job.get('message', 'No se pudo procesar el archivo.')
        }), 200

    return jsonify({
        'success': True,
        'processing': True,
        'status': status_value,
        'message': job.get('message', 'Procesando archivo...')
    }), 200


@app.route('/status', methods=['GET'])
def status():
    """Retorna el estado de carga actual"""
    dataframe_id = session.get('dataframe_id', '')
    file_loaded = False

    if dataframe_id:
        dataframe_path = os.path.join(DATAFRAME_FOLDER, f'{dataframe_id}.pkl')
        file_loaded = os.path.exists(dataframe_path)

    file_name = session.get('file_name', '')

    return jsonify({
        'file_loaded': file_loaded,
        'file_name': file_name,
        'resumen_formatos': session.get('resumen_formatos', {})
    }), 200


@app.route('/download/<codigo_formato>', methods=['GET'])
def download(codigo_formato):
    """
    Genera y descarga el Excel para un formato específico

    Args:
        codigo_formato: '1001', '1005', etc.
    """
    try:
        print(f"\n{'='*80}")
        print(f"[DESCARGA] Iniciando generación de Formato {codigo_formato}")
        print(f"{'='*80}")

        # Validar que hay sesión con datos
        dataframe_id = session.get('dataframe_id', '')
        print(f"[1/5] Validando sesión... dataframe_id={dataframe_id}")

        if not dataframe_id:
            print(f"[ERROR] No hay dataframe_id en sesión")
            return jsonify({
                'success': False,
                'message': 'No hay archivo cargado. Por favor carga el archivo de balance primero.'
            }), 400

        dataframe_path = os.path.join(DATAFRAME_FOLDER, f'{dataframe_id}.pkl')
        print(f"[2/5] Verificando archivo... {dataframe_path}")

        if not os.path.exists(dataframe_path):
            print(f"[ERROR] Archivo no encontrado: {dataframe_path}")
            return jsonify({
                'success': False,
                'message': 'Archivo de datos no encontrado. Por favor carga el archivo nuevamente.'
            }), 400

        # Validar formato
        if codigo_formato not in FORMATOS_DISPONIBLES:
            print(f"[ERROR] Formato inválido: {codigo_formato}")
            return jsonify({
                'success': False,
                'message': f'Formato {codigo_formato} no válido'
            }), 400

        # Cargar DataFrame desde archivo temporal
        print(f"[3/5] Cargando DataFrame desde {dataframe_path}...")
        try:
            with open(dataframe_path, 'rb') as f:
                df = pickle.load(f)
            print(f"[3/5] DataFrame cargado: {len(df)} filas, {len(df.columns)} columnas")
        except Exception as e:
            print(f"[ERROR] No se pudo cargar DataFrame: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Error al cargar datos: {str(e)}'
            }), 400

        # Procesar datos según formato
        print(f"[4/5] Procesando datos para formato {codigo_formato}...")
        try:
            processor = DataProcessor(df)

            # Validar estructura
            valido, errores = processor.validar_estructura()
            if not valido:
                print(f"[ERROR] Estructura inválida: {errores}")
                return jsonify({
                    'success': False,
                    'message': f'Estructura inválida: {"; ".join(errores)}'
                }), 400

            df_formato = processor.procesar_formato(codigo_formato)

            if df_formato.empty:
                print(f"[WARNING] No se encontraron datos para el patrón de {codigo_formato}")
                return jsonify({
                    'success': False,
                    'message': f'No se encontraron datos para el formato {codigo_formato}. Verifica que el archivo contiene cuentas de este formato.'
                }), 400

            print(f"[4/5] Datos procesados: {len(df_formato)} filas (incluyendo totales)")
        except Exception as e:
            print(f"[ERROR] Error al procesar formato: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'message': f'Error al procesar datos: {str(e)}'
            }), 400

        # Generar Excel
        print(f"[5/5] Generando Excel...")
        excel_gen = ExcelGenerator(codigo_formato, df_formato, 'COLTRADE', 2025)
        archivo = excel_gen.generar_excel()
        nombre_archivo = excel_gen.obtener_nombre_archivo()
        tamaño_kb = len(archivo.getvalue()) / 1024

        print(f"[5/5] Excel generado: {nombre_archivo} ({tamaño_kb:.2f} KB)")
        print(f"[EXITO] Reporte {codigo_formato} generado correctamente")
        print(f"{'='*80}\n")

        # Enviar archivo
        return send_file(
            archivo,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=nombre_archivo
        )

    except Exception as e:
        print(f"[ERROR CRITICO] {str(e)}")
        import traceback
        traceback.print_exc()
        print(f"{'='*80}\n")

        return jsonify({
            'success': False,
            'message': f'Error al generar el reporte: {str(e)}'
        }), 500


@app.route('/debug', methods=['GET'])
def debug():
    """Endpoint de debug para diagnosticar problemas"""
    try:
        dataframe_id = session.get('dataframe_id', '')
        dataframe_path = ''
        file_exists = False

        if dataframe_id:
            dataframe_path = os.path.join(DATAFRAME_FOLDER, f'{dataframe_id}.pkl')
            file_exists = os.path.exists(dataframe_path)

        return jsonify({
            'session_id': dataframe_id,
            'file_path': dataframe_path,
            'file_exists': file_exists,
            'file_name': session.get('file_name', ''),
            'upload_time': session.get('upload_time', ''),
            'dataframe_folder': DATAFRAME_FOLDER,
            'folder_exists': os.path.exists(DATAFRAME_FOLDER),
            'temp_files': len(glob.glob(os.path.join(DATAFRAME_FOLDER, '*.pkl')))
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/clear-session', methods=['POST'])
def clear_session():
    """Limpia la sesión actual y archivos temporales"""
    try:
        # Eliminar archivo temporal si existe
        dataframe_id = session.get('dataframe_id', '')
        if dataframe_id:
            dataframe_path = os.path.join(DATAFRAME_FOLDER, f'{dataframe_id}.pkl')
            if os.path.exists(dataframe_path):
                os.remove(dataframe_path)

        # Limpiar sesión
        session.clear()
        return jsonify({'success': True, 'message': 'Sesión limpiada'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    """Maneja archivos demasiado grandes"""
    return jsonify({
        'success': False,
        'message': 'Archivo demasiado grande (máximo 50MB)'
    }), 413


@app.errorhandler(404)
def not_found(error):
    """Maneja rutas no encontradas"""
    return jsonify({
        'success': False,
        'message': 'Ruta no encontrada'
    }), 404


@app.errorhandler(500)
def server_error(error):
    """Maneja errores del servidor"""
    return jsonify({
        'success': False,
        'message': 'Error interno del servidor'
    }), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', '').lower() in {'1', 'true', 'yes'}

    print("=" * 60)
    print("GENERADOR DE REPORTES - MEDIOS MAGNÉTICOS COLTRADE")
    print("=" * 60)
    print(f"Iniciando aplicación en http://0.0.0.0:{port}")
    print("Presiona CTRL+C para detener el servidor")
    print("=" * 60)

    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        use_reloader=debug
    )
