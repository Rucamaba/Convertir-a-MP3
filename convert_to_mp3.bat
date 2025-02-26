@echo off
chcp 65001 > nul
setlocal EnableDelayedExpansion
set PYTHONIOENCODING=utf-8

echo ===================================
echo    YouTube a MP3 - Conversor
echo ===================================
echo.

""C:\Users\ruben\AppData\Local\Programs\Python\Python313\python.exe"" ""C:\Convertir a MP3\youtube_to_mp3.py"" "%~1"
if !errorlevel! neq 0 (
    echo.
    echo [ERROR] La conversion no se completo correctamente
) else (
    echo.
    echo [EXITO] La conversion se completo correctamente
)
echo.
echo Presione cualquier tecla para salir...
pause > nul
