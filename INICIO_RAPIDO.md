# 🚀 Inicio Rápido

## Para Windows

### Opción 1: Script Automático (Recomendado)

1. **Descarga o clona el proyecto**
2. **Abre una terminal (cmd.exe o PowerShell)** en la carpeta del proyecto
3. **Ejecuta el script:**
   ```bash
   run.bat
   ```
4. **Abre tu navegador en:** http://localhost:5000

¡Listo! La aplicación está corriendo.

### Opción 2: Manual

1. **Abre una terminal (cmd.exe)** en la carpeta del proyecto
2. **Crea el entorno virtual:**
   ```bash
   python -m venv venv
   ```
3. **Activa el entorno virtual:**
   ```bash
   venv\Scripts\activate
   ```
4. **Instala las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```
5. **Ejecuta la aplicación:**
   ```bash
   python app.py
   ```
6. **Abre tu navegador en:** http://localhost:5000

---

## Para macOS / Linux

### Opción 1: Script Automático (Recomendado)

1. **Descarga o clona el proyecto**
2. **Abre una terminal** en la carpeta del proyecto
3. **Dale permisos al script:**
   ```bash
   chmod +x run.sh
   ```
4. **Ejecuta el script:**
   ```bash
   ./run.sh
   ```
5. **Abre tu navegador en:** http://localhost:5000

¡Listo! La aplicación está corriendo.

### Opción 2: Manual

1. **Abre una terminal** en la carpeta del proyecto
2. **Crea el entorno virtual:**
   ```bash
   python3 -m venv venv
   ```
3. **Activa el entorno virtual:**
   ```bash
   source venv/bin/activate
   ```
4. **Instala las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```
5. **Ejecuta la aplicación:**
   ```bash
   python3 app.py
   ```
6. **Abre tu navegador en:** http://localhost:5000

---

## 📋 Cómo Usar la Aplicación

### Paso 1: Preparar el archivo
- Tienes que tener un archivo Excel llamado `balance_de_sumas_y_saldos.xlsx`
- Debe tener 7 columnas (Cuenta, Balance Inicial D/C, Movimiento D/C, Balance Final D/C)

### Paso 2: Cargar el archivo
1. En la interfaz web, arrastra y suelta tu archivo de balance
2. O haz clic para seleccionar el archivo manualmente
3. Espera a que aparezca el mensaje de éxito

### Paso 3: Descargar reportes
1. Una vez cargado, haz clic en cualquiera de los 7 botones de formato
2. Los archivos se descargarán automáticamente

---

## 🎯 Estructura de Archivos Descargados

Los archivos se descargan con este formato:

```
Formato_1001_COLTRADE_2024.xlsx
Formato_1005_COLTRADE_2024.xlsx
...
```

Puedes cambiar:
- **Código de formato**: 1001, 1005, etc.
- **Nombre de empresa**: COLTRADE (editar en `app.py`)
- **Año**: 2024 (editar en `app.py`)

---

## ❓ Preguntas Frecuentes

### ¿Qué versión de Python necesito?
Python 3.8 o superior. Puedes verificar con:
```bash
python --version
```

### ¿El puerto 5000 está en uso?
Si el puerto 5000 está ocupado, edita `app.py` y cambia:
```python
app.run(host='localhost', port=8000, debug=True)  # Cambiar a puerto 8000
```

### ¿Cómo apago el servidor?
Presiona **CTRL + C** en la terminal.

### ¿Dónde se guardan los datos?
**En ningún lado.** Los datos se procesan en memoria y se descartan después de generar el reporte. Es completamente seguro.

### ¿Qué tamaño máximo de archivo soporta?
50 MB. Si necesitas más, edita en `app.py`:
```python
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB
```

### ¿Puedo agregar más formatos?
Sí. Edita `modules/data_processor.py` para agregar el mapeo de cuentas y `app.py` para agregar el botón en la interfaz.

---

## 🆘 Solución de Problemas

### Error: "No module named 'flask'"
```bash
pip install -r requirements.txt
```

### Error: "Port 5000 already in use"
En Windows:
```bash
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

En macOS/Linux:
```bash
lsof -ti:5000 | xargs kill -9
```

### El archivo no se carga
- Verifica que sea un archivo `.xlsx` (no `.xls`)
- Verifica que el nombre contenga "balance"
- Verifica que tenga al menos 7 columnas

### Error: "Session not loaded"
Recarga la página y carga el archivo de nuevo.

---

## 📞 Contacto

Para soporte o reportar bugs, contacta al equipo de desarrollo.

---

**¡Disfruta usando el Generador de Reportes COLTRADE!** 🎉
