#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test para verificar que el reporte 1001 se llena con datos de Odoo."""

import pandas as pd
from modules.data_processor import DataProcessor
from modules.odoo_client import OdooContactProvider
from modules.excel_generator import ExcelGenerator
import tempfile
import os

def crear_balance_test():
    """Crea un balance de prueba con NITs conocidos."""
    datos = {
        'Codigo': ['14350101', '14350102'],
        'Nombre de la Cuenta': ['Bancos', 'Caja'],
        'NIT': ['900901834-7', '900901834-7'],
        'Tercero': ['150 POR CIENTO SAS', '150 POR CIENTO SAS'],
        'Debito': [1000000.00, 500000.00],
        'Credito': [0.0, 0.0]
    }
    return pd.DataFrame(datos)

def main():
    print("=" * 70)
    print("TEST: GENERACION DE REPORTE 1001 CON DATOS DE ODOO")
    print("=" * 70)

    # 1. Crear balance de prueba
    print("\n[1] Creando balance de prueba...")
    df = crear_balance_test()
    print(f"    Balance creado: {len(df)} registros")

    # 2. Inicializar cliente de Odoo
    print("\n[2] Inicializando cliente de Odoo...")
    contact_provider = OdooContactProvider.from_environment()
    if not contact_provider:
        print("    [ERROR] No se pudieron cargar credenciales de Odoo")
        return False

    try:
        contact_provider._conectar()
        print(f"    [OK] Conectado a Odoo (UID: {contact_provider.uid})")
    except Exception as e:
        print(f"    [ERROR] No se pudo conectar: {e}")
        return False

    # 3. Procesar formato 1001
    print("\n[3] Procesando formato 1001...")
    try:
        processor = DataProcessor(df, contact_provider=contact_provider)
        df_1001 = processor.procesar_formato('1001')
        print(f"    [OK] Formato procesado: {len(df_1001)} registros")
    except Exception as e:
        print(f"    [ERROR] Error al procesar: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 4. Verificar campos de ubicacion
    print("\n[4] Verificando campos de ubicacion:")
    print(f"    Columnas en el DataFrame: {list(df_1001.columns)}")

    # Verificar columnas internas primero
    columnas_internas = ['direccion', 'dpto', 'municipio', 'pais']
    print("\n    Columnas internas (minusculas):")
    for col in columnas_internas:
        if col in df_1001.columns:
            valores_no_vacios = df_1001[col].notna().sum() - (df_1001[col] == '').sum()
            print(f"    - {col}: {valores_no_vacios} valores no vacios")
            if valores_no_vacios > 0:
                print(f"      Ejemplo: {df_1001[col].iloc[0]}")
        else:
            print(f"    [FALTA] {col}")

    print("\n    Columnas DIAN (mayusculas):")
    columnas_ubicacion = ['Direccion', 'Codigo dpto.', 'Codigo mcp', 'Pais de residencia o domicilio']
    for col in columnas_ubicacion:
        if col in df_1001.columns:
            valores_no_vacios = df_1001[col].notna().sum() - (df_1001[col] == '').sum()
            print(f"    - {col}: {valores_no_vacios} valores no vacios de {len(df_1001)}")
            if valores_no_vacios > 0:
                print(f"      Ejemplo: {df_1001[col].iloc[0]}")
        else:
            print(f"    [FALTA] {col}")

    # 5. Generar Excel
    print("\n[5] Generando archivo Excel...")
    try:
        excel_gen = ExcelGenerator('1001', df_1001, 'COLTRADE', 2025)
        archivo = excel_gen.generar_excel()

        # Guardar en temp
        temp_path = os.path.join(tempfile.gettempdir(), 'test_1001.xlsx')
        with open(temp_path, 'wb') as f:
            f.write(archivo.getvalue())

        print(f"    [OK] Excel generado: {temp_path}")
        print(f"    Tamano: {os.path.getsize(temp_path) / 1024:.1f} KB")
    except Exception as e:
        print(f"    [ERROR] Error al generar Excel: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n" + "=" * 70)
    print("[OK] PRUEBA COMPLETADA EXITOSAMENTE")
    print("=" * 70)
    return True

if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
