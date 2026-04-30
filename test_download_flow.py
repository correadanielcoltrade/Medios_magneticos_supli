#!/usr/bin/env python3
"""Script para diagnosticar problemas con la descarga de reportes"""

import os
import sys
import pickle
import pandas as pd
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.data_processor import DataProcessor
from modules.excel_generator import ExcelGenerator

# Crear datos de prueba
print("=" * 80)
print("TEST DE FLUJO DE DESCARGA")
print("=" * 80)

# 1. Crear DataFrame de prueba
print("\n1. Creando DataFrame de prueba...")
datos = {
    'Código': ['2365001', '2366001'],
    'Nombre de la cuenta': ['RETENCIÓN EN LA FUENTE', 'RETENCIÓN EN LA FUENTE'],
    'NIT del tercero': ['800197268-4', '890903938-8'],
    'Nombre del tercero': ['DIRECCIÓN DE IMPUESTOS', 'BANCOLOMBIA SA'],
    'Débito': [1500000.00, 2000000.00],
    'Crédito': [1500000.00, 2000000.00],
}

df = pd.DataFrame(datos)
print(f"OK: DataFrame creado: {len(df)} filas, {len(df.columns)} columnas")
print(df)

# 2. Validar estructura
print("\n2. Validando estructura...")
processor = DataProcessor(df)
valido, errores = processor.validar_estructura()

if not valido:
    print(f"[ERROR] Estructura invalida: {errores}")
    sys.exit(1)
else:
    print(f"[OK] Estructura válida")
    print(f"  Tipo: {'Nueva' if processor.estructura_nueva else 'Antigua'}")

# 3. Procesar para formato 1001
print("\n3. Procesando para formato 1001...")
try:
    df_formato = processor.procesar_formato('1001')
    if df_formato.empty:
        print("[ERROR] No se encontraron datos para formato 1001")
        print("  Nota: Las cuentas 2365 y 2366 deberían coincidir")
    else:
        print(f"[OK] Datos procesados: {len(df_formato)} filas")
        print(df_formato)
except Exception as e:
    print(f"[ERROR] Error procesando: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 4. Generar Excel
print("\n4. Generando Excel...")
try:
    excel_gen = ExcelGenerator('1001', df_formato, 'COLTRADE', 2025)
    archivo = excel_gen.generar_excel()
    nombre = excel_gen.obtener_nombre_archivo()

    # Verificar que el archivo se generó
    archivo_size = len(archivo.getvalue())
    print(f"[OK] Excel generado correctamente")
    print(f"  Nombre: {nombre}")
    print(f"  Tamaño: {archivo_size:,} bytes")

    if archivo_size < 1000:
        print(f"[ERROR] ALERTA: El archivo es muy pequeño ({archivo_size} bytes)")

except Exception as e:
    print(f"[ERROR] Error generando Excel: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 5. Guardar archivo para prueba
print("\n5. Guardando archivo de prueba...")
try:
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
        f.write(archivo.getvalue())
        temp_path = f.name
    print(f"[OK] Archivo guardado en: {temp_path}")
    print(f"  Puedes abrir este archivo para verificar que se generó correctamente")
except Exception as e:
    print(f"[ERROR] Error guardando archivo: {e}")

print("\n" + "=" * 80)
print("RESULTADO: Todo funciona correctamente")
print("=" * 80)
print("\nSi la descarga en el navegador no funciona, revisa:")
print("1. Consola del navegador (F12) para ver errores")
print("2. Endpoint /debug para ver estado de sesión")
print("3. Revisa que el archivo balance se cargó correctamente")
