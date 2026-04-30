#!/bin/bash

echo "===================================================="
echo " GENERADOR DE REPORTES - MEDIOS MAGNETICOS"
echo "===================================================="
echo ""

# Verificar si existe venv
if [ ! -d "venv" ]; then
    echo "Creando entorno virtual..."
    python3 -m venv venv
    echo "Entorno virtual creado."
fi

echo "Activando entorno virtual..."
source venv/bin/activate

echo "Instalando dependencias..."
pip install -r requirements.txt -q

echo ""
echo "===================================================="
echo " Iniciando aplicacion..."
echo " Abre tu navegador en: http://localhost:5000"
echo " Presiona CTRL+C para detener el servidor"
echo "===================================================="
echo ""

python3 app.py
