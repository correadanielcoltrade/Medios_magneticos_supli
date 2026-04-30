# 📊 Generador de Reportes - Medios Magnéticos COLTRADE

Aplicación Flask moderna para generar reportes de medios magnéticos en Excel a partir de un balance de sumas y saldos.

## 🎯 Características

✅ **Interfaz Web Intuitiva**: Landing page responsiva con drag & drop para carga de archivos
✅ **7 Formatos de Reportes**: Generación de múltiples formatos contables (1001, 1005, 1006, 1007, 1008, 1009, 2276)
✅ **Procesamiento en Memoria**: Los datos se procesan sin guardar en base de datos
✅ **Excel Profesional**: Reportes formateados con openpyxl (estilos, colores, totales)
✅ **Validaciones Robustas**: Validación de archivos y estructura de datos
✅ **Responsive Design**: Funciona en desktop, tablet y mobile

## 📋 Requisitos Previos

- Python 3.8+
- pip (gestor de paquetes)

## 🚀 Instalación Rápida

### 1. Clonar o Descargar el Proyecto

```bash
cd "ruta/del/proyecto"
```

### 2. Crear Entorno Virtual (Recomendado)

```bash
# En Windows
python -m venv venv
venv\Scripts\activate

# En macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecutar la Aplicación

```bash
python app.py
```

La aplicación estará disponible en: **http://localhost:5000**

## 📁 Estructura del Proyecto

```
generador-medios-magneticos/
├── app.py                          # Aplicación Flask principal
├── requirements.txt                # Dependencias del proyecto
├── README.md                       # Este archivo
│
├── modules/
│   ├── __init__.py                 # Init del módulo
│   ├── data_processor.py           # Procesamiento de datos
│   └── excel_generator.py          # Generación de Excel
│
├── templates/
│   └── index.html                  # Landing page
│
└── static/
    ├── style.css                   # Estilos CSS
    └── js/
        └── app.js                  # Lógica JavaScript
```

## 🔧 Cómo Usar

### Paso 1: Cargar Archivo
1. Abre la aplicación en el navegador
2. Arrastra y suelta tu archivo `balance_de_sumas_y_saldos.xlsx` en la zona de carga
   - O haz clic para seleccionar el archivo manualmente
3. Espera a que se procese (deberás ver un mensaje de éxito)

### Paso 2: Descargar Reportes
1. Una vez cargado, se habilitarán 7 botones para descargar reportes
2. Haz clic en el botón del formato que deseas
3. El archivo Excel se descargará automáticamente

### Formatos Disponibles

| Código | Nombre | Descripción |
|--------|--------|-------------|
| **1001** | Pagos o abonos | Retenciones en IVA y Renta |
| **1005** | IVA Descontable | IVA descontable |
| **1006** | IVA Generado | IVA generado e impuesto al consumo |
| **1007** | Ingresos | Ingresos operacionales |
| **1008** | Cuentas por Cobrar | Cartera de clientes |
| **1009** | Cuentas por Pagar | Obligaciones con proveedores |
| **2276** | Rentas de Trabajo | Gastos de nómina |

## 📊 Estructura del Archivo de Balance

El archivo `balance_de_sumas_y_saldos.xlsx` debe tener la siguiente estructura:

| Unnamed: 0 | Balance Inicial D | Balance Inicial C | 2025 D | 2025 C | Balance Final D | Balance Final C |
|---|---|---|---|---|---|---|
| Descripción de Cuenta | Débito | Crédito | Débito | Crédito | Débito | Crédito |
| 110200 Bancos | 5000 | | 2000 | | 7000 | |
| 220100 Cuentas por Pagar | | 3000 | | 1000 | | 4000 |

### Validaciones de Archivo

- ✅ Extensión: `.xlsx`
- ✅ Nombre: debe contener "balance"
- ✅ Columnas: mínimo 7 columnas
- ✅ Valores numéricos: en las columnas de débito/crédito

## 🎨 Personalización

### Cambiar Empresa o Año

Edita en `app.py`:

```python
excel_gen = ExcelGenerator(codigo_formato, df_formato, 'TU_EMPRESA', 2025)
```

### Cambiar Colores

Edita en `static/style.css` las variables CSS:

```css
:root {
    --primary-color: #1f4e78;
    --primary-light: #4472c4;
    /* ... más variables ... */
}
```

### Añadir Nuevos Formatos

Edita en `modules/data_processor.py`:

```python
FORMATO_CONFIG = {
    '2277': {  # Nuevo formato
        'nombre': 'Nuevo Formato',
        'descripcion': 'Descripción',
        'cuentas_patron': ['XXXX'],
        'tipo': 'tipo'
    },
    # ... más formatos ...
}
```

Y agrega en `app.py`:

```python
FORMATOS_DISPONIBLES = {
    '2277': {
        'nombre': 'Formato 2277',
        'descripcion': 'Descripción',
        'icono': '📋'
    },
    # ... más formatos ...
}
```

## 🔐 Seguridad

- ✅ Validación de tipo de archivo
- ✅ Validación de tamaño (máximo 50MB)
- ✅ Validación de estructura de datos
- ✅ Procesamiento en memoria (sin almacenamiento persistente)
- ✅ Sesiones seguras con secret_key

## ⚙️ Configuración Avanzada

### Cambiar Puerto

Edita en `app.py`:

```python
app.run(host='localhost', port=8000, debug=True)
```

### Desactivar Debug

Para producción, en `app.py`:

```python
app.run(host='localhost', port=5000, debug=False)
```

## 🐛 Solución de Problemas

### Error: "ModuleNotFoundError: No module named 'flask'"

```bash
pip install -r requirements.txt
```

### Error: "Port 5000 already in use"

```bash
# Cambiar puerto en app.py o matar el proceso
# En Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# En macOS/Linux:
lsof -ti:5000 | xargs kill -9
```

### El archivo no se procesa correctamente

1. Verifica que el archivo está en formato `.xlsx` (no `.xls`)
2. Verifica que el nombre contiene "balance"
3. Verifica la estructura (7 columnas, datos numéricos)

## 📞 Soporte

Para reportar bugs o sugerencias, contáctate con el equipo de desarrollo.

## 📄 Licencia

© 2024 COLTRADE SAS. Todos los derechos reservados.

---

**Última actualización**: 2024
**Versión**: 1.0.0
