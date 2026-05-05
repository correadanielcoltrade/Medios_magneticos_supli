#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script de prueba para validar conexión a Odoo y traer contactos."""

import sys
import os
from modules.odoo_client import OdooContactProvider

def main():
    print("=" * 60)
    print("PRUEBA DE CONEXION A ODOO")
    print("=" * 60)

    # Intentar conectar
    print("\n1. Inicializando cliente de Odoo desde .env...")
    provider = OdooContactProvider.from_environment()

    if provider is None:
        print("[ERROR] No se pudieron cargar las credenciales del .env")
        print("   Verifica que el archivo .env contenga:")
        print("   - ODOO_URL")
        print("   - ODOO_DB")
        print("   - ODOO_USER")
        print("   - ODOO_PASSWORD o ODOO_API_KEY")
        return False

    print("[OK] Credenciales cargadas:")
    print(f"   URL: {provider.url}")
    print(f"   DB: {provider.db}")
    print(f"   Usuario: {provider.user}")

    # Intentar conectar
    print("\n2. Conectando a Odoo...")
    try:
        provider._conectar()
        print(f"[OK] Conectado exitosamente (UID: {provider.uid})")
    except Exception as e:
        print(f"[ERROR] Error de conexion: {e}")
        return False

    # Obtener campos disponibles
    print("\n3. Verificando campos disponibles en res.partner...")
    try:
        campos = provider._partner_campos()
        campos_importantes = ['vat', 'street', 'street2', 'city', 'city_id', 'state_id', 'country_id']
        print("   Campos encontrados:")
        for campo in campos_importantes:
            if campo in campos:
                print(f"   [OK] {campo}")
            else:
                print(f"   [NO] {campo}")
    except Exception as e:
        print(f"[ERROR] Error al obtener campos: {e}")
        return False

    # Probar con un NIT de ejemplo
    print("\n4. Intentando traer contacto de prueba...")
    print("   (Buscaremos cualquier contacto con NIT en Odoo)")

    try:
        # Primero, buscar cualquier contacto para ver si hay datos
        todos_contactos = provider._execute_kw(
            'res.partner',
            'search_read',
            [[('vat', '!=', False)]],
            {'fields': ['vat', 'name'], 'limit': 3}
        )

        if not todos_contactos:
            print("   [AVISO] No hay contactos con NIT en Odoo")
            print("      Prueba manualmente con un NIT conocido")
            return True

        print(f"   Encontrados {len(todos_contactos)} contactos con NIT:")
        for contacto in todos_contactos:
            nit = contacto.get('vat', 'Sin NIT')
            nombre = contacto.get('name', 'Sin nombre')
            print(f"   - NIT: {nit}, Nombre: {nombre}")

            # Obtener detalles del primer contacto
            if nit != 'Sin NIT':
                print(f"\n   Obteniendo detalles para NIT: {nit}")
                detalles = provider.obtener_contacto(nit)
                if detalles:
                    print(f"   [OK] Datos obtenidos:")
                    print(f"      - Direccion: {detalles.get('direccion', 'N/A')}")
                    print(f"      - Departamento: {detalles.get('dpto', 'N/A')}")
                    print(f"      - Municipio: {detalles.get('municipio', 'N/A')}")
                    print(f"      - Pais: {detalles.get('pais', 'N/A')}")
                else:
                    print(f"   [AVISO] No se obtuvieron detalles")
                break

    except Exception as e:
        print(f"[ERROR] Error al obtener contactos: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n" + "=" * 60)
    print("[OK] PRUEBA COMPLETADA EXITOSAMENTE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
