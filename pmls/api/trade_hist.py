from __future__ import annotations

from dataclasses import fields

from py_clob_client import ClobClient, TradeParams

from pmls.api.gamma_client import fetch_market_by_token_id
from pmls.models import TradeHistory

TRADE_HISTORY_KEYS = {f.name for f in fields(TradeHistory)}


def list_trade_history(
    cli: ClobClient,
    token_id: str = None,
    before: int = None,
    after: int = None,
    market: str = None,
) -> list[TradeHistory]:
    
    
    res = cli.get_trades(
        TradeParams(
            asset_id=token_id,
            before=before,
            after=after,
            market=market,
        )
    )

    trades: list[TradeHistory] = []
    for o in res:
        trade_kwargs = {k: o.get(k) for k in TRADE_HISTORY_KEYS}
        trades.append(TradeHistory(**trade_kwargs))

    return trades


def filter_trades_by_query(trades: list[TradeHistory], query: str) -> list[TradeHistory]:
    q = query.lower()
    market_cache: dict[str, dict | None] = {}
    matched: list[TradeHistory] = []
    for trade in trades:
        # Fast path: outcome contains keyword
        if trade.outcome and q in trade.outcome.lower():
            matched.append(trade)
            continue

        # Slow path: look up market question via GAMMA; skip on any error
        if trade.asset_id:
            if trade.asset_id not in market_cache:
                try:
                    market_cache[trade.asset_id] = fetch_market_by_token_id(trade.asset_id)
                except Exception:
                    market_cache[trade.asset_id] = None
            market = market_cache[trade.asset_id]
            if market:
                question = (market.get("description") or "").lower()
                if q in question:
                    matched.append(trade)
    return matched
