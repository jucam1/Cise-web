#!/usr/bin/env python3
"""
Reemplaza <span>DD de mes de YYYY</span> por
<time datetime="YYYY-MM-DD">DD de mes de YYYY</time>
en archivos HTML del blog (hero y cualquier otro lugar donde aparezca la fecha legible).

Uso:
  python3 actualizar_fecha.py archivo.html
  python3 actualizar_fecha.py blog/ _queue/listos/
"""
import re, sys
from pathlib import Path

MESES = {
    "enero": "01", "febrero": "02", "marzo": "03", "abril": "04",
    "mayo": "05", "junio": "06", "julio": "07", "agosto": "08",
    "septiembre": "09", "octubre": "10", "noviembre": "11", "diciembre": "12",
}

# Captura cualquier <span> que contenga una fecha en español: "14 de agosto de 2026"
PATRON = re.compile(
    r'<span>(\d{1,2}) de '
    r'(enero|febrero|marzo|abril|mayo|junio|julio|agosto|'
    r'septiembre|octubre|noviembre|diciembre) de (\d{4})</span>'
)


def _reemplazar(m: re.Match) -> str:
    dia, mes_texto, ano = m.group(1), m.group(2), m.group(3)
    iso = f"{ano}-{MESES[mes_texto]}-{int(dia):02d}"
    return f'<time datetime="{iso}">{dia} de {mes_texto} de {ano}</time>'


def procesar_archivo(path: Path) -> bool:
    contenido = path.read_text(encoding="utf-8")
    nuevo = PATRON.sub(_reemplazar, contenido)
    if nuevo != contenido:
        path.write_text(nuevo, encoding="utf-8")
        return True
    return False


def procesar_directorio(dirpath: Path) -> list[str]:
    actualizados = []
    for html in sorted(dirpath.glob("*.html")):
        if procesar_archivo(html):
            actualizados.append(str(html))
    return actualizados


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 actualizar_fecha.py <archivo.html|directorio> ...")
        sys.exit(1)

    total: list[str] = []
    for arg in sys.argv[1:]:
        p = Path(arg)
        if p.is_file():
            if procesar_archivo(p):
                total.append(str(p))
                print(f"  {p}")
            else:
                print(f"  sin cambios: {p}")
        elif p.is_dir():
            actualizados = procesar_directorio(p)
            total.extend(actualizados)
            for a in actualizados:
                print(f"  {a}")
        else:
            print(f"  no encontrado: {arg}", file=sys.stderr)

    print(f"\nTotal actualizados: {len(total)}")
