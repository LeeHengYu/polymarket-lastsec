from __future__ import annotations

import json
from typing import Any

import requests

from pmls.constants import DEFAULT_GAMMA_BASE_URL, DEFAULT_TIMEOUT_SECONDS


def fetch_event(
    event_slug: str,
    base_url: str = DEFAULT_GAMMA_BASE_URL,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    url = f"{base_url.rstrip('/')}/events/slug/{event_slug}"
    try:
        response = requests.get(url, timeout=timeout_seconds)
    except requests.RequestException as exc:
        raise RuntimeError("Unable to reach GAMMA API.") from exc

    if response.status_code == 404:
        raise ValueError(f"Event '{event_slug}' was not found.")

    try:
        payload = response.json()
    except ValueError as exc:
        raise RuntimeError("GAMMA API returned invalid JSON.") from exc

    return payload


def extract_market_slugs(event: dict[str, Any]) -> list[str]:
    markets = event.get("markets", [])
    slugs: list[str] = []
    for item in markets:
        slug = item.get("slug")
        if slug:
            slugs.append(slug)
    return slugs


def fetch_event_markets(
    event_slug: str,
    base_url: str = DEFAULT_GAMMA_BASE_URL,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> list[str]:
    event = fetch_event(event_slug, base_url=base_url, timeout_seconds=timeout_seconds)
    return extract_market_slugs(event)


def fetch_market_by_slug(market_slug: str) -> dict[str, Any]:
    url = f"{DEFAULT_GAMMA_BASE_URL.rstrip('/')}/markets"
    try:
        response = requests.get(
            url,
            params={"slug": market_slug, "closed": False},
            timeout=DEFAULT_TIMEOUT_SECONDS,
        )
    except requests.RequestException as exc:
        raise RuntimeError("Unable to reach GAMMA API for market lookup.") from exc

    if not response.ok:
        raise RuntimeError(response.text)

    try:
        payload = response.json()
    except ValueError as exc:
        raise RuntimeError(response.text) from exc

    if not payload:
        raise ValueError(f"Market '{market_slug}' was not found.")
    return payload[0]


def fetch_market_by_token_id(token_id: str) -> dict[str, Any]:
    url = f"{DEFAULT_GAMMA_BASE_URL.rstrip('/')}/markets"
    try:
        response = requests.get(
            url,
            params={"clob_token_ids": token_id},
            timeout=DEFAULT_TIMEOUT_SECONDS,
        )
    except requests.RequestException as exc:
        raise RuntimeError("Unable to reach GAMMA API for market lookup.") from exc

    if not response.ok:
        raise RuntimeError(response.text)

    try:
        payload = response.json()
    except ValueError as exc:
        raise RuntimeError(response.text) from exc

    if not payload:
        raise ValueError(f"No market found for token_id '{token_id}'.")
    return payload[0]


def extract_outcome_token_ids(market: dict[str, Any]) -> dict[str, str]:
    try:
        token_ids = json.loads(market["clobTokenIds"])
        outcomes = json.loads(market["outcomes"])
        pairs = list(zip(outcomes, token_ids))
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError("Invalid market outcome/token payload.") from exc

    if not pairs:
        raise ValueError("Invalid market outcome/token payload.")

    return {str(outcome).lower(): str(token_id) for outcome, token_id in pairs}


def extract_markets_with_outcomes(event: dict[str, Any]) -> list[tuple[str, dict[str, str]]]:
    markets = event.get("markets", [])
    results: list[tuple[str, dict[str, str]]] = []
    for market in markets:
        if not isinstance(market, dict):
            continue
        slug = market.get("slug")
        if not slug:
            continue
        try:
            outcomes = extract_outcome_token_ids(market)
        except ValueError:
            outcomes = {}
        results.append((str(slug), outcomes))
    return results


def fetch_event_markets_with_outcomes(
    event_slug: str,
    base_url: str = DEFAULT_GAMMA_BASE_URL,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> list[tuple[str, dict[str, str]]]:
    event = fetch_event(event_slug, base_url=base_url, timeout_seconds=timeout_seconds)
    return extract_markets_with_outcomes(event)
