# Nuevo: Indicador de Progreso para Descargas

## ¿Qué es Nuevo?

Ahora cuando haces click en un reporte para descargarlo, verás:

1. **Barra de Progreso Visual** - Del 0% al 100%
2. **Porcentaje en Tiempo Real** - Número que actualiza
3. **Mensaje "Generando reporte..."** - Confirma que está funcionando
4. **Logs en Consola del Servidor** - Para debugging

---

## Cómo Funciona

### Flujo Visual en el Navegador

```
ANTES (sin feedback):
Click → Esperar → ?? → Descarga o silencio

AHORA (con feedback):
Click → 0% → 25% → 50% → 75% → 100% → Descarga
        Barra de progreso + Porcentaje visible
```

### Pasos para Descargar

1. **Carga tu archivo** `balance_*.xlsx`
   - Espera a que se cargue

2. **Haz click en un formato** (ej: Formato 1001)
   - Verás la barra de progreso aparecer
   - El porcentaje aumentará de 0% a 100%

3. **Espera a que llegue a 100%**
   - El archivo se descargará automáticamente
   - Verás un mensaje de éxito

---

## Indicadores Visuales

### Barra de Progreso

```
┌─────────────────────────────────────┐
│ ████████░░░░░░░░░░░░░░░░░░░░░░░░░░ │  50%
│                                       │
│      Generando reporte...            │
└─────────────────────────────────────┘
```

**Colores:**
- 🟦 Azul → Progreso
- 🟩 Verde → Progreso final
- ⬜ Gris → Pendiente

### Estados

| Estado | Descripción |
|--------|-------------|
| 0% | Iniciando generación |
| 25% | Validando datos |
| 50% | Procesando formato |
| 75% | Generando Excel |
| 100% | Descargando |

---

## Logs en la Consola del Servidor

Cuando descargas un reporte, en la consola verás:

```
================================================================================
[DESCARGA] Iniciando generación de Formato 1001
================================================================================
[1/5] Validando sesión... dataframe_id=abc123-uuid-def456
[2/5] Verificando archivo... temp/dataframes/abc123-uuid-def456.pkl
[3/5] Cargando DataFrame desde temp/dataframes/abc123-uuid-def456.pkl...
[3/5] DataFrame cargado: 50 filas, 6 columnas
[4/5] Procesando datos para formato 1001...
[4/5] Datos procesados: 10 filas (incluyendo totales)
[5/5] Generando Excel...
[5/5] Excel generado: Formato_1001_COLTRADE_2025.xlsx (12.50 KB)
[EXITO] Reporte 1001 generado correctamente
================================================================================
```

**Cómo leer los logs:**

- `[1/5]` = Paso 1 de 5
- `[3/5] DataFrame cargado` = Éxito cargando datos
- `[4/5] Datos procesados` = Datos filtrados correctamente
- `[EXITO]` = Reporte completado sin errores

### Si Hay un Error

Verás algo como:

```
[ERROR] No hay dataframe_id en sesión
[ERROR] Archivo no encontrado: temp/dataframes/abc123.pkl
[ERROR] No se encontraron datos para el patrón de 1001
[ERROR CRITICO] AttributeError: ...
```

---

## Debugging: Qué Revisar Si No Funciona

### 1. **Revisa la Consola del Navegador (F12)**

```
Abre: DevTools → Consola (Console)
Busca: [DESCARGA] o [PROGRESO]
```

Deberías ver:
```
[DESCARGA] Iniciando generación de reporte Formato 1001...
[PROGRESO] Formato 1001: 0%
[PROGRESO] Formato 1001: 25%
[PROGRESO] Formato 1001: 50%
[PROGRESO] Formato 1001: 75%
[PROGRESO] Formato 1001: 100%
[DESCARGA] Completado en 2.35s
```

### 2. **Revisa la Consola del Servidor**

```
Donde ejecutas: python app.py

Busca: [DESCARGA], [ERROR], [EXITO]
```

### 3. **Endpoint de Debug**

```
Abre: http://localhost:5000/debug

Verifica:
✓ session_id está lleno
✓ file_exists = true
✓ file_name está correcto
```

---

## Casos Comunes

### Caso 1: Barra llega a 100% pero no descarga

**Problema:** Permisos del navegador para descargas automáticas  
**Solución:**
- Revisa configuración del navegador
- Permite descargas automáticas para localhost
- Intenta con otro navegador

### Caso 2: La barra se queda en 50%

**Problema:** Error al procesar datos  
**Solución:**
- Revisa logs del servidor
- Busca `[ERROR]` en los logs
- Verifica que el archivo balance sea correcto

### Caso 3: Barra de progreso no aparece

**Problema:** JavaScript no está funcionando  
**Solución:**
- Recarga la página (F5)
- Limpia caché (Ctrl+Shift+Delete)
- Abre consola (F12) y busca errores en rojo

### Caso 4: Logs del servidor están vacíos

**Problema:** Servidor no está procesando la solicitud  
**Solución:**
- Verifica que Python está ejecutándose
- Reinicia: `python app.py`
- Verifica que el puerto 5000 está disponible

---

## Tiempos Esperados

| Acción | Tiempo Esperado |
|--------|-----------------|
| Cargar archivo (100 filas) | 1-2 segundos |
| Generar reporte | 0.5-2 segundos |
| Total | 2-4 segundos |

Si tarda más de 10 segundos, algo está mal.

---

## Resumen de Cambios

### Cambios en app.js
```javascript
// NUEVO: Barra de progreso visual
showDownloadProgress(codigo, 0)   // 0%
showDownloadProgress(codigo, 50)  // 50%
showDownloadProgress(codigo, 100) // 100%

// NUEVO: Logs detallados en consola
console.log('[DESCARGA] Iniciando...')
console.log('[PROGRESO] Formato 1001: 25%')
```

### Cambios en app.py
```python
# NUEVO: Logs detallados en consola del servidor
print(f"[DESCARGA] Iniciando generación de Formato {codigo_formato}")
print(f"[1/5] Validando sesión...")
print(f"[EXITO] Reporte {codigo_formato} generado correctamente")
```

### Cambios en style.css
```css
/* NUEVO: Estilos para barra de progreso */
.download-progress-container
.download-progress
.download-progress-bar
.download-progress-text
```

---

## Preguntas Frecuentes

**P: ¿Por qué tarda tanto?**  
R: Depende del tamaño del archivo y el número de filas. Excel es lento generando.

**P: ¿La barra es exacta?**  
R: No es exacta, es una estimación. Es para mostrar que está funcionando.

**P: ¿Se guardan los reportes?**  
R: No, se generan en memoria y se descargan directamente.

**P: ¿Puedo descargar múltiples reportes?**  
R: Sí, haz click en varios formatos. Se descargarán en secuencia.

---

## Próximas Mejoras

- [ ] Indicador de progreso real (con WebSocket)
- [ ] Historial de descargas
- [ ] Opción de generar todos los formatos
- [ ] Vista previa antes de descargar

---

## Status

✅ Indicador visual funcionando  
✅ Logs en navegador implementados  
✅ Logs en servidor detallados  
✅ Listo para usar

**Cualquier problema, revisa los logs del navegador (F12) y del servidor.**
