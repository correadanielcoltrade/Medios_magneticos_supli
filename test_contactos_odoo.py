#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test para ver si obtener_contactos está funcionando."""

from modules.odoo_client import OdooContactProvider
import pandas as pd

def main():
    print("=" * 70)
    print("TEST: OBTENCION DE CONTACTOS DE ODOO")
    print("=" * 70)

    # Conectar a Odoo
    print("\n[1] Conectando a Odoo...")
    provider = OdooContactProvider.from_environment()
    if not provider:
        print("    [ERROR] Credenciales no cargadas")
        return False

    try:
        provider._conectar()
        print(f"    [OK] Conectado (UID: {provider.uid})")
    except Exception as e:
        print(f"    [ERROR] {e}")
        return False

    # Obtener un contacto
    print("\n[2] Obteniendo contacto por NIT...")
    nit = '900901834-7'
    print(f"    Buscando NIT: {nit}")

    try:
        contacto = provider.obtener_contacto(nit)
        print(f"    [OK] Contacto obtenido")
        print(f"    - Direccion: {contacto.get('direccion', 'N/A')}")
        print(f"    - Dpto: {contacto.get('dpto', 'N/A')}")
        print(f"    - Municipio: {contacto.get('municipio', 'N/A')}")
        print(f"    - Pais: {contacto.get('pais', 'N/A')}")
    except Exception as e:
        print(f"    [ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

    # Obtener multiples contactos
    print("\n[3] Obteniendo multiples contactos...")
    nits = ['900901834-7']
    try:
        contactos = provider.obtener_contactos(nits)
        print(f"    [OK] Se obtuvieron {len(contactos)} contactos")
        for nit_key, datos in contactos.items():
            print(f"    NIT {nit_key}:")
            print(f"      - Direccion: {datos.get('direccion', 'N/A')}")
            print(f"      - Dpto: {datos.get('dpto', 'N/A')}")
            print(f"      - Municipio: {datos.get('municipio', 'N/A')}")
            print(f"      - Pais: {datos.get('pais', 'N/A')}")
    except Exception as e:
        print(f"    [ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

    # Crear un Series con NITs como en el DataProcessor
    print("\n[4] Simulando lo que hace DataProcessor...")
    df = pd.DataFrame({
        'nit': ['900901834-7', '900901834-7']
    })
    print(f"    DataFrame con NITs: {df['nit'].tolist()}")

    try:
        contactos = provider.obtener_contactos(df['nit'].tolist())
        print(f"    [OK] Contactos obtenidos: {len(contactos)}")
        for nit, datos in contactos.items():
            print(f"    - {nit}: {datos}")
    except Exception as e:
        print(f"    [ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n" + "=" * 70)
    print("[OK] PRUEBA COMPLETADA")
    print("=" * 70)
    return True

if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
