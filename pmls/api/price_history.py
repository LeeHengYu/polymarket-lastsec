from __future__ import annotations

import requests

from pmls.constants import DEFAULT_CLOB_HOST, DEFAULT_TIMEOUT_SECONDS


def fetch_price_history(
    token_id: str,
    interval: str = "1d",
    fidelity: int = 1,
    start_ts: int | None = None,
    end_ts: int | None = None,
) -> list[dict]:
    params = {
        "market": token_id,
        "interval": interval,
        "fidelity": fidelity,
    }
    if start_ts is not None:
        params["startTs"] = start_ts
    if end_ts is not None:
        params["endTs"] = end_ts

    resp = requests.get(
        f"{DEFAULT_CLOB_HOST}/prices-history",
        params=params,
        timeout=DEFAULT_TIMEOUT_SECONDS,
    )
    resp.raise_for_status()
    return resp.json().get("history", [])
