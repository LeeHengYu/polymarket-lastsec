from __future__ import annotations

import os
import sys

from pmls.api.positions import list_positions


def _cmd_pnl(args):
    try:
        positions = list_positions(user=args.user)
    except Exception as exc:
        print(exc, file=sys.stderr)
        return 1

    if not positions:
        print("No positions.")
        return 0

    total_cost = total_value = total_unrealized = total_realized = 0.0

    for p in positions:
        cost       = p.initialValue or 0.0
        value      = p.currentValue or 0.0
        unrealized = p.cashPnl or 0.0
        realized   = p.realizedPnl or 0.0
        pct        = p.percentPnl or 0.0

        total_cost       += cost
        total_value      += value
        total_unrealized += unrealized
        total_realized   += realized

        sign = "+" if unrealized >= 0 else ""
        print(
            f"{p.title or '-'} {p.outcome or ''}: "
            f"{p.size or 0} shares @ {p.avgPrice or '-'} | "
            f"cur {p.curPrice or '-'} | "
            f"cost ${cost:.2f} | value ${value:.2f} | "
            f"unPnL {sign}{unrealized:.2f} ({pct:.1f}%) | realPnL ${realized:.2f}"
        )

    print("-" * 60)
    net = total_unrealized + total_realized
    sign = "+" if net >= 0 else ""
    print(
        f"TOTAL {len(positions)} position(s) | "
        f"cost ${total_cost:.2f} | value ${total_value:.2f} | "
        f"unPnL ${total_unrealized:.2f} | realPnL ${total_realized:.2f} | "
        f"net {sign}{net:.2f}"
    )
    return 0


def _cmd_pos(args):
    try:
        positions = list_positions(user=args.user)
    except Exception as exc:
        print(exc, file=sys.stderr)
        return 1

    if not positions:
        print("No positions.")
        return 0

    for p in positions:
        title = p.title or "-"
        size = p.size or "-"
        avg = p.avgPrice or "-"
        cur = p.curPrice or "-"
        value = p.currentValue or "-"
        pnl = p.cashPnl or "-"
        print(
            f"{title} {p.outcome or ''}: size={size} avg={avg} curPrice={cur} "
            f"value={value} pnl={pnl} token_id={p.asset or '-'}"
        )

    return 0


def register(subparsers):
    # POSITIONS
    pos_parser = subparsers.add_parser("pos", help="Get current positions for a user.")
    pos_parser.add_argument(
        "--user",
        type=str,
        default=os.environ.get("POLY_ADDR"),
        help="User address. Defaults to POLY_ADDR env var.",
    )
    pos_parser.set_defaults(handler=_cmd_pos)

    # PNL
    pnl_parser = subparsers.add_parser("pnl", help="Show P&L summary across all open positions.")
    pnl_parser.add_argument(
        "--user",
        type=str,
        default=os.environ.get("POLY_ADDR"),
        help="User address. Defaults to POLY_ADDR env var.",
    )
    pnl_parser.set_defaults(handler=_cmd_pnl)
