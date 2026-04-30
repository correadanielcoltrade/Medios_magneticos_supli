# Cambios Realizados - Adaptación a Nueva Estructura de Balance

## Resumen
Se ha actualizado completamente la lógica del procesamiento de datos para soportar la **nueva estructura del Balance de Sumas y Saldos** sin perder compatibilidad con la estructura antigua.

## Estructura Nueva vs Antigua

### Estructura Antigua (7 columnas)
```
Código | Balance Inicial D | Balance Inicial C | Movimiento D | Movimiento C | Balance Final D | Balance Final C
```

### Estructura Nueva (6 columnas) - AHORA SOPORTADA
```
Código | Nombre de la cuenta | NIT del tercero | Nombre del tercero | Débito | Crédito
```

## Cambios en data_processor.py

### 1. Detección Automática de Estructura
Se agregó el método `_detectar_estructura()` que:
- Identifica automáticamente si es estructura nueva o antigua
- Busca palabras clave como "Débito" y "Crédito" en las columnas
- Almacena el tipo de estructura en `self.estructura_nueva`

### 2. Normalización Mejorada
`_normalize_dataframe()` ahora:
- Detecta la estructura de forma inteligente
- Mapea correctamente las columnas según el tipo
- Establece nombres de columna estandarizados internamente

### 3. Procesamiento Dual
El método `procesar_formato()` ahora:
- Delega al método `_procesar_formato_nuevo()` para estructura nueva
- Delega al método `_procesar_formato_antiguo()` para estructura antigua
- Mantiene lógica separada para cada tipo

### 4. Nueva Función: _procesar_formato_nuevo()
```python
- Extrae código, nombre cuenta, NIT y nombre tercero
- Valida que el código sea numérico
- Aplica filtros de patrón de cuenta
- Genera DataFrame con columnas: Código, Cuenta, NIT Tercero, Nombre Tercero, Débito, Crédito, Saldo
- Agrega automáticamente fila de TOTAL
```

### 5. Validación Actualizada
`validar_estructura()` ahora:
- Acepta mínimo 6 columnas (era 7)
- Valida columnas numéricas dinámicamente según el tipo
- Proporciona mensajes de error más claros

## Cambios en excel_generator.py

### Estilos Dinámicos
Se mejoró `_aplicar_estilos_datos()` para:
- Detectar automáticamente columnas numéricas
- Buscar por nombre de columna ("Débito", "Crédito", "Saldo", "Balance", "Movimiento")
- Aplicar formato '#,##0.00' solo a columnas numéricas
- Funciona con cualquier estructura de datos

## Cómo Usar

### 1. Para archivos con estructura NUEVA (Recomendado)
Asegúrate de que tu Excel tenga estas 6 columnas en este orden:
```
1. Código (ejemplo: 1105050501)
2. Nombre de la cuenta (ejemplo: CAJA GENERAL)
3. NIT del tercero (ejemplo: 900534936-5)
4. Nombre del tercero (ejemplo: CÁMARAS Y ALARMAS LAMSEG SAS)
5. Débito (valores numéricos)
6. Crédito (valores numéricos)
```

**Ventajas:**
- Información de terceros incluida
- Estructura más clara y profesional
- Mejor trazabilidad de datos

### 2. Para archivos con estructura ANTIGUA (Sigue funcionando)
Si tienes archivos antiguos con 7 columnas, **siguen funcionando sin cambios**.

## Flujo de Procesamiento

```
1. Usuario carga balance_*.xlsx
   ↓
2. app.py → DataProcessor.validar_estructura()
   ↓
3. DataProcessor._detectar_estructura()
   - Identifica si es nueva o antigua
   ↓
4. app.py → DataProcessor.procesar_formato(codigo)
   ↓
5. _procesar_formato_nuevo() O _procesar_formato_antiguo()
   - Filtra por patrones de cuenta
   - Genera DataFrame con columnas correspondientes
   ↓
6. ExcelGenerator.generar_excel()
   - Aplica estilos dinámicamente
   - Formato numérico automático
   ↓
7. Usuario descarga Formato_XXXX_COLTRADE_2025.xlsx
```

## Archivos Modificados

1. **modules/data_processor.py**
   - Agregado: `_detectar_estructura()`
   - Modificado: `_normalize_dataframe()`
   - Modificado: `procesar_formato()`
   - Agregado: `_procesar_formato_nuevo()`
   - Agregado: `_procesar_formato_antiguo()`
   - Modificado: `validar_estructura()`

2. **modules/excel_generator.py**
   - Modificado: `_aplicar_estilos_datos()`
   - Ahora detecta columnas numéricas dinámicamente

## Archivos de Prueba Incluidos

1. **test_balance_nueva.py** - Script de prueba unitaria
2. **create_test_excel.py** - Genera archivo Excel de prueba
3. **balance_de_sumas_y_saldos_TEST.xlsx** - Archivo de ejemplo con datos reales

## Testing

Para probar el nuevo sistema:

```bash
# Ejecutar pruebas unitarias
python test_balance_nueva.py

# Ver resultado esperado:
# - Validacion: OK
# - Tipo de estructura: Nueva
# - Columnas detectadas correctamente
```

## Patrones de Cuenta por Formato

| Formato | Descripción | Patrón de Cuentas |
|---------|-------------|------------------|
| 1001 | Retenciones | 2365, 2366, 2x |
| 1005 | IVA descontable | 24050 |
| 1006 | IVA generado | 24051 |
| 1007 | Ingresos | 4 |
| 1008 | Cuentas por cobrar | 1205 |
| 1009 | Cuentas por pagar | 2 |
| 2276 | Nómina | 5105, 5205 |

## Notas Importantes

✓ Retrocompatible con estructura antigua  
✓ Detección automática - no requiere configuración  
✓ Estilos dinámicos en Excel  
✓ Soporta información de terceros  
✓ Validación robusta de estructura  

## Próximos Pasos Opcionales

1. Actualizar template de carga para indicar estructura esperada
2. Agregar más formatos según necesidad
3. Permitir mapeo personalizado de patrones de cuenta
4. Agregar filtros por NIT o nombre de tercero en la UI
