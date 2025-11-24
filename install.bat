@echo off
chcp 65001 >nul
echo ============================================================
echo    INSTALADOR - Descarga de Noticias Radiales - Simbiu
echo ============================================================
echo.

:: verificar si se ejecuta como administrador
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Este script requiere permisos de administrador.
    echo Por favor, ejecuta como administrador haciendo clic derecho 
    echo sobre el archivo y seleccionando "Ejecutar como administrador".
    echo.
    pause
    exit /b 1
)

echo [1/4] Verificando instalación de Python 3.11...
echo.

:: verificar si python está instalado
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Python ya está instalado:
    python --version
    echo.
    goto :install_packages
)

echo [!] Python no está instalado en el sistema.
echo.

:: descargar Python 3.11
echo [2/4] Descargando Python 3.11.9...
echo.

set PYTHON_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
set PYTHON_INSTALLER=%TEMP%\python-3.11.9-installer.exe

curl -L -o "%PYTHON_INSTALLER%" "%PYTHON_URL%"
if %errorlevel% neq 0 (
    echo [ERROR] No se pudo descargar Python. Verifica tu conexión a internet.
    echo.
    pause
    exit /b 1
)

echo ✓ Python descargado exitosamente.
echo.

:: instalar Python
echo [3/4] Instalando Python 3.11.9...
echo Esto puede tomar unos minutos...
echo.

"%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
if %errorlevel% neq 0 (
    echo [ERROR] Error durante la instalación de Python.
    echo.
    pause
    exit /b 1
)

echo ✓ Python instalado exitosamente.
echo.

:: eliminar instalador
del "%PYTHON_INSTALLER%"

:: actualizar las variables de entorno en la sesión actual
call refreshenv >nul 2>&1

echo [!] Python ha sido agregado al PATH.
echo.

:install_packages
echo [4/4] Instalando dependencias de Python...
echo.

:: actualizar pip
echo Actualizando pip...
python -m pip install --upgrade pip --quiet
echo ✓ pip actualizado.
echo.

:: instalar dependencias
echo Instalando librerías necesarias:
echo   - requests
echo   - mysql-connector-python
echo   - paramiko
echo   - tkcalendar
echo   - mutagen
echo.

python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Error al instalar las dependencias.
    echo Intentando instalar manualmente...
    echo.
    python -m pip install requests mysql-connector-python paramiko tkcalendar mutagen
)

echo.
echo ============================================================
echo    ✓ INSTALACIÓN COMPLETADA EXITOSAMENTE
echo ============================================================
echo.
echo Ahora puedes ejecutar la aplicación usando "ejecutar.bat"
echo.
pause

