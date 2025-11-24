@echo off
chcp 65001 >nul
echo ============================================================
echo    INSTALADOR DE DEPENDENCIAS - Simbiu
echo    (No requiere permisos de administrador)
echo ============================================================
echo.

echo [1/2] Verificando Python...
echo.

:: verificar si python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no está instalado.
    echo.
    echo Por favor, descarga e instala Python 3.11 desde:
    echo https://www.python.org/downloads/
    echo.
    echo IMPORTANTE: Durante la instalación, marca la opción
    echo "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo ✓ Python encontrado:
python --version
echo.

echo [2/2] Instalando dependencias...
echo.

:: actualizar pip
echo Actualizando pip...
python -m pip install --upgrade pip --user --quiet
echo ✓ pip actualizado.
echo.

:: instalar dependencias
echo Instalando librerías necesarias...
echo.

python -m pip install --user requests
echo ✓ requests instalado

python -m pip install --user mysql-connector-python
echo ✓ mysql-connector-python instalado

python -m pip install --user paramiko
echo ✓ paramiko instalado

python -m pip install --user tkcalendar
echo ✓ tkcalendar instalado

python -m pip install --user mutagen
echo ✓ mutagen instalado

echo.
echo ============================================================
echo    ✓ TODAS LAS DEPENDENCIAS INSTALADAS
echo ============================================================
echo.
echo Ahora puedes ejecutar la aplicación con "ejecutar.bat"
echo.
pause

