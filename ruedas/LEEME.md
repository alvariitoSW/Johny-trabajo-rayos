# Ruedas de pyRadiomics para Windows

Aquí GitHub Actions deja **pyRadiomics 3.1.0** (repositorio oficial, commit `6a761c4`) ya compilado para Windows de
64 bits, para Python 3.11 y 3.12 (`.whl`). Lo compila y pasa todas las pruebas del pipeline en un Windows real
(`.github/workflows/windows.yml`). Así el PC del hospital lo instala **sin compilador**: `instalar.bat`.

pyRadiomics es software libre con licencia BSD de 3 cláusulas (© The Regents of the University of California / el
equipo de pyRadiomics); la licencia completa va dentro de cada `.whl`. Repositorio: https://github.com/AIM-Harvard/pyradiomics

**Nombre de versión**: las ruedas se llaman `pyradiomics-3.0.1a1-…` porque GitHub Actions compila una copia sin las
etiquetas de versión de git, y la herramienta de versiones de pyRadiomics pone entonces «3.0.1a1». **El código es el
mismo** (commit `6a761c4`, etiqueta v3.1.0, fijado en `requirements-pyradiomics.txt`). En `outputs/extraccion_meta.json`
saldrá esa versión: anótalo así en el método del estudio («pyRadiomics 3.1.0, commit 6a761c4»).
