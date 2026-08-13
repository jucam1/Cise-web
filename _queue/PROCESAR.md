# Instrucciones de procesamiento — Cola del blog
## Claude Code debe seguir estos pasos cada vez que el usuario diga
## "procesa la cola del blog" o similar.

---

### PASO 1 — Detectar órdenes en cola

Primero sincroniza con el repositorio remoto para recibir los JSONs que CISEFLOW haya depositado:

```bash
git pull origin main
```

Luego lista todos los archivos JSON en _queue/ (ignorar .gitkeep y .md):

```bash
ls _queue/*.json 2>/dev/null || echo "Cola vacía"
```

Si no hay JSON, responde: "La cola está vacía. No hay artículos pendientes."
Si hay JSON, procesa cada uno en orden.

---

### PASO 2 — Para cada JSON, descargar y optimizar fotos

Lee el JSON y ejecuta este script Python adaptando las URLs reales:

```python
import requests, os
from PIL import Image
from io import BytesIO
import json

with open("_queue/orden-XXXX.json") as f:
    data = json.load(f)

slug = data["slug"]
os.makedirs(f"img/blog/{slug}", exist_ok=True)

for i, foto in enumerate(data["fotos"]):
    r = requests.get(foto["url"], timeout=30)
    img = Image.open(BytesIO(r.content)).convert("RGB")
    if img.width > 1200:
        ratio = 1200 / img.width
        img = img.resize((1200, int(img.height * ratio)), Image.LANCZOS)
    nombre = "hero" if foto["esHero"] else f"foto-{i}"
    ruta = f"img/blog/{slug}/{nombre}.webp"
    img.save(ruta, "WEBP", quality=82)
    print(f"✓ {ruta} ({os.path.getsize(ruta)//1024} KB)")
```

---

### PASO 3 — Generar el HTML del artículo

#### POLÍTICAS FIJAS — usar siempre, nunca inventar datos distintos

##### Diagnóstico
- General (equipo que enciende): $150 MXN + IVA · 48 horas hábiles.
  Se descuenta del total si el cliente autoriza la reparación.
- Nivel componente (no enciende o mojado): $250 MXN + IVA · 5 días hábiles.
  NO se descuenta de la reparación — es un trabajo de mayor profundidad.

##### Tiempos de entrega (post-diagnóstico)
- Refacciones nacionales: 5 a 10 días hábiles.
- Refacciones internacionales: 30 a 40 días hábiles.
- No poner tiempos exactos si no se sabe el origen de la refacción.
  Usar: "El tiempo depende de la disponibilidad de refacciones."
- Pueden aparecer fallas ocultas distintas a la reportada —
  en ese caso se envía una nueva cotización antes de continuar.

##### Garantía
- Mano de obra: 35 días naturales.
- Refacciones: según política del fabricante.
- Software: sin garantía.

##### Reglas de contenido
- Si el JSON trae precio → mostrarlo como referencia.
- Si el JSON NO trae precio → decir "cotización tras diagnóstico", sin inventar cifras.
- Nunca poner tiempos de entrega específicos que no vengan en el JSON.
- Nunca decir que el diagnóstico fue gratis — explicar la política real.
- No mencionar datos del cliente (nombre, teléfono, RFC).

---

Usa `blog/bisagra-laptop-oaxaca.html` como template estructural.
Genera `blog/{slug}.html` con:

- title tag: "{marca} {modelo} — {falla resuelta en Oaxaca} | Ciselaptop"
  (máximo 60 caracteres, ajusta si es necesario)
- meta description: basada en falla + solución + ciudad + precio si existe
  (máximo 155 caracteres)
- H1: título natural del caso real en primera persona del taller
- Intro: párrafo explicando cómo llegó el equipo y qué tenía
- Secciones con H2/H3 según el tipo de reparación:
  - ¿Qué es este tipo de reparación? → answer capsule (definición en 2-3 líneas)
  - Síntomas que presentaba el equipo → lista
  - Qué se hizo paso a paso → H3 por cada etapa
  - Galería de fotos del proceso (grid 2-3 columnas con las fotos descargadas)
  - ¿Cuánto cuesta? → tabla con precio desde + tiempo + garantía
  - CTA intermedio (fondo #f0f2fc, botón navy → WhatsApp)
  - Preguntas frecuentes → 3-4 preguntas relevantes al tipo de reparación
- CTA final (dark-section con botón rojo)
- Schema JSON-LD: Article + FAQPage (misma estructura que los artículos existentes)
- Todas las URLs en schema con https://www.ciselaptop.com
- Fecha: la del campo "fecha" del JSON
- og:image y twitter:image: /img/blog/{slug}/hero.webp con www

Mantén exactamente las mismas clases CSS, variables y estructura
que usa blog/bisagra-laptop-oaxaca.html.

---

### PASO 4 — Actualizar sitemap.xml

Agrega esta entrada antes del cierre </urlset>:

```xml
<url>
  <loc>https://www.ciselaptop.com/blog/{slug}</loc>
  <lastmod>{fecha}</lastmod>
  <changefreq>monthly</changefreq>
  <priority>0.7</priority>
</url>
```

---

### PASO 5 — Actualizar blog.html

En la sección del grid de artículos, agrega una nueva card
siguiendo exactamente el mismo patrón HTML de las cards existentes:

- Imagen: /img/blog/{slug}/hero.webp (h-48 object-cover)
- Badge: categoría del JSON
  - "Bisagras y carcasas" → style="background-color:#fde8e8; color:#C8272E;"
  - "Actualización SSD"   → style="background-color:#e8eaf6; color:#1D2E8C;"
  - "Software y sistema"  → style="background-color:#f3e8ff; color:#7c3aed;"
  - "Impresoras"          → style="background-color:#fff3e0; color:#e65100;"
  - "Diagnóstico"         → style="background-color:#e8eaf6; color:#1D2E8C;"
  - otras                 → style="background-color:#f3f4f6; color:#374151;"
- H2: mismo título que el H1 del artículo
- Excerpt: 1-2 líneas resumiendo el caso (marca, modelo, falla resuelta)
- Autor: "Ciselaptop" · fecha legible (ej. "12 de agosto de 2026")
- Enlace: /blog/{slug}
- "Leer artículo →"

Inserta la nueva card AL INICIO del grid (los artículos más recientes primero).

---

### PASO 6 — Eliminar el JSON procesado

```bash
rm _queue/orden-{id}.json
```

---

### PASO 7 — Commit y push

```bash
git add .
git commit -m "Blog: {marca} {modelo} — {falla} [{fecha}]"
git push origin main
```

Vercel despliega automáticamente en 1-2 minutos.

---

### PASO 8 — Confirmar al usuario

Reporta:
- Artículo creado: ciselaptop.com/blog/{slug}
- Fotos descargadas y optimizadas: N fotos, peso total X KB
- Sitemap actualizado
- Blog index actualizado
- Deploy disparado en Vercel
