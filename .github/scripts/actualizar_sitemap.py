#!/usr/bin/env python3
import json, sys, shutil
from datetime import date
from pathlib import Path

meta_path = sys.argv[1]
fecha = sys.argv[2] if len(sys.argv) > 2 else str(date.today())

with open(meta_path) as f:
    meta = json.load(f)

# Campo obligatorio — mover a _queue/errores/ si falta
slug = meta.get("slug")

if not slug:
    errores_dir = Path("_queue/errores")
    errores_dir.mkdir(parents=True, exist_ok=True)
    json_src = Path(meta_path)
    html_src = json_src.with_suffix(".html")
    shutil.move(str(json_src), str(errores_dir / json_src.name))
    if html_src.exists():
        shutil.move(str(html_src), str(errores_dir / html_src.name))
    print("✗ Campo obligatorio 'slug' faltante: artículo movido a _queue/errores/")
    sys.exit(0)
nueva_entrada = f"""  <url>
    <loc>https://www.ciselaptop.com/blog/{slug}</loc>
    <lastmod>{fecha}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>"""

with open("sitemap.xml", "r", encoding="utf-8") as f:
    contenido = f.read()

if f"/{slug}" not in contenido:
    contenido = contenido.replace("</urlset>", f"{nueva_entrada}\n</urlset>")
    with open("sitemap.xml", "w", encoding="utf-8") as f:
        f.write(contenido)
    print(f"✓ Sitemap actualizado: {slug}")
else:
    print(f"⚠ Ya existe en sitemap: {slug}")
