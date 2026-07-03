# BOT Mateo Facturas

Modulo de recibos/facturas para integrar con FastAPI y un bot de WhatsApp.

## Estructura

```text
app/
├── services/
│   └── receipts/
│       ├── generator.py
│       ├── numbering.py
│       ├── schemas.py
│       └── vat.py
└── templates/
    └── receipts/
        ├── global-move/
        ├── nova-move/
        └── blank/
```

## Uso basico

```python
from pathlib import Path

from app.services.receipts import ReceiptGenerator


generator = ReceiptGenerator()

data = {
    "client_name": "Cliente de prueba",
    "client_email": "cliente@email.com",
    "client_phone": "+34 600 000 000",
    "description": "Servicio de relocation",
    "amount": 900,
    "vat_mode": "add",
    "vat_rate": 21,
    "payment_method": "Via transferencia",
    "payment_date": "2026/07/03",
}

html = generator.render_html(data, template_name="global-move")
```

## Generar PDF

Instala Chromium una vez:

```bash
playwright install chromium
```

Y luego:

```python
await generator.save_pdf(
    data,
    Path("storage/generated-receipts/receipt.pdf"),
    template_name="global-move",
)
```

## IVA

Si el importe no incluye IVA:

```python
{"amount": 900, "vat_mode": "add", "vat_rate": 21}
```

Resultado:

```text
base = 900
iva = 189
total = 1089
```

Si el importe ya incluye IVA:

```python
{"amount": 900, "vat_mode": "included", "vat_rate": 21}
```

Resultado:

```text
base = 743.80
iva = 156.20
total = 900
```

## Plantillas

- `global-move`: plantilla principal. Datos de empresa por defecto: GLOBAL MOVE, C/Ortega y Gasset 25, (28007) Madrid, NIF B-14464336.
- `nova-move`: misma plantilla con NOVA MOVE.
- `blank`: plantilla base para crear nuevas variantes.
