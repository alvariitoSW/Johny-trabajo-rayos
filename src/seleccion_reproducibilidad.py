"""Sorteo de los casos para el segundo observador (protocolo §8: 20-30 % al azar, mínimo orientativo 15).

Se ejecuta en el hospital, ANTES de segmentar, una sola vez. La lista resultante se queda en el hospital.
Con la misma semilla y los mismos casos sale siempre la misma lista (semilla fija por defecto: 20261030).
Número de casos: n = min(N, max(mínimo, ceil(porcentaje/100 · N))). Si N es menor que el mínimo, se avisa
y se eligen todos.

Salida:  <salida>/seleccion_reproducibilidad.csv   columna id, ordenada
         <salida>/seleccion_reproducibilidad.json  semilla, porcentaje, minimo, N, n, fecha, aviso

Uso:  python src/seleccion_reproducibilidad.py --casos data/crudo [--porcentaje 30] [--minimo 15] [--semilla 20261030]
"""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
from datetime import date
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comun  # noqa: E402


def leer_codigos(origen: Path) -> list[str]:
    if origen.is_dir():
        codigos = [c.name for c in origen.iterdir() if c.is_dir()]
    else:
        codigos = [l.strip() for l in origen.read_text(encoding='utf-8').splitlines() if l.strip()]
    for c in codigos:
        comun.comprobar_id(c)
    return sorted(set(codigos))


def seleccionar(codigos: list[str], porcentaje: float, minimo: int, semilla: int) -> tuple[list[str], str]:
    N = len(codigos)
    n = min(N, max(minimo, math.ceil(porcentaje / 100 * N)))
    aviso = (f'Solo hay {N} casos, menos del mínimo orientativo de {minimo}; se eligen todos.'
             if N < minimo else '')
    return sorted(random.Random(semilla).sample(sorted(codigos), n)), aviso


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--casos', type=Path, required=True, help='carpeta con una subcarpeta por código, o un .txt')
    p.add_argument('--porcentaje', type=float, default=30)
    p.add_argument('--minimo', type=int, default=15)
    p.add_argument('--semilla', type=int, default=20261030)
    p.add_argument('--salida', type=Path, default=Path('outputs'))
    a = p.parse_args(argv)

    codigos = leer_codigos(a.casos)
    elegidos, aviso = seleccionar(codigos, a.porcentaje, a.minimo, a.semilla)
    a.salida.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({'id': elegidos}).to_csv(a.salida / 'seleccion_reproducibilidad.csv', index=False, encoding='utf-8')
    (a.salida / 'seleccion_reproducibilidad.json').write_text(json.dumps(
        {'semilla': a.semilla, 'porcentaje': a.porcentaje, 'minimo': a.minimo, 'N': len(codigos),
         'n': len(elegidos), 'fecha': date.today().isoformat(), 'aviso': aviso},
        ensure_ascii=False, indent=2), encoding='utf-8')
    if aviso:
        print('AVISO: ' + aviso)
    print(f'Sorteo: {len(elegidos)} de {len(codigos)} casos para el segundo observador → '
          f'{a.salida / "seleccion_reproducibilidad.csv"}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
