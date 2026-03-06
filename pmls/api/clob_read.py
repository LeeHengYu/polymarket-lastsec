from __future__ import annotations

from py_clob_client.clob_types import BookParams

from pmls.credentials import public_client


def fetch_spread(token_id: str) -> str:
    client = public_client()
    resp = client.get_spread(token_id)
    return resp.get("spread", "-")


def fetch_tick_size(token_id: str) -> str:
    client = public_client()
    return client.get_tick_size(token_id)


def fetch_midpoints(token_ids: list[str]) -> dict[str, str]:
    client = public_client()
    return client.get_midpoints([BookParams(token_id=tid) for tid in token_ids])
