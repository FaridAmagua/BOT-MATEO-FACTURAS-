from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Literal, TypedDict

VatMode = Literal["none", "add", "included"]


class VatResult(TypedDict):
    base_amount: Decimal
    vat_amount: Decimal
    total_amount: Decimal
    vat_rate: Decimal
    vat_mode: VatMode


def _money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_vat(
    amount: int | float | str | Decimal,
    vat_rate: int | float | str | Decimal = Decimal("21"),
    mode: VatMode = "none",
) -> VatResult:
    """Calculate base, VAT and total from a gross or net amount."""
    amount_decimal = Decimal(str(amount))
    rate_decimal = Decimal(str(vat_rate))
    multiplier = Decimal("1") + (rate_decimal / Decimal("100"))

    if mode == "add":
        base_amount = amount_decimal
        vat_amount = base_amount * (rate_decimal / Decimal("100"))
        total_amount = base_amount + vat_amount
    elif mode == "included":
        total_amount = amount_decimal
        base_amount = total_amount / multiplier
        vat_amount = total_amount - base_amount
    else:
        base_amount = amount_decimal
        vat_amount = Decimal("0")
        total_amount = amount_decimal

    return {
        "base_amount": _money(base_amount),
        "vat_amount": _money(vat_amount),
        "total_amount": _money(total_amount),
        "vat_rate": rate_decimal,
        "vat_mode": mode,
    }


def format_eur(amount: Decimal) -> str:
    formatted = f"{amount:.2f}".replace(".", ",")
    if formatted.endswith(",00"):
        formatted = formatted[:-3]
    return f"{formatted} €"
