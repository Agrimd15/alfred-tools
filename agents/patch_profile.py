#!/usr/bin/env python3
"""
Surgical profile.json patcher for the daily refresh routine.
Usage: python3 agents/patch_profile.py <TICKER> [news_json_path]

Patches:
 - brief.comps: fresh evRevenue, revenueGrowth, grossMargin from data.json
 - top-level marketCloseAsOf, freshnessNote, lastRunDate, brief.runDate
 - brief.recentNews: prepend new items from news_json_path (keeps newest 8)
"""
import json, sys, os
from datetime import date

TICKER = sys.argv[1].upper()
NEWS_FILE = sys.argv[2] if len(sys.argv) > 2 else None
TODAY = date.today().isoformat()

data_dumps = os.path.join(os.environ.get("ATLAS_DATA_ROOT", "."), "data-dumps")
data_path   = os.path.join(data_dumps, TICKER, "runs", TODAY, "data.json")
profile_path = os.path.join(data_dumps, TICKER, "profile.json")

with open(data_path) as f:
    d = json.load(f)
with open(profile_path) as f:
    p = json.load(f)

# --- 1. Update top-level metadata ---
p["marketCloseAsOf"] = d.get("marketCloseAsOf")
p["freshnessNote"]   = d.get("freshnessNote")
p["lastRunDate"]     = TODAY
if "brief" in p:
    p["brief"]["runDate"] = TODAY

# --- 2. Update brief.comps with fresh multiples ---
data_comps_by_ticker = {c["ticker"]: c for c in d.get("comps", [])}
t = d.get("trading", {})  # subject trading data

new_comps = []
for comp in p.get("brief", {}).get("comps", []):
    ticker = comp.get("ticker", "").upper()
    if ticker == TICKER or comp.get("type") == "Subject":
        # Update subject row from trading
        comp["evRevenue"]      = t.get("evRevenueLTM", comp.get("evRevenue"))
        comp["revenueGrowth"]  = t.get("revenueGrowthYoY", comp.get("revenueGrowth"))
        comp["grossMargin"]    = t.get("grossMargin", comp.get("grossMargin"))
        comp["priceAsOf"]      = t.get("priceAsOf", d.get("marketCloseAsOf"))
    elif ticker in data_comps_by_ticker:
        dc = data_comps_by_ticker[ticker]
        comp["evRevenue"]      = dc.get("evRevenueLTM", comp.get("evRevenue"))
        comp["revenueGrowth"]  = dc.get("revenueGrowth", comp.get("revenueGrowth"))
        comp["grossMargin"]    = dc.get("grossMargin", comp.get("grossMargin"))
        comp["priceAsOf"]      = dc.get("priceAsOf", d.get("marketCloseAsOf"))
    new_comps.append(comp)

if new_comps:
    p["brief"]["comps"] = new_comps

# --- 3. Prepend new news items ---
if NEWS_FILE and os.path.exists(NEWS_FILE):
    with open(NEWS_FILE) as f:
        new_news = json.load(f)
    if isinstance(new_news, list) and new_news:
        existing = p["brief"].get("recentNews", [])
        # Deduplicate by headline
        existing_headlines = {n.get("headline", "") for n in existing}
        fresh = [n for n in new_news if n.get("headline", "") not in existing_headlines]
        combined = fresh + existing
        p["brief"]["recentNews"] = combined[:8]  # keep newest 8
        print(f"  Prepended {len(fresh)} new news items")
    else:
        print("  No new news items to add")
else:
    print("  No news file — skipping news update")

# --- 4. Also update revenueHistory LTM point if present ---
ltm_revenue = t.get("totalRevenueLTM")
if ltm_revenue:
    rh = p.get("revenueHistory", p.get("brief", {}).get("revenueHistory", []))
    for point in rh:
        if point.get("year", "").startswith("LTM"):
            point["label"] = ltm_revenue if isinstance(ltm_revenue, str) else f"${ltm_revenue/1e9:.1f}B"
            point["source"] = "yfinance / Yahoo Finance"
            break

# --- 5. Write back ---
with open(profile_path, "w") as f:
    json.dump(p, f, indent=2)
print(f"  Patched {TICKER}: marketCloseAsOf={d.get('marketCloseAsOf')}, comps updated")
