from __future__ import annotations

from pmls.api.gamma_client import extract_outcome_token_ids, fetch_market_by_token_id
from pmls.credentials import public_client
from pmls.models import DisplayOutcome


def fetch_orderbook_snapshots(
    token_ids: list[str],
    depth: int,
) -> list[DisplayOutcome]:
    client = public_client()
    snapshots: list[DisplayOutcome] = []
    for token_id in token_ids:
        market = fetch_market_by_token_id(token_id)
        outcome_map = extract_outcome_token_ids(market)
        outcome_name = next(
            (name for name, tid in outcome_map.items() if tid == token_id),
            token_id,
        )

        orderbook = client.get_order_book(token_id)
        asks = sorted(
            (item for item in orderbook.asks if item.price),
            key=lambda item: float(item.price),
        )[:depth][::-1]
        bids = sorted(
            (item for item in orderbook.bids if item.price),
            key=lambda item: float(item.price),
            reverse=True,
        )[:depth]
        snapshots.append(DisplayOutcome(outcome=outcome_name, token_id=token_id, asks=asks, bids=bids))
    return snapshots
