"""
Mapeo de cuentas contables a formularios.

La fuente oficial de parametros es el CSV "Cuentas medios magneticos 2024".
Cada fila contiene una cuenta PUC y hasta dos bloques de parametros DIAN:
Formulario, Concepto, Descripcion, Naturaleza y Ubicacion/Casilla.
"""

import csv
import os
import re


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARAMETROS_CUENTAS_PATH = os.path.join(
    BASE_DIR,
    'data',
    'cuentas_medios_magneticos_2024.csv',
)

NOMBRES_FORMULARIOS = {
    '1001': 'Pagos o abonos en cuenta y retenciones',
    '1003': 'Retenciones que le practicaron',
    '1005': 'IVA descontable',
    '1006': 'IVA generado',
    '1007': 'Ingresos recibidos',
    '1008': 'Cuentas por cobrar',
    '1009': 'Cuentas por pagar',
    '1012': 'Informacion de saldos de cuentas',
    '2276': 'Informacion de rentas de trabajo',
}


def _limpiar_texto(valor):
    if valor is None:
        return ''
    return ' '.join(str(valor).strip().split())


def _extraer_codigo_y_descripcion(cuenta_puc):
    cuenta_puc = _limpiar_texto(cuenta_puc)
    match = re.match(r'^(\d+)\s*(.*)$', cuenta_puc)
    if not match:
        return '', cuenta_puc
    return match.group(1), _limpiar_texto(match.group(2))


def _leer_csv_parametros(path):
    for encoding in ('utf-8-sig', 'cp1252', 'latin-1'):
        try:
            with open(path, newline='', encoding=encoding) as archivo:
                return list(csv.reader(archivo, delimiter=';'))
        except UnicodeDecodeError:
            continue
        except FileNotFoundError:
            return []
    return []


def _campo(row, idx):
    if idx >= len(row):
        return ''
    return _limpiar_texto(row[idx])


def _extraer_parametros_cuentas(path=PARAMETROS_CUENTAS_PATH):
    rows = _leer_csv_parametros(path)
    if not rows:
        return {}

    header_idx = None
    for idx, row in enumerate(rows):
        if any(_limpiar_texto(cell).lower() == 'cuenta puc' for cell in row):
            header_idx = idx
            break

    if header_idx is None:
        return {}

    header = rows[header_idx]
    indices_formulario = [
        idx for idx, cell in enumerate(header)
        if _limpiar_texto(cell).lower() == 'formulario'
    ]

    parametros = {}
    for row in rows[header_idx + 1:]:
        cuenta_puc = _campo(row, 1)
        codigo_cuenta, descripcion_cuenta = _extraer_codigo_y_descripcion(cuenta_puc)
        if not codigo_cuenta:
            continue

        for idx_formulario in indices_formulario:
            formulario = _campo(row, idx_formulario)
            if not formulario:
                continue

            concepto = _campo(row, idx_formulario + 1)
            descripcion_parametro = _campo(row, idx_formulario + 2)
            naturaleza = _campo(row, idx_formulario + 3)
            ubicacion = _campo(row, idx_formulario + 4)

            parametros.setdefault(formulario, {})
            if codigo_cuenta in parametros[formulario]:
                continue

            parametros[formulario][codigo_cuenta] = {
                'cuenta_puc': cuenta_puc,
                'concepto': concepto,
                'descripcion': descripcion_cuenta or descripcion_parametro,
                'descripcion_cuenta': descripcion_cuenta,
                'descripcion_parametro': descripcion_parametro,
                'naturaleza': naturaleza,
                'ubicacion': ubicacion,
            }

    return parametros


PARAMETROS_CUENTAS_FORMULARIO = _extraer_parametros_cuentas()

# Mapeo especializado para Formato 1001.
MAPEO_FORMATO_1001 = {
    codigo: parametros.copy()
    for codigo, parametros in PARAMETROS_CUENTAS_FORMULARIO.get('1001', {}).items()
}


# Mapeo de cuentas a formularios.
MAPEO_CUENTAS_FORMULARIO = {
    codigo_formulario: {
        'nombre': NOMBRES_FORMULARIOS.get(codigo_formulario, f'Formato {codigo_formulario}'),
        'cuentas_patron': list(parametros.keys()),
        'parametros': {codigo: datos.copy() for codigo, datos in parametros.items()},
    }
    for codigo_formulario, parametros in PARAMETROS_CUENTAS_FORMULARIO.items()
}


def obtener_codigo_parametro_formulario(codigo_formulario, codigo_cuenta):
    """
    Retorna la cuenta parametrizada que aplica a una cuenta del balance.

    Primero intenta coincidencia exacta. Si el balance viene con subcuentas mas
    detalladas, usa la cuenta parametrizada mas larga que sea prefijo.
    """
    codigo_cuenta = _limpiar_texto(codigo_cuenta).replace('.0', '')
    parametros = MAPEO_CUENTAS_FORMULARIO.get(codigo_formulario, {}).get('parametros', {})
    if codigo_cuenta in parametros:
        return codigo_cuenta

    coincidencias = [
        codigo_parametro for codigo_parametro in parametros
        if codigo_parametro and codigo_cuenta.startswith(str(codigo_parametro))
    ]
    if not coincidencias:
        return ''
    return max(coincidencias, key=len)


def obtener_parametro_cuenta(codigo_formulario, codigo_cuenta):
    """Obtiene los parametros DIAN aplicables a una cuenta del balance."""
    codigo_parametro = obtener_codigo_parametro_formulario(codigo_formulario, codigo_cuenta)
    if not codigo_parametro:
        return None
    parametros = MAPEO_CUENTAS_FORMULARIO[codigo_formulario]['parametros'][codigo_parametro].copy()
    parametros['codigo_parametro'] = codigo_parametro
    return parametros


def obtener_formulario_por_cuenta(codigo_cuenta):
    """
    Obtiene el formulario correspondiente a una cuenta.

    Returns:
        (codigo_formulario, nombre_formulario) o (None, None)
    """
    for codigo_formulario, config in MAPEO_CUENTAS_FORMULARIO.items():
        if obtener_codigo_parametro_formulario(codigo_formulario, codigo_cuenta):
            return codigo_formulario, config['nombre']

    return None, None


def obtener_cuentas_por_formulario(codigo_formulario):
    """
    Obtiene todas las cuentas parametrizadas de un formulario.

    Returns:
        Lista de cuentas o lista vacia.
    """
    if codigo_formulario in MAPEO_CUENTAS_FORMULARIO:
        return MAPEO_CUENTAS_FORMULARIO[codigo_formulario]['cuentas_patron']
    return []


def obtener_mapa_formato_1001():
    """Retorna el mapeo cuenta -> parametros del formato 1001."""
    return {codigo: datos.copy() for codigo, datos in MAPEO_FORMATO_1001.items()}
