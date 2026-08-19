#!/usr/bin/env python3
"""
Estampa la fecha real de publicación en archivos HTML del blog.

Actualiza:
  - <time datetime="...">DD de mes de YYYY</time>  (también convierte <span> legacy)
  - "datePublished": "..." en el bloque JSON-LD
  - "dateModified": "..." en el bloque JSON-LD

Por defecto usa la fecha de hoy en zona horaria América/Mexico_City.
Con --fecha=YYYY-MM-DD usa la fecha indicada (correcciones manuales).

Uso:
  python3 actualizar_fecha.py archivo.html
  python3 actualizar_fecha.py blog/ _queue/listos/
  python3 actualizar_fecha.py --fecha=2026-08-18 archivo.html
"""
import re, sys
from datetime import datetime, date
from pathlib import Path
from zoneinfo import ZoneInfo

MESES_ES = {
    1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
    5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
    9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre",
}

# Coincide <span> o <time datetime="..."> con fecha legible española
PATRON_FECHA = re.compile(
    r'<(?:span|time(?:\s+datetime="[^"]*")?)'
    r'>(\d{1,2}) de '
    r'(enero|febrero|marzo|abril|mayo|junio|julio|agosto|'
    r'septiembre|octubre|noviembre|diciembre) de (\d{4})'
    r'</(?:span|time)>'
)

# Coincide datePublished / dateModified en JSON-LD
PATRON_JSON_LD = re.compile(
    r'("date(?:Published|Modified)"\s*:\s*")(\d{4}-\d{2}-\d{2})(")'
)


def hoy_cdmx() -> date:
    return datetime.now(ZoneInfo("America/Mexico_City")).date()


def fecha_legible(d: date) -> str:
    return f"{d.day} de {MESES_ES[d.month]} de {d.year}"


def procesar_archivo(path: Path, fecha: date) -> bool:
    contenido = path.read_text(encoding="utf-8")

    iso = fecha.isoformat()
    legible = fecha_legible(fecha)

    # Reemplazar tags de fecha visible (<span> legacy o <time> existente)
    nuevo = PATRON_FECHA.sub(
        lambda _m: f'<time datetime="{iso}">{legible}</time>',
        contenido,
    )

    # Actualizar datePublished y dateModified en JSON-LD
    nuevo = PATRON_JSON_LD.sub(
        lambda m: f'{m.group(1)}{iso}{m.group(3)}',
        nuevo,
    )

    if nuevo != contenido:
        path.write_text(nuevo, encoding="utf-8")
        return True
    return False


def procesar_directorio(dirpath: Path, fecha: date) -> list[str]:
    actualizados = []
    for html in sorted(dirpath.glob("*.html")):
        if procesar_archivo(html, fecha):
            actualizados.append(str(html))
    return actualizados


if __name__ == "__main__":
    raw_args = sys.argv[1:]
    fecha_arg = next((a for a in raw_args if a.startswith("--fecha=")), None)
    targets = [a for a in raw_args if not a.startswith("--")]

    if fecha_arg:
        fecha = date.fromisoformat(fecha_arg.split("=", 1)[1])
    else:
        fecha = hoy_cdmx()

    if not targets:
        print("Uso: python3 actualizar_fecha.py [--fecha=YYYY-MM-DD] <archivo.html|directorio> ...")
        sys.exit(1)

    total: list[str] = []
    for arg in targets:
        p = Path(arg)
        if p.is_file():
            if procesar_archivo(p, fecha):
                total.append(str(p))
                print(f"  actualizado: {p}")
            else:
                print(f"  sin cambios: {p}")
        elif p.is_dir():
            actualizados = procesar_directorio(p, fecha)
            total.extend(actualizados)
            for a in actualizados:
                print(f"  {a}")
        else:
            print(f"  no encontrado: {arg}", file=sys.stderr)

    print(f"\nTotal actualizados: {len(total)}, fecha={fecha.isoformat()}")
