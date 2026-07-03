from __future__ import annotations

from datetime import date
from random import SystemRandom

_random = SystemRandom()


def build_receipt_number(prefix: str = "GM", today: date | None = None) -> str:
    """Build a receipt number when WhatsApp did not provide one."""
    today = today or date.today()
    suffix = _random.randint(1000, 9999)
    return f"{prefix}-{today:%Y%m%d}-{suffix}"


def build_reference(prefix: str = "SERV", today: date | None = None) -> str:
    """Build a short reference when WhatsApp did not provide one."""
    today = today or date.today()
    suffix = _random.randint(1000, 9999)
    return f"{prefix}-{today:%Y-%m}-{suffix}"
