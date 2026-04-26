#!/usr/bin/env python3
"""Fetch current prices and compute portfolio overview from Holdings.md."""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import yfinance as yf

VAULT_ROOT = Path(__file__).resolve().parent.parent
HOLDINGS_PATH = VAULT_ROOT / "Investing Knowledge Base" / "07-Portfolio" / "Holdings.md"
PRICES_PATH = VAULT_ROOT / "ops" / "prices.md"
OVERVIEW_PATH = VAULT_ROOT / "ops" / "portfolio-overview.md"


def parse_holdings(path):
    """Parse Holdings.md for ticker, entry price, shares, entry date.

    Expected table format:
    | Ticker | Entry Price (USD) | Shares | Entry Date | Bucket |
    """
    if not path.exists():
        return []

    holdings = []
    in_table = False
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("| Ticker"):
                in_table = True
                continue
            if in_table and line.startswith("|---"):
                continue
            if in_table and line.startswith("|"):
                cols = [c.strip() for c in line.split("|")[1:-1]]
                if len(cols) >= 4:
                    try:
                        holdings.append({
                            "ticker": cols[0],
                            "entry_price": float(cols[1].replace("$", "").replace(",", "")),
                            "shares": float(cols[2]),
                            "entry_date": cols[3],
                            "bucket": cols[4] if len(cols) > 4 else "unknown",
                        })
                    except (ValueError, IndexError):
                        continue
            elif in_table and not line.startswith("|"):
                in_table = False

    return holdings


def fetch_price_data(tickers):
    """Fetch current and historical prices for a list of tickers."""
    if not tickers:
        return {}

    data = {}
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1y")
            if hist.empty:
                data[ticker] = None
                continue

            current = hist["Close"].iloc[-1]
            week_ago = hist["Close"].iloc[-5] if len(hist) >= 5 else hist["Close"].iloc[0]
            month_ago = hist["Close"].iloc[-21] if len(hist) >= 21 else hist["Close"].iloc[0]
            ytd_start = hist[hist.index >= f"{datetime.now().year}-01-01"]
            ytd_price = ytd_start["Close"].iloc[0] if not ytd_start.empty else hist["Close"].iloc[0]

            data[ticker] = {
                "current": round(current, 2),
                "week_return": round((current - week_ago) / week_ago * 100, 2),
                "month_return": round((current - month_ago) / month_ago * 100, 2),
                "ytd_return": round((current - ytd_price) / ytd_price * 100, 2),
            }
        except Exception:
            data[ticker] = None

    return data


def fetch_nzdusd_history():
    """Fetch NZD/USD for cost basis conversion."""
    try:
        fx = yf.Ticker("NZDUSD=X")
        hist = fx.history(period="5y")
        if hist.empty:
            return None, None
        current = hist["Close"].iloc[-1]
        return current, hist
    except Exception:
        return None, None


def write_prices(holdings, price_data, path):
    """Write ops/prices.md with raw price data."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = [
        "# Price Snapshot",
        f"",
        f"Generated: {now}",
        "",
        "| Ticker | Current (USD) | 5-Day % | 1-Month % | YTD % |",
        "|---|---|---|---|---|",
    ]

    for h in holdings:
        t = h["ticker"]
        d = price_data.get(t)
        if d is None:
            lines.append(f"| {t} | DATA UNAVAILABLE | - | - | - |")
        else:
            lines.append(f"| {t} | ${d['current']:.2f} | {d['week_return']:+.2f}% | {d['month_return']:+.2f}% | {d['ytd_return']:+.2f}% |")

    lines.append("")
    path.write_text("\n".join(lines))


def write_overview(holdings, price_data, nzd_rate, path):
    """Write ops/portfolio-overview.md with formatted P&L."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    total_cost_usd = 0
    total_value_usd = 0
    position_lines = []

    for h in holdings:
        t = h["ticker"]
        d = price_data.get(t)
        cost = h["entry_price"] * h["shares"]
        total_cost_usd += cost

        if d is None:
            position_lines.append(f"| {t} | ${h['entry_price']:.2f} | ${cost:.2f} | DATA UNAVAILABLE | - | - | {h['bucket']} |")
        else:
            value = d["current"] * h["shares"]
            total_value_usd += value
            pnl = value - cost
            pnl_pct = (pnl / cost * 100) if cost > 0 else 0
            days_held = (datetime.now() - datetime.strptime(h["entry_date"], "%Y-%m-%d")).days if h["entry_date"] else 0
            position_lines.append(f"| {t} | ${d['current']:.2f} | ${value:.2f} | ${pnl:+.2f} | {pnl_pct:+.1f}% | {days_held}d | {h['bucket']} |")

    total_return_pct = ((total_value_usd - total_cost_usd) / total_cost_usd * 100) if total_cost_usd > 0 else 0
    nzd_cost = total_cost_usd / nzd_rate if nzd_rate else None

    lines = [
        "# Portfolio Overview",
        "",
        f"Generated: {now}",
        "",
        "## Summary",
        f"- Total cost basis (USD): ${total_cost_usd:,.2f}",
        f"- Total current value (USD): ${total_value_usd:,.2f}",
        f"- Total return: {total_return_pct:+.1f}%",
    ]

    if nzd_cost:
        lines.append(f"- NZD cost basis (approx): NZD ${nzd_cost:,.2f}")
        if nzd_cost >= 50000:
            lines.append("- ⚠️ **FIF THRESHOLD EXCEEDED** — strategy review required")
        elif nzd_cost >= 40000:
            lines.append("- ⚠️ FIF threshold approaching (NZD $40k+)")

    lines += [
        "",
        "## Positions",
        "| Ticker | Current | Value | P&L | Return | Held | Bucket |",
        "|---|---|---|---|---|---|---|",
    ]
    lines.extend(position_lines)
    lines.append("")

    path.write_text("\n".join(lines))


def main():
    holdings = parse_holdings(HOLDINGS_PATH)

    if not holdings:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        PRICES_PATH.write_text(f"# Price Snapshot\n\nGenerated: {now}\n\nNo holdings found in Holdings.md. Add positions to generate price data.\n")
        OVERVIEW_PATH.write_text(f"# Portfolio Overview\n\nGenerated: {now}\n\nNo holdings found in Holdings.md. Add positions to generate portfolio overview.\n")
        print("No holdings found. Empty output files generated.")
        return

    tickers = [h["ticker"] for h in holdings]
    print(f"Fetching prices for: {', '.join(tickers)}")

    try:
        price_data = fetch_price_data(tickers)
    except Exception as e:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        PRICES_PATH.write_text(f"# Price Snapshot\n\nGenerated: {now}\n\n## DATA UNAVAILABLE\n\nyfinance fetch failed: {e}\n")
        OVERVIEW_PATH.write_text(f"# Portfolio Overview\n\nGenerated: {now}\n\n## DATA UNAVAILABLE\n\nyfinance fetch failed: {e}\n")
        print(f"Error fetching prices: {e}", file=sys.stderr)
        return

    nzd_rate, _ = fetch_nzdusd_history()

    write_prices(holdings, price_data, PRICES_PATH)
    write_overview(holdings, price_data, nzd_rate, OVERVIEW_PATH)
    print(f"Written: {PRICES_PATH}")
    print(f"Written: {OVERVIEW_PATH}")


if __name__ == "__main__":
    main()
