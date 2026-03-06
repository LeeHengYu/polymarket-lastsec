from __future__ import annotations

import sys

from pmls.api.positions import resolve_sell_all_size
from pmls.credentials import create_clob_client_from_env
from pmls.trading.limit_order import run_limito
from pmls.trading.market_order import run_marketo


def _cmd_marketo(args):
    bet = args.bet
    price_display = args.price
    token_id = args.token_id

    if bet == -1 and args.side == "SELL":
        try:
            bet = resolve_sell_all_size(token_id)
        except Exception as exc:
            print(f"Failed to fetch positions: {exc}", file=sys.stderr)
            return 1
        if bet is None:
            print(f"No open position for token {token_id}.", file=sys.stderr)
            return 1
    elif bet <= 0:
        print("Invalid input", file=sys.stderr)
        return 1
    if price_display is not None and (price_display <= 0 or price_display > 100):
        print("Invalid input", file=sys.stderr)
        return 1

    try:
        client = create_clob_client_from_env()
    except Exception as exc:
        print(exc, file=sys.stderr)
        return 1

    try:
        max_price = 1.0 if price_display is None else price_display / 100
        result = run_marketo(client, token_id, bet, max_price, side=args.side)
        print('Note: Marketable orders in sport market are delayed by 3 seconds.')
    except Exception as e:
        print(e, file=sys.stderr)
        return 1

    if not result:
        print("No available orders.")
        return 0

    if result.success:
        print(f"{args.side} order {result.order_id} submitted.")
        return 0
    else:
        print(result.errorMsg)
        return 1


def _cmd_limito(args):
    bet = args.bet
    price_display = args.price
    token_id = args.token_id

    if bet == -1 and args.side == "SELL":
        try:
            bet = resolve_sell_all_size(token_id)
        except Exception as exc:
            print(f"Failed to fetch positions: {exc}", file=sys.stderr)
            return 1
        if bet is None:
            print(f"No open position for token {token_id}.", file=sys.stderr)
            return 1
    if bet <= 0 or price_display <= 0 or price_display > 100:
        print("Invalid input", file=sys.stderr)
        return 1

    try:
        client = create_clob_client_from_env()
    except Exception as exc:
        print(exc, file=sys.stderr)
        return 1

    try:
        result = run_limito(client, token_id, bet, price_display / 100, side=args.side)
    except Exception as e:
        print(e, file=sys.stderr)
        return 1

    if not result:
        print("No available orders.")
        return 0

    if result.success:
        print(f"{args.side} order {result.order_id} submitted.")
        return 0

    print(result.errorMsg)
    return 1


def register(subparsers):
    # MARKETO
    marketo_parser = subparsers.add_parser(
        "marketo", help="Place a market order (BUY or SELL) filled immediately at best available price."
    )
    marketo_parser.add_argument(
        "--token-id", type=str, required=True, dest="token_id",
        help="Token ID to trade.",
    )
    marketo_parser.add_argument(
        "--bet", type=float, required=True,
        help="USDC to spend (BUY) or number of shares to sell (SELL). Use -1 with SELL to sell entire position."
    )
    marketo_parser.add_argument(
        "--price",
        type=float,
        default=None,
        dest="price",
        help="Max price cap in cents 0-100 (BUY only). Order rejected if market exceeds this.",
    )
    marketo_parser.add_argument(
        "--side",
        type=str,
        default="BUY",
        choices=["BUY", "SELL"],
        dest="side",
        help="BUY (default) or SELL.",
    )
    marketo_parser.set_defaults(handler=_cmd_marketo)

    # LIMITO
    limito_parser = subparsers.add_parser(
        "limito", help="Place a GTC limit order at an explicit price."
    )
    limito_parser.add_argument(
        "--token-id", type=str, required=True, dest="token_id",
        help="Token ID to trade.",
    )
    limito_parser.add_argument(
        "--bet", type=float, required=True,
        help="USDC to spend (BUY) or number of shares to sell (SELL). Use -1 with SELL to sell entire position."
    )
    limito_parser.add_argument(
        "--price",
        type=float,
        required=True,
        dest="price",
        help="Limit price in cents 0-100.",
    )
    limito_parser.add_argument(
        "--side",
        type=str,
        default="BUY",
        choices=["BUY", "SELL"],
        dest="side",
        help="Order side: BUY (default) or SELL.",
    )
    limito_parser.set_defaults(handler=_cmd_limito)
