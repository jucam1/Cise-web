# Instrucciones de procesamiento — Cola del blog
## Cuando el usuario diga "procesa la cola del blog", sigue estos pasos.

---

### PASO 0 — Actualizar repo local

```bash
git pull origin main
```

---

### PASO 1 — Detectar órdenes en cola

```bash
ls _queue/*.json 2>/dev/null || echo "Cola vacía"
```

Si no hay JSON, responde: "La cola está vacía. No hay artículos pendientes."
Si hay JSON, procesa los **5 más antiguos** (orden alfabético de nombre de archivo = orden cronológico) pero NO los publiques todavía.
Si hay más de 5, procesa solo los 5 primeros y al final del PASO 7 indica cuántos quedaron pendientes para la próxima sesión.

---

### PASO 2 — Para cada JSON: descargar y optimizar fotos

Lee el JSON y ejecuta este script Python:

```python
import requests, os, json
from PIL import Image
from io import BytesIO

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

Usa `blog/bisagra-laptop-oaxaca.html` como template estructural.
Genera el HTML completo del artículo basándote en los datos del JSON.

#### Políticas fijas — nunca inventar datos distintos a estos

**Diagnóstico:**
- General (equipo que enciende): $150 MXN + IVA · 48 horas hábiles.
  Se descuenta del total si el cliente autoriza la reparación.
- Nivel componente (no enciende o mojado): $250 MXN + IVA · 5 días hábiles.
  NO se descuenta — es trabajo de mayor profundidad.

**Tiempos de entrega post-diagnóstico:**
- Refacciones nacionales: 5 a 10 días hábiles.
- Refacciones internacionales: 30 a 40 días hábiles.
- Si no se sabe origen de refacción: "El tiempo depende de la disponibilidad de refacciones."
- Pueden aparecer fallas ocultas distintas — se envía nueva cotización antes de continuar.

**Garantía:**
- Mano de obra: 35 días naturales.
- Refacciones: según política del fabricante.
- Software: sin garantía.

**Reglas de contenido:**
- Si el JSON trae precio → mostrarlo como referencia.
- Si NO trae precio → "cotización tras diagnóstico", sin inventar cifras.
- Nunca poner tiempos específicos que no vengan en el JSON.
- Nunca decir que el diagnóstico fue gratis — explicar la política real.
- No mencionar datos del cliente.

#### Estructura del artículo

- title tag: máximo 60 caracteres con keyword + ciudad + Ciselaptop
- meta description: máximo 155 caracteres
- H1: título natural del caso
- Intro: cómo llegó el equipo y qué tenía
- Answer capsule: definición del tipo de reparación en 2-3 líneas
- Síntomas: lista de lo que presentaba
- Proceso paso a paso: H3 por cada etapa
- Galería: grid 2-3 columnas con las fotos de `img/blog/{slug}/`
- Tabla de referencia: solo con datos que vengan en el JSON
- CTA intermedio (fondo #f0f2fc, botón navy)
- FAQ: 3-4 preguntas relevantes al tipo de reparación
- CTA final (dark-section, botón rojo)
- Schema JSON-LD: Article + FAQPage
- Todas las URLs en schema con https://www.ciselaptop.com

#### Fecha visible en el hero — usar `<time>` semántico

La fecha del artículo dentro del hero **siempre** debe usar el tag `<time>` con su atributo `datetime` en formato ISO (`YYYY-MM-DD`). Nunca usar `<span>` para la fecha:

```html
<span>·</span><time datetime="2026-08-14">14 de agosto de 2026</time>
```

Ejemplo completo del bloque autor/fecha en el hero:

```html
<div class="flex items-center gap-2 mt-4 text-sm" style="color:rgba(255,255,255,0.60);">
  <svg ...icono usuario.../>
  <a href="/quienes-somos" class="font-medium hover:underline" style="color:#FFD700;">Ciselaptop</a>
  <span>·</span><time datetime="YYYY-MM-DD">DD de mes de YYYY</time>
</div>
```

O en el formato `<p>` alternativo (artículos sin el bloque flex de autor):

```html
<p class="text-sm mt-4" style="color:rgba(255,255,255,0.60);">
  <a href="/quienes-somos" class="font-medium hover:underline" style="color:#FFD700;">Ciselaptop</a>
  <span>·</span><time datetime="YYYY-MM-DD">DD de mes de YYYY</time>
</p>
```

**NO guardes el HTML en `blog/` todavía.**
Guárdalo en `_queue/listos/` con este nombre:
`{TIMESTAMP}-{slug}.html`
donde TIMESTAMP = fecha y hora actual en formato YYYYMMDDHHMMSS.

---

### PASO 4 — Generar el archivo de metadatos

Para cada artículo, crea `_queue/listos/{TIMESTAMP}-{slug}.json`
con la misma marca de tiempo que el HTML:

```json
{
  "slug": "reparacion-hp-t250-oaxaca",
  "titulo": "El title tag exacto del artículo",
  "categoria": "Impresoras",
  "fecha": "2026-08-13",
  "excerpt": "1-2 líneas resumiendo el caso: marca, modelo, falla resuelta.",
  "imagenHero": "/img/blog/reparacion-hp-t250-oaxaca/hero.webp"
}
```

---

### PASO 5 — Eliminar el JSON de la cola

```bash
rm _queue/orden-{id}.json
```

---

### PASO 6 — Commit y push

Cuando hayas procesado todos los JSONs de la cola:

```bash
git add .
git commit -m "Queue: {N} artículos listos para publicación programada"
git push origin main
```

---

### PASO 7 — Reportar al usuario

Indica:
- Cuántos artículos procesaste y sus slugs
- Cuántas fotos descargaste en total
- Que están en `_queue/listos/` esperando publicación
- Que GitHub Actions los publicará uno por día automáticamente
- Que NO hace falta hacer nada más hasta que llegue el email de notificación
