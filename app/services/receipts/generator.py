from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader

from .numbering import build_receipt_number, build_reference
from .vat import calculate_vat, format_eur


class ReceiptGenerator:
    """Render receipt templates for the WhatsApp/FastAPI bot."""

    def __init__(self, templates_root: Path | None = None) -> None:
        self.templates_root = templates_root or Path(__file__).resolve().parents[2] / "templates" / "receipts"

    def render_html(self, data: dict[str, Any], template_name: str = "global-move") -> str:
        template_dir = self.templates_root / template_name
        context = self._build_context(template_dir, data)

        env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=True,
            keep_trailing_newline=True,
        )
        html = env.get_template("template.html").render(**context)

        styles_uri = (template_dir / "styles.css").resolve().as_uri()
        assets_uri = (template_dir / "assets").resolve().as_uri().rstrip("/") + "/"
        return html.replace("./styles.css", styles_uri).replace("./assets/", assets_uri)

    def save_html(self, data: dict[str, Any], output_path: Path, template_name: str = "global-move") -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(self.render_html(data, template_name), encoding="utf-8")
        return output_path

    async def save_pdf(self, data: dict[str, Any], output_path: Path, template_name: str = "global-move") -> Path:
        """Render a PDF with Playwright. Requires `playwright install chromium`."""
        from playwright.async_api import async_playwright

        html = self.render_html(data, template_name)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch()
            page = await browser.new_page(viewport={"width": 794, "height": 1123})
            await page.set_content(html, wait_until="networkidle")
            await page.pdf(
                path=str(output_path),
                format="A4",
                print_background=True,
                margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
            )
            await browser.close()

        return output_path

    def _build_context(self, template_dir: Path, data: dict[str, Any]) -> dict[str, Any]:
        defaults = self._load_defaults(template_dir)
        context = {**defaults, **{key: value for key, value in data.items() if value is not None}}

        prefix = str(context.get("numbering_prefix") or "GM")
        reference_prefix = str(context.get("reference_prefix") or "SERV")
        if self._is_placeholder(context.get("receipt_number")):
            context["receipt_number"] = build_receipt_number(prefix)
        if self._is_placeholder(context.get("reference")):
            context["reference"] = build_reference(reference_prefix)

        amount = context.get("amount")
        if amount is not None:
            vat = calculate_vat(
                amount=amount,
                vat_rate=context.get("vat_rate", 21),
                mode=context.get("vat_mode", "none"),
            )
            context["base_amount"] = format_eur(vat["base_amount"])
            context["vat_amount"] = format_eur(vat["vat_amount"])
            if self._is_placeholder(context.get("total")):
                context["total"] = format_eur(vat["total_amount"])
            if self._is_placeholder(context.get("price")):
                context["price"] = context["base_amount"]
            if self._is_placeholder(context.get("partial_amount")):
                context["partial_amount"] = context["total"]

        return context

    @staticmethod
    def _load_defaults(template_dir: Path) -> dict[str, Any]:
        sample_path = template_dir / "sample-data.json"
        if not sample_path.exists():
            return {}
        return json.loads(sample_path.read_text(encoding="utf-8"))

    @staticmethod
    def _is_placeholder(value: Any) -> bool:
        if value is None or value == "":
            return True
        if not isinstance(value, str):
            return False
        stripped = value.strip()
        return stripped.startswith("{{") and stripped.endswith("}}")
