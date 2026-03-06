from __future__ import annotations

from typing import Any, Optional

from py_clob_client import ClobClient
from py_clob_client.clob_types import OpenOrderParams

from pmls.models import OpenOrder


def list_orders(cli: ClobClient, params: Optional[OpenOrderParams] = None) -> list[OpenOrder]:
    res = cli.get_orders(params)

    return [
        OpenOrder(
            order_id=o.get("id"),
            token_id=o.get("asset_id"),
            address=o.get("maker_address"),
            side=o.get("side"),
            outcome=o.get("outcome"),
            size=int(o.get("original_size")),
            price=float(o.get("price")),
        )
        for o in res
    ]


def fetch_order_by_id(cli: ClobClient, order_id: str) -> dict[str, Any]:
    return cli.get_order(order_id)