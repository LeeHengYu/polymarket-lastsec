from __future__ import annotations

from py_clob_client.client import ClobClient, MarketOrderArgs
from py_clob_client.clob_types import OrderType
from py_clob_client.order_builder.constants import BUY

from pmls.models import PostOrderResult


def run_marketo(
    client: ClobClient,
    token_id: str,
    bet: float,
    max_price: float,
    side: str = BUY,
) -> PostOrderResult:

    order = client.create_market_order(
        MarketOrderArgs(
            token_id=token_id,
            side=side,
            amount=bet,
            price=max_price,
        )
    )
    
    resp = client.post_order(order, OrderType.FOK)

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
