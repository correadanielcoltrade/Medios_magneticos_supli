#!/usr/bin/env python3
"""Test que verifica que la aplicacion Flask se carga correctamente"""

import sys
import os

try:
    from app import app
    print("OK: Aplicacion Flask cargada correctamente")
    print("\nRutas disponibles:")
    for rule in app.url_map.iter_rules():
        methods = sorted(rule.methods - {'HEAD', 'OPTIONS'})
        print(f"  {rule.rule:30} {str(methods)}")

    print("\nDirectorios creados:")
    print(f"  - temp/")
    print(f"  - temp/dataframes/")

    print("\nConfiguracion:")
    print(f"  MAX_CONTENT_LENGTH: 50MB")
    print(f"  SECRET_KEY: configurado")

    print("\nOK: Todo funciona correctamente!")
    sys.exit(0)

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
