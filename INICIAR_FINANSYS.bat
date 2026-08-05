@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
  set "PYTHON_CMD=py"
) else (
  where python >nul 2>nul
  if errorlevel 1 (
    echo Python nao foi encontrado.
    echo Instale Python 3.12 ou superior em https://www.python.org/downloads/
    pause
    exit /b 1
  )
  set "PYTHON_CMD=python"
)

if not exist ".venv\Scripts\python.exe" (
  echo Criando ambiente virtual...
  %PYTHON_CMD% -m venv .venv
  if errorlevel 1 goto :erro
  echo Instalando dependencias do FinanSys...
  ".venv\Scripts\python.exe" -m pip install --upgrade pip
  ".venv\Scripts\python.exe" -m pip install -r requirements.txt
  if errorlevel 1 goto :erro
)

start "" http://127.0.0.1:8000
".venv\Scripts\python.exe" main.py
goto :fim

:erro
echo.
echo Nao foi possivel preparar o FinanSys.
pause
exit /b 1

:fim
endlocal
