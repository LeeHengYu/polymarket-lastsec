from __future__ import annotations

import requests

from pmls.constants import DEFAULT_CLOB_HOST, DEFAULT_TIMEOUT_SECONDS


def fetch_server_time() -> int:
    resp = requests.get(
        f"{DEFAULT_CLOB_HOST}/time",
        timeout=DEFAULT_TIMEOUT_SECONDS,
    )
    resp.raise_for_status()
    return resp.json()
