@echo off
setlocal

chcp 65001 >nul
set PYTHONIOENCODING=utf-8

call .venv\Scripts\activate.bat
python src\tools\version_builder.py
if errorlevel 1 (
    echo Version update has failed.
    pause
    exit /b 1
)

for /f "delims=" %%i in ('python -c "from src.assets.headers import header_big; print(header_big)"') do echo %%i

echo.
echo.
echo.

echo ============================
echo Building ProgressiveNodeX...
echo ============================

echo.
echo.
echo.

rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
rmdir /s /q _Out
del /q *.spec 2>nul

pyinstaller ^
    --onefile ^
    --name ProgressiveNodeX ^
    --add-data=src\templates;src\templates ^
    --add-data=src\templates;templates ^
    --version-file=src\assets\version.txt ^
    --icon=assets\logo.ico ^
    --distpath _Out ^
    main.py

if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo Build was successful
echo Output:
echo dist/ProgressiveNodeX.exe
pause