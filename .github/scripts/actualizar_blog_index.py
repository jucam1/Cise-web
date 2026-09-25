#!/usr/bin/env python3
import json, sys, shutil
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

meta_path = sys.argv[1]

with open(meta_path) as f:
    meta = json.load(f)

# Campos obligatorios — mover a _queue/errores/ si alguno falta
slug      = meta.get("slug")
categoria = meta.get("categoria")

if not slug or not categoria:
    missing = [k for k in ("slug", "categoria") if not meta.get(k)]
    errores_dir = Path("_queue/errores")
    errores_dir.mkdir(parents=True, exist_ok=True)
    json_src = Path(meta_path)
    html_src = json_src.with_suffix(".html")
    shutil.move(str(json_src), str(errores_dir / json_src.name))
    if html_src.exists():
        shutil.move(str(html_src), str(errores_dir / html_src.name))
    print(f"✗ Campos obligatorios faltantes ({', '.join(missing)}): artículo movido a _queue/errores/")
    sys.exit(0)

# Campos opcionales con valores de respaldo
titulo  = meta.get("titulo", f"{slug} — Ciselaptop Oaxaca")
excerpt = meta.get("excerpt", "")
imagen  = meta.get("imagenHero", f"/img/blog/{slug}/hero.webp")

# Fecha real del día en que corre el script (zona horaria CDMX)
meses = {1:"enero",2:"febrero",3:"marzo",4:"abril",5:"mayo",6:"junio",
         7:"julio",8:"agosto",9:"septiembre",10:"octubre",11:"noviembre",12:"diciembre"}
hoy = datetime.now(ZoneInfo("America/Mexico_City"))
fecha_legible = f"{hoy.day} de {meses[hoy.month]} de {hoy.year}"

# Colores de badge por categoría
badge_styles = {
    "Bisagras y carcasas": "background-color:#fde8e8; color:#C8272E;",
    "Actualización SSD":   "background-color:#e8eaf6; color:#1D2E8C;",
    "Software y sistema":  "background-color:#f3e8ff; color:#7c3aed;",
    "Impresoras":          "background-color:#fff3e0; color:#e65100;",
    "Diagnóstico":         "background-color:#e8eaf6; color:#1D2E8C;",
}
badge_style = badge_styles.get(categoria, "background-color:#f3f4f6; color:#374151;")

# HTML de la nueva card — misma estructura que las cards existentes en blog.html
nueva_card = f"""          <!-- card:{slug} -->
          <div class="group block rounded-2xl border border-gray-100 shadow-sm overflow-hidden card-lift">
            <a href="/blog/{slug}">
              <div class="relative w-full h-48 overflow-hidden">
                <img
                  src="{imagen}"
                  alt="{titulo}"
                  class="absolute inset-0 w-full h-full object-cover"
                  loading="lazy"
                />
              </div>
            </a>
            <div class="p-6">
              <span class="inline-block text-xs font-semibold px-2 py-1 rounded-full mb-3" style="{badge_style}">{categoria}</span>
              <h2 class="text-lg font-bold text-gray-900 mb-2 leading-snug">
                <a href="/blog/{slug}" class="hover:text-blue-800 transition-colors">
                  {titulo}
                </a>
              </h2>
              <p class="text-sm text-gray-500 leading-relaxed mb-4">
                {excerpt}
              </p>
              <div class="flex items-center gap-2 mt-4 text-sm text-gray-500">
                <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-[#1D2E8C]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5.121 17.804A9 9 0 1118.88 6.196M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                <a href="/quienes-somos" class="text-[#1D2E8C] font-medium hover:underline">Ciselaptop</a>
                <span>·</span>
                <span>{fecha_legible}</span>
              </div>
              <a href="/blog/{slug}" class="text-sm font-semibold hover:underline" style="color:#1D2E8C;">Leer artículo →</a>
            </div>
          </div>"""

with open("blog.html", "r", encoding="utf-8") as f:
    contenido = f.read()

if f"card:{slug}" not in contenido:
    contenido = contenido.replace(
        "<!-- NUEVA_CARD_AQUI -->",
        f"<!-- NUEVA_CARD_AQUI -->\n{nueva_card}"
    )
    with open("blog.html", "w", encoding="utf-8") as f:
        f.write(contenido)
    print(f"✓ Blog index actualizado: {slug}")
else:
    print(f"⚠ Card ya existe: {slug}")
