# pmls — Polymarket CLI

A Python CLI for reading and trading on [Polymarket](https://polymarket.com) prediction markets via the CLOB and GAMMA APIs.

---

## Installation

```bash
pip install pmls
```

Requires Python ≥ 3.11.

---

## Environment Variables

Create a `.env` file in the working directory (loaded automatically via `python-dotenv`).

| Variable                   | Required for | Description                                      |
| -------------------------- | ------------ | ------------------------------------------------ |
| `PMLS_CLOB_PRIVATE_KEY`    | Trading      | EOA private key for signing orders               |
| `PMLS_CLOB_API_KEY`        | Trading      | Polymarket CLOB API key                          |
| `PMLS_CLOB_API_SECRET`     | Trading      | Polymarket CLOB API secret                       |
| `PMLS_CLOB_API_PASSPHRASE` | Trading      | Polymarket CLOB API passphrase                   |
| `FUNDER_ADDR`              | Trading      | Funder wallet address (proxy wallet on Polygon)  |
| `POLY_ADDR`                | `pos`, `pnl` | Your Polygon wallet address for position lookups |

Trading commands (`marketo`, `limito`, `orders`, `cancel`) require all five CLOB vars. Read-only commands (`pos`, `pnl`) only require `POLY_ADDR`.

---

## Key Concepts

- **Event slug**: identifier for a top-level event (e.g. `super-bowl-2025`). One event contains multiple markets.
- **Market slug**: identifier for a single binary market (e.g. `chiefs-win-super-bowl-2025`).
- **Token ID**: large integer string identifying one side (outcome) of a binary market. Each binary market has exactly two token IDs (e.g. Yes and No).
- **Outcome**: human-readable label for one side of a market, e.g. `"Yes"` or `"No"` (case-insensitive in CLI).
- **Price convention**: all `--price` arguments are in **cents (0–100)**. The CLOB API uses 0–1 internally; the CLI converts automatically.

---

## Commands

### `get-markets <event-slug>`

Resolve an event slug to its constituent market slugs.

```bash
pmls get-markets <event-slug>
```

**Output** — one market slug per line on stdout:

```
chiefs-win-super-bowl-2025
eagles-win-super-bowl-2025
```

---

### `orderbook <market-slug>`

Fetch and display the L2 orderbook for all outcomes of a market.

```bash
pmls orderbook <market-slug> [--depth N] [--once|-o]
```

| Argument        | Default  | Description                                            |
| --------------- | -------- | ------------------------------------------------------ |
| `market-slug`   | required | Market slug to fetch                                   |
| `--depth N`     | `3`      | Price levels per side (1–10)                           |
| `--once` / `-o` | off      | Fetch once and exit; omit for continuous 0.5 s polling |

**Output format** — repeated per outcome:

```
Outcome: Yes (Token: <token-id>)
Timestamp: 2025-01-01 12:00:00:000000
Asks
| PRICE|       SIZE|
|  63.0|      100.0|
|  62.5|      200.0|

Bids
| PRICE|       SIZE|
|  61.0|      150.0|
|  60.5|       80.0|
```

Asks are sorted ascending (best ask last, i.e. closest to mid at the bottom). Bids are sorted descending (best bid first).

---

### `marketo`

Place a **market order** (Fill-or-Kill) filled immediately at the best available price.

```bash
pmls marketo --bet <amount> --side <BUY|SELL> \
  (--token-id <id> | --slug <slug> --outcome <name>) \
  [--price <cap-cents>]
```

| Argument               | Required           | Description                                                                                                        |
| ---------------------- | ------------------ | ------------------------------------------------------------------------------------------------------------------ |
| `--bet`                | Yes                | USDC to spend (BUY), or number of shares to sell (SELL). Pass `-1` with `--side SELL` to sell the entire position. |
| `--side`               | No (default `BUY`) | `BUY` or `SELL`                                                                                                    |
| `--token-id`           | One group required | Token ID to trade directly                                                                                         |
| `--slug` + `--outcome` | One group required | Market slug and outcome name; resolved to a token ID via GAMMA API                                                 |
| `--price`              | No                 | Max buy price cap in cents (0–100). BUY only; order is rejected if best ask exceeds this.                          |

**Output on success:**

```
Note: Marketable orders in sport market are delayed by 3 seconds.
BUY order <order-id> submitted.
```

**Output on failure:** Polymarket server error message to stderr, exit code 1.

---

### `limito`

Place a **GTC limit order** at an explicit price.

```bash
pmls limito --bet <amount> --price <cents> --side <BUY|SELL> \
  (--token-id <id> | --slug <slug> --outcome <name>)
```

| Argument               | Required           | Description                                                                                                        |
| ---------------------- | ------------------ | ------------------------------------------------------------------------------------------------------------------ |
| `--bet`                | Yes                | USDC to spend (BUY), or number of shares to sell (SELL). Pass `-1` with `--side SELL` to sell the entire position. |
| `--price`              | Yes                | Limit price in cents (0–100)                                                                                       |
| `--side`               | No (default `BUY`) | `BUY` or `SELL`                                                                                                    |
| `--token-id`           | One group required | Token ID to trade directly                                                                                         |
| `--slug` + `--outcome` | One group required | Market slug and outcome name                                                                                       |

**Output on success:**

```
BUY order <order-id> submitted.
```

---

### `orders`

List all open (resting) orders.

```bash
pmls orders
```

**Output format** — one order per line:

```
<outcome> <side> <size>@$<price>, token ID: <token-id>
```

Example:

```
Yes BUY 100@$0.62, token ID: 10667...
```

---

### `cancel`

Cancel open orders.

```bash
pmls cancel --all
pmls cancel --id <order-id>[,<order-id>,...]
```

| Argument       | Description                                 |
| -------------- | ------------------------------------------- |
| `--all` / `-a` | Cancel every open order                     |
| `--id`         | Comma-separated list of order IDs to cancel |

**Output on success:**

```
Canceled 2 order(s): <id1>, <id2>
```

Per-order failures are printed to stderr:

```
Not canceled <id>: <reason>
```

---

### `trade`

List trade history.

```bash
pmls trade [--token-id <id>] [--before <unix-ts>] [--after <unix-ts>] [--market <market-id>] [-q <keyword>]
```

| Argument       | Description                                                                                                                     |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `--token-id`   | Filter to a specific token ID                                                                                                   |
| `--before`     | Unix timestamp upper bound                                                                                                      |
| `--after`      | Unix timestamp lower bound                                                                                                      |
| `--market`     | Filter by market ID                                                                                                             |
| `-q <keyword>` | Keyword filter matched against outcome name or market description (case-insensitive). |

**Output format** — one trade per line:

```
<outcome> <side> <size>@<price>. Total: $<total> (<market-id>)
```

Example:

```
Yes BUY 50.0@0.6. Total: $30.0 (0x1234...)
```

---

### `pos`

Show open positions for a wallet address.

```bash
pmls pos [--user <address>]
```

| Argument | Default      | Description            |
| -------- | ------------ | ---------------------- |
| `--user` | `$POLY_ADDR` | Polygon wallet address |

**Output format** — one position per line:

```
<market-title> <outcome>: size=<shares> avg=<avg-price> curPrice=<current-price> value=<current-value-usd> pnl=<unrealized-pnl-usd> token_id=<token-id>
```

---

### `pnl`

Show P&L summary across all open positions with a totals row.

```bash
pmls pnl [--user <address>]
```

| Argument | Default      | Description            |
| -------- | ------------ | ---------------------- |
| `--user` | `$POLY_ADDR` | Polygon wallet address |

**Output format:**

```
<title> <outcome>: <size> shares @ <avg-price> | cur <cur-price> | cost $<cost> | value $<value> | unPnL +<unrealized> (<pct>%) | realPnL $<realized>
------------------------------------------------------------
TOTAL <N> position(s) | cost $<total-cost> | value $<total-value> | unPnL $<total-unrealized> | realPnL $<total-realized> | net +<net>
```

---

## Exit Codes

| Code | Meaning                   |
| ---- | ------------------------- |
| `0`  | Success                   |
| `1`  | Error (message on stderr) |

