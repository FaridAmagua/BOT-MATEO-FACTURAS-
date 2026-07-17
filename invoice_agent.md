# Invoice Agent Guide

Este documento sirve como guia para un agente que tenga que ayudar con el modulo de recibos/facturas de este repositorio.

El objetivo del agente es responder preguntas del usuario, modificar campos de las plantillas y generar recibos/PDFs sin romper el diseno visual existente.

## Resumen Del Modulo

El modulo esta pensado para integrarse en un backend FastAPI conectado a un bot de WhatsApp.

El flujo esperado es:

1. El bot recibe datos del usuario por WhatsApp.
2. FastAPI normaliza esos datos.
3. `ReceiptGenerator` rellena una plantilla HTML.
4. Opcionalmente se calcula IVA.
5. Opcionalmente se genera PDF con Playwright.

Ruta principal del modulo:

```text
app/services/receipts/
```

Plantillas:

```text
app/templates/receipts/
```

## Archivos Importantes

```text
app/services/receipts/generator.py
```

Renderiza HTML y PDF. Carga los datos por defecto de `sample-data.json`, mezcla los datos recibidos del bot y rellena `template.html`.

```text
app/services/receipts/numbering.py
```

Genera numero de recibo y referencia cuando no vienen en los datos.

```text
app/services/receipts/vat.py
```

Calcula base, IVA y total.

```text
app/services/receipts/schemas.py
```

Modelo Pydantic de entrada para datos de recibos.

## Plantillas Disponibles

```text
app/templates/receipts/global-move/
```

Plantilla principal. Usa GLOBAL MOVE con estos datos por defecto:

```text
GLOBAL MOVE
C/Ortega y Gasset 25
(28007) Madrid
NIF: B-14464336
```

```text
app/templates/receipts/nova-move/
```

Misma estructura visual, pero para NOVA MOVE.

```text
app/templates/receipts/blank/
```

Plantilla base sin datos concretos. Sirve para crear nuevas variantes.

## Estructura De Cada Plantilla

Cada plantilla tiene:

```text
template.html
styles.css
sample-data.json
schema.json
assets/
```

`template.html` contiene los placeholders tipo:

```html
{{client_name}}
{{receipt_number}}
{{reference}}
{{description}}
{{total}}
```

`styles.css` contiene todo el diseno visual. No usar estilos inline.

`sample-data.json` contiene valores por defecto de la plantilla.

`assets/logo.png` contiene el logo.

`assets/watermark.png` contiene la marca de agua.

## Campos Que Se Pueden Cambiar

Campos habituales:

```text
company_name
company_address
company_city
company_tax_id
client_name
client_email
client_phone
receipt_number
reference
description
price
units
discount
partial_amount
total
payment_method
payment_date
```

Campos para calculo:

```text
amount
vat_mode
vat_rate
```

`vat_mode` puede ser:

```text
none
add
included
```

## Como Responder Si El Usuario Quiere Cambiar Un Campo

Si el usuario quiere cambiar un texto fijo de empresa, editar:

```text
app/templates/receipts/{template}/sample-data.json
```

Ejemplo:

```json
{
  "company_name": "GLOBAL MOVE"
}
```

Si el usuario quiere cambiar el texto visible fijo de la plantilla, editar:

```text
app/templates/receipts/{template}/template.html
```

Si el usuario quiere cambiar posicion, fuente, margenes, lineas, logo, watermark o estilo visual, editar:

```text
app/templates/receipts/{template}/styles.css
```

Importante: si un cambio visual debe afectar a todas las plantillas, aplicarlo a:

```text
app/templates/receipts/global-move/styles.css
app/templates/receipts/nova-move/styles.css
app/templates/receipts/blank/styles.css
```

## Reglas De Diseno

Mantener siempre:

- A4.
- Una sola pagina.
- `@page { size: A4; margin: 0; }`.
- HTML semantico.
- CSS vanilla.
- Sin JavaScript.
- Sin frameworks CSS.
- Logo como imagen PNG.
- Watermark como imagen independiente.

No mover el layout salvo que el usuario lo pida claramente.

No convertir el diseno a responsive movil.

No meter estilos inline.

No borrar placeholders si la plantilla debe seguir siendo dinamica.

## Estilo Actual

Las tres plantillas usan la misma tipografia base:

```css
--body-font: "Segoe UI", "Aptos", "Helvetica Neue", Arial, sans-serif;
```

El total esta configurado como texto normal:

```css
.total-line strong {
  font-size: 15.6px;
  font-weight: 400;
}
```

El total esta alineado con la linea de pago:

```css
.total-line {
  top: 0;
  gap: 4mm;
}
```

## Como Generar Un HTML

Ejemplo basico:

```python
from pathlib import Path

from app.services.receipts import ReceiptGenerator


generator = ReceiptGenerator()

data = {
    "client_name": "FRANCIO RUIZ",
    "description": "Honorarios servicio alquiler piso",
    "price": "2300 €",
    "units": "1,00",
    "discount": "0",
    "partial_amount": "2300 €",
    "total": "2300 €",
    "payment_method": "Via transferencia",
    "payment_date": "18/06/2026",
}

generator.save_html(
    data,
    Path("generated/factura.html"),
    template_name="global-move",
)
```

## Como Generar Un PDF

Primero instalar Chromium de Playwright:

```bash
playwright install chromium
```

Luego:

```python
from pathlib import Path

from app.services.receipts import ReceiptGenerator


generator = ReceiptGenerator()

await generator.save_pdf(
    data,
    Path("generated/factura.pdf"),
    template_name="global-move",
)
```

## Numeracion Y Referencia

Si `receipt_number` o `reference` vienen vacios o como placeholders, el sistema los genera automaticamente.

Ejemplo de numero:

```text
GM-20260709-8020
```

Ejemplo de referencia:

```text
SERV-2026-07-6244
```

La logica esta en:

```text
app/services/receipts/numbering.py
```

Si el usuario pide numeracion fiscal estricta o secuencial, no usar aleatorio. Recomendar guardar el ultimo numero en base de datos.

## IVA

La logica esta en:

```text
app/services/receipts/vat.py
```

Si el importe no incluye IVA:

```python
{
    "amount": 900,
    "vat_mode": "add",
    "vat_rate": 21,
}
```

Resultado:

```text
base = 900
iva = 189
total = 1089
```

Si el importe ya incluye IVA:

```python
{
    "amount": 900,
    "vat_mode": "included",
    "vat_rate": 21,
}
```

Resultado:

```text
base = 743.80
iva = 156.20
total = 900
```

Si no hay IVA:

```python
{
    "amount": 900,
    "vat_mode": "none",
}
```

## Campos Opcionales De Cliente

Los campos de cliente pueden venir vacios:

```text
client_email
client_phone
```

Actualmente el modulo renderiza lo que reciba. Si se quiere ocultar una linea vacia de email o telefono, modificar `template.html` para usar condicionales Jinja:

```html
{% if client_email %}
  <p class="contact-line">
    <img src="./assets/icons/email.png" alt="" aria-hidden="true">
    <span>{{ client_email }}</span>
  </p>
{% endif %}
```

Nota: ahora los placeholders usan `{{client_email}}` sin espacios. Jinja tambien acepta `{{ client_email }}`.

## Como Cambiar El Logo

Sustituir:

```text
app/templates/receipts/{template}/assets/logo.png
```

No incrustar SVG en HTML.

Mantener PNG con fondo transparente si es posible.

## Como Cambiar La Marca De Agua

Sustituir:

```text
app/templates/receipts/{template}/assets/watermark.png
```

La posicion/opacidad se controla en:

```css
.watermark {
  position: absolute;
  opacity: 0.58;
}
```

## Como Crear Una Nueva Plantilla

Copiar `blank`:

```bash
cp -r app/templates/receipts/blank app/templates/receipts/nueva-plantilla
```

En Windows PowerShell:

```powershell
Copy-Item -Recurse app\templates\receipts\blank app\templates\receipts\nueva-plantilla
```

Despues ajustar:

```text
sample-data.json
template.html
styles.css
assets/logo.png
assets/watermark.png
```

## Comprobaciones Antes De Terminar

Antes de responder al usuario despues de un cambio:

1. Comprobar que el HTML no rompe la estructura A4.
2. Comprobar que `template.html` conserva los placeholders dinamicos.
3. Comprobar que no se tocaron plantillas no solicitadas, salvo que el usuario pidiera cambios globales.
4. Si se genera PDF, verificar que existe el archivo.
5. Si el cambio debe quedar en GitHub, hacer commit y push.

Comandos utiles:

```bash
git status --short
git diff --stat
git log --oneline -5
```

## Politica De Git

Repositorio:

```text
https://github.com/FaridAmagua/BOT-MATEO-FACTURAS-.git
```

Si el usuario pide subir cambios:

```bash
git add .
git commit -m "Describe receipt template change"
git push
```

No subir archivos generados:

```text
generated/
storage/
*.pdf
```

Estos ya estan en `.gitignore`.

## Preguntas Frecuentes Del Usuario

### "Quiero cambiar el nombre de la empresa"

Editar `sample-data.json` de la plantilla correspondiente.

### "Quiero cambiar el total o el importe"

Si es una factura concreta, cambiar los datos enviados a `ReceiptGenerator`.

Si es un valor por defecto, cambiar `sample-data.json`.

### "Quiero que calcule IVA"

Usar `amount`, `vat_mode` y `vat_rate`.

### "Quiero mover una seccion"

Editar coordenadas CSS en `styles.css`. La plantilla usa posicionamiento absoluto en A4, asi que cambios pequenos pueden mover mucho visualmente.

### "Quiero que todas las plantillas se vean igual"

Aplicar el mismo cambio CSS a las tres carpetas:

```text
global-move
nova-move
blank
```

### "Quiero generar una factura para una persona"

Usar `ReceiptGenerator` con `template_name="global-move"` salvo que el usuario pida otra plantilla.

Datos minimos recomendados:

```python
{
    "client_name": "...",
    "description": "...",
    "total": "... €",
    "price": "... €",
    "partial_amount": "... €",
    "units": "1,00",
    "discount": "0",
    "payment_method": "Via transferencia",
    "payment_date": "dd/mm/yyyy",
}
```

## Notas Para El Agente

- Responder siempre en espanol si el usuario habla en espanol.
- Ser directo y practico.
- Si el usuario pide modificar una plantilla, hacer el cambio en archivos reales.
- Si el usuario pide PDF, generarlo en `generated/`.
- Si el usuario pide subir a GitHub, confirmar commit y hash.
- No redisenar la plantilla salvo que el usuario lo pida.
- No inventar datos fiscales si el usuario no los da.
- No incluir DNI si el usuario dice que no lo ponga.
