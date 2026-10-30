@echo off
rem Instala el entorno del estudio en este PC (una sola vez). No necesita permisos de administrador.
cd /d "%~dp0"
set PYTHONUTF8=1
echo.
echo === Instalando el entorno del estudio (tarda unos minutos) ===
if not exist venv\Scripts\python.exe (
  py -3.11 -m venv venv
  if errorlevel 1 goto error
)
call venv\Scripts\activate.bat
python -m pip install -r requirements.txt
if errorlevel 1 goto error
rem pyRadiomics ya compilado para Windows (carpeta ruedas), sin compilador
python -m pip install --no-index --find-links ruedas --no-deps pyradiomics
if errorlevel 1 goto error
python -c "import radiomics; from radiomics import cMatrices; print('pyRadiomics', radiomics.__version__, 'instalado')"
if errorlevel 1 goto error
echo.
echo === LISTO. Ahora abre la app con doble clic en lanzar_app.bat ===
pause
exit /b 0
:error
echo.
echo === Algo ha fallado. Haz una foto de esta ventana y mandala. ===
pause
exit /b 1
