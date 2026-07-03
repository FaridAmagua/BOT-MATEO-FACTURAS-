from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ReceiptInput(BaseModel):
    template: Literal["global-move", "nova-move", "blank"] = "global-move"
    document_title: str = "Recibo"

    company_name: str | None = None
    company_address: str | None = None
    company_city: str | None = None
    company_tax_id: str | None = None

    client_name: str | None = None
    client_email: str | None = None
    client_phone: str | None = None

    receipt_number: str | None = None
    reference: str | None = None
    description: str | None = None
    price: str | None = None
    units: str = "1,00"
    discount: str = "0"
    partial_amount: str | None = None
    total: str | None = None

    amount: float | None = None
    vat_mode: Literal["none", "add", "included"] = "none"
    vat_rate: float = 21

    payment_method: str | None = None
    payment_date: str | None = None

    numbering_prefix: str = Field(default="GM", description="Prefix used when receipt_number is missing.")
    reference_prefix: str = Field(default="SERV", description="Prefix used when reference is missing.")
