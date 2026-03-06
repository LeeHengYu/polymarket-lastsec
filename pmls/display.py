from __future__ import annotations

from datetime import datetime
from decimal import Decimal, InvalidOperation

from py_clob_client.clob_types import OrderSummary

from pmls.models import DisplayOutcome


def _fmt_price(raw: str) -> str:
    if not raw:
        return "-"
    try:
        value = Decimal(raw)
        if Decimal("0") <= value <= Decimal("1"):
            value = value * Decimal("100")
        s = format(value, "f")
        result = s.rstrip("0").rstrip(".") if "." in s else s
        return result if result not in {"", "-0"} else "0"
    except (InvalidOperation, TypeError, ValueError):
        return "-"


def _fmt_size(raw: str) -> str:
    if not raw:
        return "-"
    try:
        value = Decimal(raw)
        s = format(value, "f")
        result = s.rstrip("0").rstrip(".") if "." in s else s
        return result if result not in {"", "-0"} else "0"
    except (InvalidOperation, TypeError, ValueError):
        return "-"


def _print_levels(levels: list[OrderSummary], empty_label: str = "-") -> None:
    print(f"|{'PRICE':>6}|{'SIZE':>11}|")
    if not levels:
        print(f"|{empty_label:>6}|{'-':>11}|")
        return
    for level in levels:
        price = _fmt_price(str(level.price) if level.price is not None else "")
        size = _fmt_size(str(level.size) if level.size is not None else "")
        print(f"|{price:>6}|{size:>11}|")


def _print_outcome_table(snapshot: DisplayOutcome) -> None:
    print(f"Outcome: {snapshot.outcome} (Token: {snapshot.token_id})")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f')}")
    print("Asks")
    _print_levels(snapshot.asks)
    print("")
    print("Bids")
    _print_levels(snapshot.bids)
    print("")
