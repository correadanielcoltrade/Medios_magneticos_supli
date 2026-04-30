# Guía Rápida - Generador de Reportes con Nueva Estructura

## Paso 1: Preparar el Excel

Tu archivo debe tener **6 columnas** en este orden exacto:

| Columna | Nombre | Ejemplo |
|---------|--------|---------|
| A | Código | 1105050501 |
| B | Nombre de la cuenta | CAJA GENERAL |
| C | NIT del tercero | 900534936-5 |
| D | Nombre del tercero | CÁMARAS Y ALARMAS LAMSEG SAS |
| E | Débito | 354648834.14 |
| F | Crédito | 0.00 |

### Ejemplo Visual:

```
┌─────────────┬──────────────────┬────────────────┬────────────────────┬───────────┬──────────┐
│ Código      │ Nombre cuenta    │ NIT tercero    │ Nombre tercero     │ Débito    │ Crédito  │
├─────────────┼──────────────────┼────────────────┼────────────────────┼───────────┼──────────┤
│1105050501   │CAJA GENERAL      │900534936-5    │CÁMARAS LAMSEG      │354648834  │0         │
│1105050501   │CAJA GENERAL      │222222222-7    │CUANTÍAS MENORES    │350861055  │0         │
│1110010100   │CUENTA TRANS.     │860002964-4    │BANCO DE BOGOTÁ     │3032272800 │61000000  │
└─────────────┴──────────────────┴────────────────┴────────────────────┴───────────┴──────────┘
```

## Paso 2: Cargar el archivo en la aplicación

1. Abre http://localhost:5000
2. Selecciona tu archivo `balance_*.xlsx`
3. El sistema automáticamente detectará si es estructura nueva o antigua
4. Verás confirmación: "Archivo cargado correctamente"

## Paso 3: Generar reportes

Para cada formato deseado:

```
Formato 1001 → Retenciones
Formato 1005 → IVA Descontable
Formato 1006 → IVA Generado
Formato 1007 → Ingresos Recibidos
Formato 1008 → Cuentas por Cobrar
Formato 1009 → Cuentas por Pagar
Formato 2276 → Nómina
```

El Excel se generará automáticamente con:
- Título del reporte
- Encabezados profesionales
- Datos filtrados por patrón de cuenta
- Fila de TOTAL
- Formato de número automático
- Colores y estilos profesionales

## Paso 4: Descargar

El archivo se llamará:
```
Formato_1001_COLTRADE_2025.xlsx
Formato_1005_COLTRADE_2025.xlsx
etc...
```

## Ejemplo del Reporte Generado

```
╔════════════════════════════════════════════════╗
║ FORMATO 1001 - MEDIOS MAGNÉTICOS              ║
╠════════════════════════════════════════════════╣
║ Empresa: COLTRADE | Período: 2025             ║
║ Fecha: 24/04/2025                              ║
├──────────┬──────────────┬─────────┬─────────────┤
│ Código   │ Cuenta       │ Débito  │ Crédito     │
├──────────┼──────────────┼─────────┼─────────────┤
│2365001   │RETENCIÓN     │1,500.00 │0.00        │
│2366001   │RETENCIÓN     │2,000.00 │0.00        │
├──────────┼──────────────┼─────────┼─────────────┤
│TOTAL     │Suma saldos   │3,500.00 │0.00        │
└──────────┴──────────────┴─────────┴─────────────┘
```

## Compatibilidad

✓ **Nueva Estructura** (6 columnas) - RECOMENDADA
  - Incluye información de terceros
  - Más profesional y trazable
  
✓ **Estructura Antigua** (7 columnas) - SIGUE FUNCIONANDO
  - Sin cambios necesarios
  - Retrocompatible

## Verificación Rápida

Para verificar que tu estructura es correcta:

```bash
python test_balance_nueva.py
```

Deberías ver:
```
Validacion: OK
- Estructura correcta
- Tipo de estructura: Nueva
```

## Solución de Problemas

### "Se esperan al menos 6 columnas"
→ Tu Excel tiene menos de 6 columnas  
→ Verifica que tenga: Código, Nombre, NIT, Nombre Tercero, Débito, Crédito

### "No se encontraron datos para el formato"
→ Las cuentas en tu archivo no coinciden con el patrón del formato  
→ Revisa los patrones en CAMBIOS_REALIZADOS.md

### "Error al leer el archivo"
→ El archivo está corrupto o en formato incompatible  
→ Guarda como .xlsx (Excel 2007 o superior)

### "El archivo debe contener 'balance' en el nombre"
→ Renombra tu archivo a algo como: `balance_de_sumas_y_saldos.xlsx`

## Patrones de Filtrado

El sistema filtra cuentas automáticamente:

| Formato | Patrón | Busca cuentas que comiencen con: |
|---------|--------|----------------------------------|
| 1001 | 2365, 2366, 2x | 2365, 2366, o empiecen con 2 |
| 1005 | 24050 | 24050 |
| 1006 | 24051 | 24051 |
| 1007 | 4 | 4 |
| 1008 | 1205 | 1205 |
| 1009 | 2 | Empiecen con 2 |
| 2276 | 5105, 5205 | 5105 o 5205 |

**Ejemplo:** Si tu código es `24050123`, coincidirá con patrón `24050`

## Automatización Recomendada

El nombre de archivo debe:
```
✓ Contener "balance" (ej: balance_2025.xlsx)
✓ Ser formato .xlsx
✓ Tener 6 columnas en el orden correcto
```

Luego:
1. Carga → Sistema detecta automáticamente
2. Descarga → Reportes listos en segundos

¡Sin configuración manual! 🚀
