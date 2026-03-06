from __future__ import annotations

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY, SELL

from pmls.models import PostOrderResult


def run_limito(
    client: ClobClient,
    token_id: str,
    bet: float,
    price: float,
    side: str = BUY,
) -> PostOrderResult:
    if price <= 0:
        return PostOrderResult(success=False, order_id=None, errorMsg="Invalid input")

    order = client.create_order(
        OrderArgs(
            token_id=token_id,
            price=price,
            side=side,
            size=bet if side == SELL else bet / price,
        ),
    )

    resp = client.post_order(order, OrderType.GTC)

    try:
        resp = resp[0] if isinstance(resp, list) else resp
    except Exception as e:
        return PostOrderResult(success=False, order_id=None, errorMsg=e)

    if resp is None:
        return PostOrderResult(success=False, order_id=None, errorMsg="Order failed.")

    return PostOrderResult(
        success=bool(resp.get("success") and resp.get("orderID")),
        order_id=resp.get("orderID", ""),
        errorMsg=resp.get("errorMsg", ""),
    )
