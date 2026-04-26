#!/usr/bin/env python3
"""Fetch macro context: Treasury yields, VIX, DXY, NZD/USD."""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import requests
import yfinance as yf

VAULT_ROOT = Path(__file__).resolve().parent.parent
MACRO_PATH = VAULT_ROOT / "ops" / "macro.md"

FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"
FRED_API_KEY = os.environ.get("FRED_API_KEY", "")

FRED_SERIES = {
    "DGS10": "10-Year Treasury Yield",
    "DGS2": "2-Year Treasury Yield",
    "VIXCLS": "VIX",
    "DTWEXBGS": "DXY (Trade-Weighted USD)",
}


def fetch_fred_series(series_id):
    """Fetch latest value from FRED. Works without API key on free tier."""
    params = {
        "series_id": series_id,
        "sort_order": "desc",
        "limit": 10,
        "file_type": "json",
    }
    if FRED_API_KEY:
        params["api_key"] = FRED_API_KEY
    else:
        params["api_key"] = "DEMO_KEY"

    try:
        resp = requests.get(FRED_BASE, params=params, timeout=15)
        if resp.status_code != 200:
            return None, None

        observations = resp.json().get("observations", [])
        values = []
        for obs in observations:
            if obs["value"] != ".":
                values.append(float(obs["value"]))
                if len(values) == 2:
                    break

        if not values:
            return None, None

        current = values[0]
        prev = values[1] if len(values) > 1 else None
        return current, prev

    except Exception:
        return None, None


def fetch_nzdusd():
    """Fetch NZD/USD current rate and 5-year stats."""
    try:
        fx = yf.Ticker("NZDUSD=X")
        hist = fx.history(period="5y")
        if hist.empty:
            return None, None, None

        current = hist["Close"].iloc[-1]
        mean_5y = hist["Close"].mean()
        deviation = (current - mean_5y) / mean_5y * 100

        week_ago = hist["Close"].iloc[-5] if len(hist) >= 5 else hist["Close"].iloc[0]
        week_change = (current - week_ago) / week_ago * 100

        return {
            "current": round(current, 4),
            "mean_5y": round(mean_5y, 4),
            "deviation_pct": round(deviation, 1),
            "week_change": round(week_change, 2),
        }, None, None
    except Exception as e:
        return None, None, str(e)


def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = [
        "# Macro Snapshot",
        "",
        f"Generated: {now}",
        "",
        "## Rates & Volatility",
        "| Indicator | Current | Previous | Change |",
        "|---|---|---|---|",
    ]

    for series_id, name in FRED_SERIES.items():
        current, prev = fetch_fred_series(series_id)
        if current is None:
            lines.append(f"| {name} | DATA UNAVAILABLE | - | - |")
        elif prev is None:
            lines.append(f"| {name} | {current:.2f} | - | - |")
        else:
            change = current - prev
            lines.append(f"| {name} | {current:.2f} | {prev:.2f} | {change:+.2f} |")

    spread_10y, _ = fetch_fred_series("DGS10")
    spread_2y, _ = fetch_fred_series("DGS2")
    if spread_10y and spread_2y:
        spread = spread_10y - spread_2y
        lines.append(f"| 10Y-2Y Spread | {spread:.2f}bp | - | - |")

    lines += ["", "## FX Context"]

    fx_data, _, fx_error = fetch_nzdusd()
    if fx_data:
        lines += [
            f"- NZD/USD: {fx_data['current']} (1-week: {fx_data['week_change']:+.2f}%)",
            f"- 5-year mean: {fx_data['mean_5y']}",
            f"- Deviation from mean: {fx_data['deviation_pct']:+.1f}%",
        ]
        if fx_data["deviation_pct"] < -10:
            lines.append("- ⚠️ **Expensive USD entry** — NZD >10% below 5-year mean")
        elif fx_data["deviation_pct"] > 10:
            lines.append("- ✅ **Cheap USD entry** — NZD >10% above 5-year mean")
        else:
            lines.append("- FX within normal range")
    else:
        lines.append("- NZD/USD: DATA UNAVAILABLE")
        if fx_error:
            lines.append(f"- Error: {fx_error}")

    lines.append("")
    MACRO_PATH.write_text("\n".join(lines))
    print(f"Written: {MACRO_PATH}")


if __name__ == "__main__":
    main()
