#!/usr/bin/env python3
import json, sys
from datetime import date

meta_path = sys.argv[1]
fecha = sys.argv[2] if len(sys.argv) > 2 else str(date.today())

with open(meta_path) as f:
    meta = json.load(f)

slug = meta["slug"]
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
