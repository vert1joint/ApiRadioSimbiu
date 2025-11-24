@echo off
chcp 65001 >nul
title Renovar Token - API Simbiu

:: cambiar al directorio del script
cd /d "%~dp0"

:: ejecutar el renovador de token
python renovar_token.py

:: pausa al final (por si hay errores)
if %errorlevel% neq 0 (
    echo.
    pause
)

