"""
Configuración de ejemplo para la aplicación
Copia este archivo a config.py y ajusta los valores según tus necesidades
"""

# ==================== CONFIGURACIÓN DE LA APLICACIÓN ====================

# Información de la empresa
EMPRESA_NOMBRE = 'COLTRADE'
EMPRESA_NIT = '123.456.789-0'
ANIO_REPORTE = 2024

# Puerto y host
HOST = 'localhost'
PORT = 5000
DEBUG = True

# Tamaño máximo de archivo (en bytes)
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# Secret key para sesiones (cambiar en producción)
SECRET_KEY = 'coltrade_medios_magneticos_2025'

# ==================== INTEGRACIÓN ODOO ====================

# Configurar estos valores como variables de entorno o en un archivo local .env.
# ODOO_URL = 'https://tuempresa.odoo.com'
# ODOO_DB = 'tu_base_odoo'
# ODOO_USER = 'usuario@empresa.com'
# ODOO_API_KEY = 'api_key_generada_en_odoo'

# ==================== CONFIGURACIÓN DE FORMATOS ====================

FORMATOS = {
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

# ==================== ESTILOS ====================

# Colores para Excel
COLORES = {
    'header': 'FF1F4E78',      # Azul oscuro
    'subheader': 'FF4472C4',   # Azul claro
    'total': 'FFFFE699',       # Amarillo
    'alternado': 'FFDEEBF7'    # Azul muy claro
}

# ==================== VALIDACIONES ====================

# Extensiones permitidas
ALLOWED_EXTENSIONS = {'xlsx'}

# Nombre del archivo que se debe cargar
REQUIRED_FILE_NAME = 'balance'

# Columnas esperadas mínimas
MIN_COLUMNS = 7

# ==================== LOGGING ====================

LOG_LEVEL = 'DEBUG'  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = 'logs/app.log'
