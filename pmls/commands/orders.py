from __future__ import annotations

import json
import sys

from pmls.api.get_order import fetch_order_by_id, list_orders
from pmls.api.trade_hist import filter_trades_by_query, list_trade_history
from pmls.credentials import create_clob_client_from_env
from pmls.trading.cancel import cancel_all_orders, cancel_by_order_ids


def _cmd_get_order(args):
    try:
        cli = create_clob_client_from_env()
        resp = fetch_order_by_id(cli, args.order_id)
    except Exception as e:
        print(e, file=sys.stderr)
        return 1

    print(json.dumps(resp, indent=2))
    return 0


def _cmd_orders(args):
    try:
        cli = create_clob_client_from_env()
        orders = list_orders(cli)
        for o in orders:
            print(f'{o.outcome} {o.side} {o.size}@${o.price}, token ID: {o.token_id}')
    except Exception as e:
        print(e, file=sys.stderr)
        return 1


def _cmd_cancel(args):
    if not args.all and not args.id:
        print("Error: specify --all or --id <order-id,...>", file=sys.stderr)
        return 1

    def _handle_res(resp):
        if resp.not_canceled:
            for oid, reason in (resp.not_canceled or {}).items():
                print(f"Not canceled {oid}: {reason}", file=sys.stderr)
        if resp.canceled:
            print(f"Canceled {len(resp.canceled)} order(s): {', '.join(resp.canceled)}")
        else:
            print("No orders were canceled.")

    try:
        cli = create_clob_client_from_env()
        if args.all:
            resp = cancel_all_orders(cli)
        else:
            ids = [s.strip() for s in args.id.split(',')]
            resp = cancel_by_order_ids(cli, ids)
        _handle_res(resp)
        return 0

    except Exception as e:
        print(e, file=sys.stderr)
        return 1


def _cmd_trade(args):
    try:
        cli = create_clob_client_from_env()
        resp = list_trade_history(
            cli,
            token_id=args.token_id,
            before=args.before,
            after=args.after,
            market=args.market,
        )

        if args.query:
            resp = filter_trades_by_query(resp, args.query)

        for o in resp:
            size = float(o.size or 0)
            price = float(o.price or 0)
            total = size * price
            print(f"{o.outcome} {o.side} {size}@{price}. Total: ${round(total, 3)} ({o.market})")

        return 0

    except Exception as e:
        print(e, file=sys.stderr)
        return 1


def register(subparsers):
    # GET single order by ID
    get_order_parser = subparsers.add_parser(
        "get-order", help="Fetch a single order by its order ID (hash)."
    )
    get_order_parser.add_argument(
        "order_id",
        help="Order ID (order hash) to look up.",
    )
    get_order_parser.set_defaults(handler=_cmd_get_order)

    # GET all orders
    subparsers.add_parser(
        "orders", help="Get all open orders."
    ).set_defaults(handler=_cmd_orders)

    # CANCEL order(s)
    cancel_parser = subparsers.add_parser("cancel", help="Cancel partial or all open orders.")
    cancel_parser.set_defaults(handler=_cmd_cancel)
    cancel_parser.add_argument(
        '-a', '--all', action="store_true", help="Cancel all open orders."
    )
    cancel_parser.add_argument(
        '--id', type=str, help='Comma-separated order IDs to cancel.'
    )

    # TRADE
    trade_parser = subparsers.add_parser("trade")
    trade_parser.add_argument(
        "--token-id",
        type=str,
        default=None,
        dest="token_id",
        help="Filter trades by token id.",
    )
    trade_parser.add_argument(
        "--before",
        type=int,
        default=None,
        help="Filter trades before a unix timestamp.",
    )
    trade_parser.add_argument(
        "--after",
        type=int,
        default=None,
        help="Filter trades after a unix timestamp.",
    )
    trade_parser.add_argument(
        "--market",
        type=str,
        default=None,
        help="Filter trades by market id.",
    )
    trade_parser.add_argument(
        "-q",
        type=str,
        default=None,
        dest="query",
        help="Filter trades by keyword (matched against outcome or market question).",
    )
    trade_parser.set_defaults(handler=_cmd_trade)
