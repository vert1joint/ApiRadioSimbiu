@echo off
chcp 65001 >nul
echo ============================================================
echo    Descarga y Actualización de Noticias - Simbiu
echo ============================================================
echo.
echo Iniciando aplicación...
echo.

:: verificar si Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no está instalado.
    echo Por favor, ejecuta primero "install.bat" para instalar Python y las dependencias.
    echo.
    pause
    exit /b 1
)

:: cambiar al directorio del script
cd /d "%~dp0"

:: ejecutar el script de Python
python InterfaceApi.py

:: si el script termina con error, mostrar mensaje
if %errorlevel% neq 0 (
    echo.
    echo ============================================================
    echo [ERROR] La aplicación terminó con errores.
    echo ============================================================
    echo.
    pause
)

