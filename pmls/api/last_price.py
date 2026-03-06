from __future__ import annotations

from py_clob_client.clob_types import BookParams

from pmls.credentials import public_client


def fetch_last_trade_prices(token_ids: list[str]) -> list[dict]:
    client = public_client()
    return client.get_last_trades_prices([BookParams(token_id=tid) for tid in token_ids])
