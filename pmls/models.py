from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from py_clob_client.clob_types import OrderSummary

@dataclass
class DisplayOutcome:
    outcome: str
    token_id: str
    asks: list[OrderSummary]
    bids: list[OrderSummary]


@dataclass
class PostOrderResult:
    success: bool
    order_id: Optional[str]
    errorMsg: Optional[str]

@dataclass
class OpenOrder:
    order_id: str
    token_id: str
    address: str 
    side: str # 'BUY' or 'SELL'
    outcome: str
    size: int
    price: float
    
@dataclass
class CancelOrderResponse:
    canceled: list[str] # order ID
    not_canceled: dict[str, Any] # Record

@dataclass
class TradeHistory:
    asset_id: Optional[str]
    id: Optional[str]
    last_update: Optional[str]
    market: Optional[str]
    match_time: Optional[str]
    outcome: Optional[str]
    price: Optional[str]
    side: Optional[str]
    size: Optional[str]
    status: Optional[str]


@dataclass
class Position:
    avgPrice: Optional[float]
    cashPnl: Optional[float]
    curPrice: Optional[float]
    currentValue: Optional[float]
    initialValue: Optional[float]
    totalBought: Optional[float]
    realizedPnl: Optional[float]
    percentPnl: Optional[float]
    title: Optional[str]
    size: Optional[float]
    outcome: Optional[str]
    asset: Optional[str]
