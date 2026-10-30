@echo off
rem Abre la app en MODO MOVIL: accesible desde la red interna del hospital (wifi interna o VPN), nunca internet.
rem Para dejar entrar solo a tu movil, anade al final:  --permitir IP-DE-TU-MOVIL
rem Con certificado de Informatica:  --certificado cert.pem --clave clave.pem
rem Se cierra con Ctrl+C en esta ventana. Cierrala cuando termines.
cd /d "%~dp0"
if exist venv\Scripts\activate.bat call venv\Scripts\activate.bat
python app\servidor.py --datos data --resultados outputs --movil %*
pause
