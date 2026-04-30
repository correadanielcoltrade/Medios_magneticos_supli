# 📁 Estructura del Proyecto

```
generador-medios-magneticos/
│
├── 📋 ARCHIVOS PRINCIPALES
│   ├── app.py                          ⭐ Aplicación Flask principal (rutas, servidor)
│   ├── requirements.txt                ⭐ Dependencias de Python
│   ├── run.bat                         ⭐ Script de inicio para Windows
│   └── run.sh                          ⭐ Script de inicio para macOS/Linux
│
├── 📚 DOCUMENTACIÓN
│   ├── README.md                       📖 Documentación completa
│   ├── INICIO_RAPIDO.md                🚀 Guía de inicio rápido
│   ├── ESTRUCTURA_ARCHIVO.md           📄 Formato esperado del archivo de balance
│   ├── PROJECT_STRUCTURE.md            📁 Este archivo
│   ├── config.example.py               ⚙️ Configuración de ejemplo
│   └── .gitignore                      🔒 Archivos a ignorar en Git
│
├── 📦 MÓDULOS PRINCIPALES
│   └── modules/
│       ├── __init__.py                 Inicializador del módulo
│       ├── data_processor.py           🔄 Procesa balance y mapea a formatos
│       └── excel_generator.py          📊 Genera archivos Excel formateados
│
├── 🌐 FRONTEND (Templates)
│   └── templates/
│       └── index.html                  🎨 Landing page responsiva
│
├── 🎨 ASSETS (Static Files)
│   └── static/
│       ├── style.css                   🎨 Estilos CSS (Bootstrap 5 + custom)
│       └── js/
│           └── app.js                  ⚙️ Lógica JavaScript del cliente
│
└── 📂 DIRECTORIOS DE RUNTIME (Se crean automáticamente)
    └── temp/                           📁 Archivos temporales
    └── logs/                           📁 Archivos de log (opcional)
```

---

## 📋 Descripción de Archivos Clave

### `app.py` ⭐
**Responsabilidad**: Servidor Flask y rutas HTTP

**Contenido**:
- Inicialización de la aplicación Flask
- Ruta GET `/` → Renderiza la landing page
- Ruta POST `/upload` → Recibe y procesa archivos
- Ruta GET `/status` → Verifica estado de sesión
- Ruta GET `/download/<formato>` → Genera y descarga reportes
- Ruta POST `/clear-session` → Limpia la sesión actual

**No necesita modificación** a menos que quieras cambiar el puerto o la empresa.

---

### `modules/data_processor.py` 🔄
**Responsabilidad**: Procesamiento inteligente de datos

**Clases**:
- `DataProcessor`: Procesa datos del balance

**Métodos principales**:
- `__init__(df)`: Inicializa con un DataFrame
- `procesar_formato(codigo_formato)`: Mapea datos a un formato específico
- `validar_estructura()`: Valida que el archivo tenga la estructura correcta

**Mapeo de cuentas** (línea ~55):
- Define qué códigos de cuenta corresponden a cada formato
- Fácil de modificar si necesitas agregar nuevos formatos

---

### `modules/excel_generator.py` 📊
**Responsabilidad**: Generación de archivos Excel profesionales

**Clases**:
- `ExcelGenerator`: Genera archivos Excel con formato

**Métodos principales**:
- `__init__()`: Inicializa generador con datos
- `generar_excel()`: Crea el archivo Excel formateado
- `obtener_nombre_archivo()`: Retorna nombre descriptivo

**Características**:
- Estilos profesionales (colores, fuentes, bordes)
- Formato de números (decimales)
- Filas alternadas para legibilidad
- Fila de totales automática

---

### `templates/index.html` 🎨
**Responsabilidad**: Interfaz de usuario

**Secciones**:
1. **Header**: Logo y título
2. **Upload Section**: Dropzone para carga de archivos
3. **Reports Section**: Grid de 7 botones de descarga
4. **Footer**: Información de la empresa

**Tecnología**: HTML5, Bootstrap 5, Responsive Design

---

### `static/style.css` 🎨
**Responsabilidad**: Estilos visuales

**Contenido**:
- Variables CSS (colores, sombras)
- Estilos generales
- Componentes (header, cards, buttons)
- Animaciones (slideIn, bounce)
- Responsive media queries (mobile, tablet, desktop)

---

### `static/js/app.js` ⚙️
**Responsabilidad**: Interactividad del cliente

**Clase**: `ReportApp`

**Métodos principales**:
- `initializeElements()`: Captura elementos del DOM
- `attachEventListeners()`: Vincula eventos
- `uploadFile()`: Carga archivo al servidor
- `handleDownload()`: Descarga reportes
- `clearSession()`: Limpia sesión

---

## 🔄 Flujo de Datos

```
1. Usuario abre navegador → app.py GET / → Renderiza index.html
2. Usuario carga archivo → JavaScript evento upload
3. JavaScript envía POST /upload → app.py recibe y procesa
4. app.py usa DataProcessor → Valida y guarda en sesión
5. app.py retorna JSON con éxito
6. JavaScript habilita botones de descarga
7. Usuario hace clic en botón → JavaScript envía GET /download/1001
8. app.py usa DataProcessor + ExcelGenerator → Crea Excel
9. app.py retorna archivo → Browser descarga
10. Usuario repite paso 7-9 para otros formatos
```

---

## 📊 Mapeo de Formatos

```
┌─────────┬─────────────────────────────────┬──────────────────┐
│ Código  │ Descripción                     │ Códigos Mapeados │
├─────────┼─────────────────────────────────┼──────────────────┤
│ 1001    │ Retenciones practicadas         │ 2365, 2366, 2x   │
│ 1005    │ IVA descontable                 │ 24050x           │
│ 1006    │ IVA generado                    │ 24051x           │
│ 1007    │ Ingresos recibidos              │ 4xxx             │
│ 1008    │ Cuentas por cobrar              │ 1205             │
│ 1009    │ Cuentas por pagar               │ 2x               │
│ 2276    │ Rentas de trabajo               │ 5105x, 5205x     │
└─────────┴─────────────────────────────────┴──────────────────┘
```

---

## ⚙️ Tecnologías Utilizadas

```
Backend:
  ├── Flask 3.0.0               → Framework web
  ├── Pandas 2.1.4              → Procesamiento de datos
  ├── openpyxl 3.10.1           → Generación de Excel
  └── Werkzeug 3.0.1            → WSGI utilities

Frontend:
  ├── HTML5                      → Estructura
  ├── CSS3                       → Estilos
  ├── JavaScript (ES6)           → Interactividad
  ├── Bootstrap 5                → Framework CSS
  └── Fetch API                  → Comunicación con servidor

Build/Deploy:
  ├── Python 3.8+               → Runtime
  └── pip                        → Gestor de paquetes
```

---

## 🔐 Seguridad

- ✅ Validación de tipos de archivo
- ✅ Validación de tamaño (máx 50MB)
- ✅ Validación de estructura de datos
- ✅ Sin almacenamiento persistente (solo sesión)
- ✅ Sesiones seguras con secret_key
- ✅ Protección contra archivos grandes

---

## 📈 Escalabilidad

**Actual**: 
- Un usuario por sesión
- Procesamiento en memoria
- Ideal para hasta 50-100 usuarios simultáneos

**Para mejorar**:
- Agregar Base de datos (SQLite, PostgreSQL)
- Task queue (Celery + Redis)
- Cache (Redis)
- Logging centralizado
- Load balancer (Nginx)

---

## 🚀 Para Producción

Cambios recomendados en `app.py`:

```python
# Cambiar debug
debug = False

# Usar un servidor WSGI (Gunicorn)
# gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Agregar HTTPS
# - Usar certificados SSL
# - Force HTTPS redirect

# Mejorar seguridad
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
```

---

## 📝 Notas de Desarrollo

- **Nombres descriptivos**: Todas las variables y funciones tienen nombres claros
- **Modularidad**: Código separado en módulos por responsabilidad
- **Sin comentarios innecesarios**: El código es auto-documentable
- **Validaciones robustas**: Manejo completo de errores
- **Responsive**: Funciona en todos los dispositivos

---

## 🔗 Relación de Archivos

```
app.py
  ├─→ modules/data_processor.py
  ├─→ modules/excel_generator.py
  ├─→ templates/index.html
  │    └─→ static/js/app.js
  │    └─→ static/style.css
  └─→ requirements.txt (dependencias)
```

---

Para más información sobre cómo usar la aplicación, consulta:
- **README.md** - Documentación completa
- **INICIO_RAPIDO.md** - Guía rápida de inicio
- **ESTRUCTURA_ARCHIVO.md** - Formato del archivo de entrada
