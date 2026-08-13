# Schema del JSON de cola

Cada archivo orden-{id}.json que llega de CISEFLOW tiene esta estructura:

```json
{
  "version": "1",
  "ordenId": "123",
  "fecha": "2026-08-12",           // YYYY-MM-DD — se usa en el artículo
  "slug": "bisagra-rota-hp-15-oaxaca",  // URL final del blog post
  "categoria": "Bisagras y carcasas",
  "marca": "HP",
  "modelo": "15-P20",
  "falla": "Bisagra rota y batería no carga",
  "solucion": "Reparación de bisagras nivel 2 con malla y resinas",
  "precio": 650,                   // null si no hay precio público
  "garantia": "35 días en mano de obra",
  "fotos": [
    {
      "url": "https://cdn.do.com/.../foto1.jpg",
      "alt": "Descripción de la foto",
      "esHero": true               // true solo en la primera foto
    }
  ]
}
```
