from __future__ import annotations

from datetime import date
from random import SystemRandom

_random = SystemRandom()


def build_receipt_number(prefix: str = "GM", today: date | None = None) -> str:
    """Build a receipt number when WhatsApp did not provide one."""
    return str(_random.randint(10000, 99999))


def build_reference(prefix: str = "SERV", today: date | None = None) -> str:
    """Build a short reference when WhatsApp did not provide one."""
    today = today or date.today()
    clean_prefix = str(prefix or "SERV").strip() or "SERV"
    return f"{clean_prefix}-{today:%Y-%m}"
