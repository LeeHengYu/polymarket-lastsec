from __future__ import annotations

import sys

from pmls.api.gamma_client import (
    extract_outcome_token_ids,
    fetch_event_markets_with_outcomes,
    fetch_market_by_slug,
)
from pmls.constants import DEFAULT_GAMMA_BASE_URL, DEFAULT_TIMEOUT_SECONDS


def _cmd_get_markets(args):
    slug = args.slug
    try:
        markets_with_outcomes = fetch_event_markets_with_outcomes(
            slug,
            base_url=DEFAULT_GAMMA_BASE_URL,
            timeout_seconds=DEFAULT_TIMEOUT_SECONDS,
        )
    except Exception as exc:
        print(exc, file=sys.stderr)
        return 1

    if not markets_with_outcomes:
        print(f"No markets found for event '{slug}'.", file=sys.stderr)
        return 1

    for market_slug, outcomes_dict in markets_with_outcomes:
        print(market_slug)
        for outcome, token_id in outcomes_dict.items():
            print(f"  {outcome}: {token_id}")
    return 0


def _cmd_get_id(args):
    try:
        market = fetch_market_by_slug(args.slug)
        outcome_tokens = extract_outcome_token_ids(market)
    except Exception as exc:
        print(f"Failed to fetch market: {exc}", file=sys.stderr)
        return 1

    for outcome, token_id in outcome_tokens.items():
        print(f"{outcome}: {token_id}")
    return 0


def register(subparsers):
    get_markets_parser = subparsers.add_parser(
        "get-markets", help="Get all market slugs associated with an event slug."
    )
    get_markets_parser.add_argument("slug", help="Event slug to resolve from GAMMA.")
    get_markets_parser.set_defaults(handler=_cmd_get_markets)

    get_id_parser = subparsers.add_parser(
        "get-id", help="Get token IDs for each outcome in a market."
    )
    get_id_parser.add_argument(
        "slug",
        help="Market slug.",
    )
    get_id_parser.set_defaults(handler=_cmd_get_id)
