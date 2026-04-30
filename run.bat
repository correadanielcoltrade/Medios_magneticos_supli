@echo off
title Generador de Reportes - Medios Magneticos Supli

echo.
echo ====================================================
echo  GENERADOR DE REPORTES - MEDIOS MAGNETICOS
echo ====================================================
echo.

REM Verificar si existe venv
if not exist "venv" (
    echo Creando entorno virtual...
    python -m venv venv
    echo Entorno virtual creado.
)

echo Activando entorno virtual...
call venv\Scripts\activate.bat

echo Instalando dependencias...
pip install -r requirements.txt --quiet

echo.
echo ====================================================
echo  Iniciando aplicacion...
echo  Abre tu navegador en: http://localhost:5000
echo  Presiona CTRL+C para detener el servidor
echo ====================================================
echo.

python app.py

pause
