@echo off
rem Abre la app local. Se cierra con Ctrl+C en esta ventana.
cd /d "%~dp0"
if exist venv\Scripts\activate.bat call venv\Scripts\activate.bat
python app\servidor.py --datos data --resultados outputs --abrir
pause
