from __future__ import annotations

import os
import sys
import time
from datetime import datetime, timezone

from pmls.api.clob_read import fetch_midpoints, fetch_spread, fetch_tick_size
from pmls.api.last_price import fetch_last_trade_prices
from pmls.api.orderbook import fetch_orderbook_snapshots
from pmls.api.price_history import fetch_price_history
from pmls.api.server_time import fetch_server_time
from pmls.display import _print_outcome_table


def _cmd_orderbook(args):
    token_ids = [t.strip() for t in args.token_ids.split(",") if t.strip()]
    if not token_ids:
        print("Provide at least one token ID.", file=sys.stderr)
        return 1

    depth = args.depth
    if depth < 1 or depth > 10:
        print("--depth must be between 1 and 10", file=sys.stderr)
        return 1

    def clear_terminal():
        os.system("cls" if os.name == "nt" else "clear")

    if args.once:
        try:
            snapshots = fetch_orderbook_snapshots(token_ids, depth)
        except Exception as exc:
            print(f"Orderbook fetch failed: {exc}", file=sys.stderr)
            return 1

        clear_terminal()
        for snapshot in snapshots:
            _print_outcome_table(snapshot)
        print("-" * 28)
    else:
        try:
            while True:
                try:
                    snapshots = fetch_orderbook_snapshots(token_ids, depth)
                except Exception as exc:
                    print(f"Orderbook fetch failed: {exc}", file=sys.stderr)
                    time.sleep(0.5)
                    continue

                clear_terminal()
                for snapshot in snapshots:
                    _print_outcome_table(snapshot)
                print("-" * 28)
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("Stopped orderbook stream.")

    return 0


def _cmd_get_mid(args):
    token_ids = [t.strip() for t in args.token_ids.split(",") if t.strip()]
    if not token_ids:
        print("Provide at least one token ID.", file=sys.stderr)
        return 1

    try:
        resp = fetch_midpoints(token_ids)
    except Exception as exc:
        print(f"Midpoint fetch failed: {exc}", file=sys.stderr)
        return 1

    for tid in token_ids:
        mid = resp.get(tid, "-")
        print(f"{tid}: {mid}")
    return 0


def _cmd_get_spread(args):
    try:
        spread = fetch_spread(args.token_id)
    except Exception as exc:
        print(f"Spread fetch failed: {exc}", file=sys.stderr)
        return 1

    print(spread)
    return 0


def _cmd_get_tick_size(args):
    try:
        tick_size = fetch_tick_size(args.token_id)
    except Exception as exc:
        print(f"Tick size fetch failed: {exc}", file=sys.stderr)
        return 1

    print(tick_size)
    return 0


def _cmd_last_price(args):
    token_ids = [t.strip() for t in args.token_ids.split(",") if t.strip()]
    if not token_ids:
        print("Provide at least one token ID.", file=sys.stderr)
        return 1

    try:
        resp = fetch_last_trade_prices(token_ids)
    except Exception as exc:
        print(f"Last price fetch failed: {exc}", file=sys.stderr)
        return 1

    for entry in resp:
        tid = entry.get("token_id", "-")
        price = entry.get("price", "-")
        side = entry.get("side", "-")
        print(f"{tid}: {price} ({side})")
    return 0


def _cmd_price_history(args):
    token_id = args.token_id

    try:
        history = fetch_price_history(
            token_id,
            interval=args.interval,
            fidelity=args.fidelity,
            start_ts=args.start_ts,
            end_ts=args.end_ts,
        )
    except Exception as exc:
        print(f"Price history fetch failed: {exc}", file=sys.stderr)
        return 1

    if not history:
        print("No price history data.", file=sys.stderr)
        return 1

    lines = ["time,price"]
    for entry in history:
        ts = entry.get("t", 0)
        price = entry.get("p", 0)
        dt = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        lines.append(f"{dt},{price}")

    text = "\n".join(lines) + "\n"

    if args.output:
        with open(args.output, "w") as f:
            f.write(text)
        print(f"Wrote {len(history)} rows to {args.output}")
    else:
        print(text, end="")

    return 0


def _cmd_server_time(args):
    try:
        ts = fetch_server_time()
    except Exception as exc:
        print(f"Server time fetch failed: {exc}", file=sys.stderr)
        return 1

    dt = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    print(f"{ts} ({dt} UTC)")
    return 0


def register(subparsers):
    # ORDERBOOK
    orderbook_parser = subparsers.add_parser(
        "orderbook", help="Stream market orderbook via REST polling, or fetch once with --once."
    )
    orderbook_parser.add_argument(
        "token_ids",
        help="Comma-separated token IDs.",
    )
    orderbook_parser.add_argument(
        "--depth",
        type=int,
        default=3,
        help="Levels per side.",
    )
    orderbook_parser.add_argument(
        "-o", "--once",
        action="store_true",
        default=False,
        help="Fetch once via REST instead of continuous polling.",
    )
    orderbook_parser.set_defaults(handler=_cmd_orderbook)

    # GET-MID
    get_mid_parser = subparsers.add_parser(
        "get-mid", help="Fetch midpoint price for one or more tokens."
    )
    get_mid_parser.add_argument(
        "token_ids",
        help="Comma-separated token IDs.",
    )
    get_mid_parser.set_defaults(handler=_cmd_get_mid)

    # GET-SPREAD
    get_spread_parser = subparsers.add_parser(
        "get-spread", help="Fetch bid-ask spread for a token."
    )
    get_spread_parser.add_argument(
        "token_id",
        help="Token ID.",
    )
    get_spread_parser.set_defaults(handler=_cmd_get_spread)

    # GET-TICK-SIZE
    get_tick_size_parser = subparsers.add_parser(
        "get-tick-size", help="Fetch minimum tick size (price increment) for a token."
    )
    get_tick_size_parser.add_argument(
        "token_id",
        help="Token ID.",
    )
    get_tick_size_parser.set_defaults(handler=_cmd_get_tick_size)

    # LAST-PRICE
    last_price_parser = subparsers.add_parser(
        "last-price", help="Fetch last trade price for one or more tokens."
    )
    last_price_parser.add_argument(
        "token_ids",
        help="Comma-separated token IDs.",
    )
    last_price_parser.set_defaults(handler=_cmd_last_price)

    # PRICE-HISTORY
    price_history_parser = subparsers.add_parser(
        "price-history", help="Fetch historical price data for a token."
    )
    price_history_parser.add_argument(
        "token_id",
        help="Token ID (asset ID) to query.",
    )
    price_history_parser.add_argument(
        "--interval",
        type=str,
        default="1d",
        choices=["max", "all", "1m", "1w", "1d", "6h", "1h"],
        help="Time interval for aggregation (default: 1d).",
    )
    price_history_parser.add_argument(
        "--fidelity",
        type=int,
        default=1,
        help="Data accuracy in minutes (default: 1).",
    )
    price_history_parser.add_argument(
        "--start-ts",
        type=int,
        default=None,
        dest="start_ts",
        help="Filter after this unix timestamp.",
    )
    price_history_parser.add_argument(
        "--end-ts",
        type=int,
        default=None,
        dest="end_ts",
        help="Filter before this unix timestamp.",
    )
    price_history_parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Write CSV output to file instead of stdout.",
    )
    price_history_parser.set_defaults(handler=_cmd_price_history)

    # SERVER-TIME
    subparsers.add_parser(
        "server-time", help="Fetch current CLOB server time."
    ).set_defaults(handler=_cmd_server_time)
