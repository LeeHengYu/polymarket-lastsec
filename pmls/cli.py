from __future__ import annotations

import argparse
import sys

from pmls.commands import data, execution, market, orders, portfolio

_COMMAND_MODULES = [market, data, execution, orders, portfolio]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pmls",
        description="Polymarket market helper CLI.",
    )
    subparsers = parser.add_subparsers(dest="command")
    for module in _COMMAND_MODULES:
        module.register(subparsers)
    return parser


def main() -> int:
    parser = build_parser()
    argv = sys.argv[1:]

    if not argv:
        parser.print_help()
        return 0

    args = parser.parse_args(argv)
    handler = args.handler
    if handler is None:
        parser.print_help()
        return 0

    return handler(args)

if __name__ == "__main__":
    raise SystemExit(main())
