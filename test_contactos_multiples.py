#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test para verificar que se obtienen multiples contactos en diferentes formatos."""

from modules.odoo_client import OdooContactProvider
import time

def main():
    print("=" * 70)
    print("TEST: OBTENCION DE MULTIPLES CONTACTOS")
    print("=" * 70)

    # Conectar a Odoo
    provider = OdooContactProvider.from_environment()
    if not provider:
        print("[ERROR] Credenciales no cargadas")
        return False

    try:
        provider._conectar()
        print(f"[OK] Conectado a Odoo (UID: {provider.uid})")
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

    # Primero, obtener algunos NITs reales de Odoo
    print("\n[1] Obteniendo NITs reales de Odoo...")
    try:
        contactos_reales = provider._execute_kw(
            'res.partner',
            'search_read',
            [[('vat', '!=', False)]],
            {'fields': ['vat', 'name'], 'limit': 10}
        )
        nits_reales = [c['vat'] for c in contactos_reales if c.get('vat')]
        print(f"    NITs encontrados: {len(nits_reales)}")
        for c in contactos_reales[:5]:
            print(f"    - {c['vat']}: {c['name']}")
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

    if not nits_reales:
        print("[ERROR] No hay NITs en Odoo para probar")
        return False

    # Test: Obtener multiples contactos
    print(f"\n[2] Probando obtener_contactos con {len(nits_reales)} NITs...")
    inicio = time.time()
    contactos = provider.obtener_contactos(nits_reales)
    elapsed = time.time() - inicio
    print(f"    Tiempo: {elapsed:.2f} segundos")
    print(f"    Contactos obtenidos: {len(contactos)}")

    # Verificar cuantos tienen datos
    con_datos = sum(1 for c in contactos.values() if c.get('direccion') or c.get('dpto') or c.get('municipio'))
    print(f"    Con datos de ubicacion: {con_datos}/{len(contactos)}")

    # Mostrar algunos resultados
    print("\n[3] Detalles de los primeros contactos:")
    for nit in list(contactos.keys())[:5]:
        datos = contactos[nit]
        print(f"\n    NIT: {nit}")
        print(f"      Direccion: {datos.get('direccion', 'VACIO')}")
        print(f"      Dpto: {datos.get('dpto', 'VACIO')}")
        print(f"      Municipio: {datos.get('municipio', 'VACIO')}")
        print(f"      Pais: {datos.get('pais', 'VACIO')}")

    # Test 2: Probar con NIT en diferentes formatos
    print("\n[4] Probando NIT en diferentes formatos...")
    nit_base = nits_reales[0]
    formatos_prueba = [
        nit_base,                           # Original
        nit_base.replace('-', ''),          # Sin guión
        nit_base + '.0',                    # Con .0 (como viene de Excel)
    ]

    # Limpiar cache para forzar nueva busqueda
    provider._cache = {}

    inicio = time.time()
    contactos_formatos = provider.obtener_contactos(formatos_prueba)
    elapsed = time.time() - inicio
    print(f"    Tiempo: {elapsed:.2f} segundos")

    for nit_fmt in formatos_prueba:
        datos = contactos_formatos.get(nit_fmt, {})
        tiene_datos = bool(datos.get('direccion'))
        print(f"    Formato '{nit_fmt}': {'CON DATOS' if tiene_datos else 'SIN DATOS'}")

    print("\n" + "=" * 70)
    print("[OK] PRUEBA COMPLETADA")
    print("=" * 70)
    return True

if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
