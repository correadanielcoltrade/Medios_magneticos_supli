#!/usr/bin/env python3
"""Script de prueba para validar la nueva estructura de balance"""

import pandas as pd
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.data_processor import DataProcessor

# Crear DataFrame de prueba con la nueva estructura
datos_prueba = {
    'Código': [
        '1105050501', '1105050501', '1105050501', '1105050501',
        '1105051002', '1105051002',
        '1110010100', '1110010100', '1110010100',
        '1110020100', '1110020100',
    ],
    'Nombre de la cuenta': [
        'CAJA GENERAL', 'CAJA GENERAL', 'CAJA GENERAL', 'CAJA GENERAL',
        'CAJA PAGOS LOGÍSTICOS', 'CAJA PAGOS LOGÍSTICOS',
        'CUENTA TRANSITORIA', 'CUENTA TRANSITORIA', 'CUENTA TRANSITORIA',
        'COBROS PENDIENTES', 'COBROS PENDIENTES',
    ],
    'NIT del tercero': [
        '900534936-5', '222222222-7', '800197268-4', '900538486-0',
        '1007702540', '1073715452',
        '860002964-4', '890903938-8', '1020750460',
        '900898056-0', '1018498580',
    ],
    'Nombre del tercero': [
        'CÁMARAS Y ALARMAS LAMSEG SAS', 'CUANTÍAS MENORES',
        'DIRECCIÓN DE IMPUESTOS Y ADUANAS NACIONALES', 'ESAR SOLUCIONES LOGÍSTICAS S.A.S',
        'CAJAMARCA MORA JUAN MANUEL', 'SOGAMOSO LATORRE JUAN PABLO',
        'BANCO DE BOGOTÁ', 'BANCOLOMBIA SA', 'ORDOÑEZ ARENAS JUAN CAMILO',
        'MEMORIAS MICROS Y PARTES S A S', 'RAMÍREZ NAVARRO JULIAN DAVID',
    ],
    'Débito': [
        354648834.144, 350861055.385, 74418823.657, 74160394.966,
        420370.00, 420370.00,
        3032272800.31, 2823881780.17, 287000000.00,
        226000000.00, 226000000.00,
    ],
    'Crédito': [
        0, 0, 0, 0,
        420370.00, 420370.00,
        61000000.00, 61000000.00, 61000000.00,
        0, 0,
    ],
}

df = pd.DataFrame(datos_prueba)

print("=" * 80)
print("PRUEBA DE NUEVA ESTRUCTURA DE BALANCE")
print("=" * 80)
print("\nDatos de entrada:")
print(df.to_string())

# Crear procesador
processor = DataProcessor(df)

# Validar estructura
valido, errores = processor.validar_estructura()
print(f"\nValidacion: {'OK' if valido else 'ERROR'}")
if errores:
    for error in errores:
        print(f"  - {error}")
else:
    print(f"  - Estructura correcta")
    print(f"  - Columnas detectadas: {processor.columnas}")
    print(f"  - Tipo de estructura: {'Nueva' if processor.estructura_nueva else 'Antigua'}")

# Procesar para formato 1005 (IVA descontable - cuentas 24050)
print("\n" + "=" * 80)
print("Procesando formato 1005 (IVA descontable)")
print("=" * 80)
try:
    # Usar cuenta que no existe para demostrar filtrado
    df_formato = processor.procesar_formato('1005')
    if df_formato.empty:
        print("No se encontraron cuentas 24050 en los datos de prueba")
    else:
        print("\nResultado:")
        print(df_formato.to_string())
except Exception as e:
    print(f"ERROR: {e}")

# Procesar para formato 1008 (CXC - cuentas 1205, 11xx)
print("\n" + "=" * 80)
print("Procesando formato 1008 (Cuentas por cobrar)")
print("=" * 80)
try:
    df_formato = processor.procesar_formato('1008')
    if df_formato.empty:
        print("No se encontraron cuentas 1205 en los datos de prueba")
        print("Intentando con patrón 1105, 1110...")
        # Los datos tienen 1105 y 1110, vamos a verificar si se detectan
    else:
        print("\nResultado:")
        print(df_formato.to_string())
except Exception as e:
    print(f"ERROR: {e}")

# Procesar para formato 1001 (Retenciones - cuentas 2365, 2366, 2x)
print("\n" + "=" * 80)
print("Procesando formato 1001 (Retenciones)")
print("=" * 80)
try:
    df_formato = processor.procesar_formato('1001')
    if df_formato.empty:
        print("No se encontraron cuentas que coincidan con el patrón 2x")
    else:
        print("\nResultado:")
        print(df_formato.to_string())
except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "=" * 80)
print("Prueba completada")
print("=" * 80)
