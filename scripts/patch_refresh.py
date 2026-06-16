#!/usr/bin/env python3
"""
Surgical refresh patcher — Step 3 of SKILL.md
Updates trading/comps/marketCloseAsOf/freshnessNote/dates in profile.json.
Also prepends new news items when provided.
"""
import json
import sys
from pathlib import Path

TODAY = "2026-06-16"
DATA_ROOT = Path("data-dumps")


def map_comp(raw_comp, existing_comp=None):
    """Map data.json comp entry to profile brief.comps format."""
    base = {
        "name": raw_comp.get("name", raw_comp.get("ticker", "")),
        "ticker": raw_comp.get("ticker", ""),
        "evRevenue": raw_comp.get("evRevenueLTM", "n/a"),
        "revenueGrowth": raw_comp.get("revenueGrowth", "n/a"),
        "grossMargin": raw_comp.get("grossMargin", "n/a"),
        "source": raw_comp.get("source", "yfinance / Yahoo Finance"),
        "sourceUrl": raw_comp.get("sourceUrl", "https://finance.yahoo.com"),
    }
    # Preserve note and type from existing comp if present
    if existing_comp:
        base["type"] = existing_comp.get("type", "Peer")
        base["note"] = existing_comp.get("note", "")
    else:
        base["type"] = "Peer"
        base["note"] = ""
    return base


def patch(company_id: str, new_news: list = None):
    profile_path = DATA_ROOT / company_id / "profile.json"
    data_path = DATA_ROOT / company_id / "runs" / TODAY / "data.json"

    with open(profile_path) as f:
        profile = json.load(f)
    with open(data_path) as f:
        data = json.loads(f.read())

    # ── Trading data (top-level) ──────────────────────────────────────────────
    profile["trading"] = data["trading"]
    profile["marketCloseAsOf"] = data.get("marketCloseAsOf", TODAY)
    profile["freshnessNote"] = data.get("freshnessNote", "")
    profile["lastRunDate"] = TODAY

    # ── Comps (brief.comps) ───────────────────────────────────────────────────
    existing_comps = {c["ticker"]: c for c in profile.get("brief", {}).get("comps", []) if isinstance(c, dict)}
    new_comps_raw = data.get("comps", [])
    if new_comps_raw:
        updated_comps = []
        for raw in new_comps_raw:
            ticker = raw.get("ticker", "")
            updated_comps.append(map_comp(raw, existing_comps.get(ticker)))
        profile.setdefault("brief", {})["comps"] = updated_comps

    # ── Run date ─────────────────────────────────────────────────────────────
    profile.setdefault("brief", {})["runDate"] = TODAY

    # ── Prepend new news items ────────────────────────────────────────────────
    if new_news:
        existing_news = profile.get("brief", {}).get("recentNews", [])
        # Prepend and keep newest 8
        combined = new_news + existing_news
        profile["brief"]["recentNews"] = combined[:8]

    # ── Write back ────────────────────────────────────────────────────────────
    with open(profile_path, "w") as f:
        json.dump(profile, f, indent=2)
    print(f"✓ {company_id}: patched trading/comps/dates" + (f" + {len(new_news)} new news" if new_news else ""))


# ── Per-company new news (only items dated strictly after last run) ────────────

NEW_NEWS = {
    "BE": [
        {
            "date": "2026-06-10",
            "headline": "Bloom Energy stock drops ~10% after Crusoe halts Wyoming data center site work; Morgan Stanley, RBC say outlook intact",
            "whyItMatters": "Crusoe pausing a Wyoming project surfaces project-timeline risk for Bloom's data-center pipeline; bulls argue the broader 2.8 GW Oracle + Nebius backlog insulates revenue guidance, but bears see it as a sign of near-term execution uncertainty in the hyperscaler build cycle.",
            "source": "CNBC",
            "sourceUrl": "https://www.cnbc.com/quotes/BE"
        }
    ],
    "ANET": [
        {
            "date": "2026-06-12",
            "headline": "Morgan Stanley raises Arista Networks price target to $190 (from $180), reiterates bullish view on AI networking demand",
            "whyItMatters": "Continued sell-side PT creep reflects Street confidence in Arista's AI back-end positioning; the 7060XE7 product announcement (June 9) reinforces a broadening portfolio for 400G/800G hyperscaler switches.",
            "source": "Bloomberg",
            "sourceUrl": "https://www.bloomberg.com/quote/ANET:US"
        },
        {
            "date": "2026-06-09",
            "headline": "Arista Networks launches 7060XE7 Series, targeting high-density AI spine and leaf switching for hyperscaler builds",
            "whyItMatters": "Extends the Arista product line deeper into the 800G AI-networking era; keeps Arista competitive with Cisco and Broadcom-accelerated custom ASICs as hyperscalers scale out AI training clusters.",
            "source": "CNBC",
            "sourceUrl": "https://www.cnbc.com/quotes/ANET"
        }
    ],
    "DDOG": [
        {
            "date": "2026-06-09",
            "headline": "Datadog CEO Olivier Pomel explains new AI capabilities helping labs secure and monitor AI agents — CNBC interview",
            "whyItMatters": "Positions Datadog as the observability layer for the AI-agent wave; the product angle (securing agentic pipelines) addresses a nascent but fast-growing buyer need and expands the TAM beyond traditional infrastructure monitoring.",
            "source": "CNBC",
            "sourceUrl": "https://www.cnbc.com/video/2026/06/09/datadog-ceo-shares-why-new-ai-capabilities-help-securitize-agents.html"
        }
    ],
}


if __name__ == "__main__":
    companies = ["CRM", "BE", "NTSK", "ANET", "CRWD", "DDOG", "IONQ", "TOST"]
    for cid in companies:
        try:
            patch(cid, new_news=NEW_NEWS.get(cid))
        except Exception as e:
            print(f"✗ {cid}: ERROR — {e}")
