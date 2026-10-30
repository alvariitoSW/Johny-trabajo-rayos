#!/usr/bin/env bash
# Abre la app local. Uso: ./lanzar_app.sh [datos] [resultados]
cd "$(dirname "$0")" || exit 1
[ -f venv/bin/activate ] && . venv/bin/activate
python3 app/servidor.py --datos "${1:-data}" --resultados "${2:-outputs}" --abrir
