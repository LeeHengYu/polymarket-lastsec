from __future__ import annotations

import os
from dataclasses import fields
from typing import Optional

import requests

from pmls.models import Position

POSITIONS_URL = "https://data-api.polymarket.com/positions"
POSITION_KEYS = {f.name for f in fields(Position)}

def list_positions(user: str | None = None) -> list[Position]:
    resolved_user = user or os.environ.get("POLY_ADDR")
    if not resolved_user:
        raise ValueError("Missing user. Provide --user or set POLY_ADDR in environment.")

    try:
        resp = requests.get(POSITIONS_URL, params={"user": resolved_user}, timeout=10)
    except requests.RequestException as exc:
        raise RuntimeError("Unable to reach positions API.") from exc

    if not resp.ok:
        raise RuntimeError(resp.text)

    try:
        payload = resp.json()
    except Exception as exc:
        raise RuntimeError(resp.text) from exc


    positions: list[Position] = []
    for item in payload:

        kwargs = {k: item.get(k) for k in POSITION_KEYS}
        positions.append(Position(**kwargs))

    return positions


def resolve_sell_all_size(token_id: str) -> Optional[float]:
    positions = list_positions()
    match = next((p for p in positions if p.asset == token_id), None)
    if match is None or match.size is None:
        return None
    return match.size
