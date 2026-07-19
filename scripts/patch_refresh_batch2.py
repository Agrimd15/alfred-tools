#!/usr/bin/env python3
"""
Surgical patch for 2026-07-19 refresh — Batch 2: MANH, NVDA, PAYC, ZM
Updates: marketCloseAsOf, freshnessNote, lastRunDate, trading, brief.comps, brief.recentNews, brief.runDate
Everything else left byte-for-byte intact.
"""
import json, os, sys

TODAY = "2026-07-19"
DATA_ROOT = os.environ.get("ATLAS_DATA_ROOT", os.getcwd())
MAX_NEWS = 8

NEWS = {
    "MANH": [
        {
            "date": "2026-07-12",
            "headline": "Manhattan Associates: Q2 Needs To Justify The Premium",
            "whyItMatters": "A Seeking Alpha analyst rated MANH a Hold heading into Q2 earnings, arguing the ~29-30x FY2026 non-GAAP P/E is difficult to justify absent stronger evidence of consolidated revenue acceleration beyond mid-single-digit growth. The piece crystallizes the central pre-earnings debate: cloud ARR growth is solid at 20%+ and RPO expanding, but the premium multiple leaves little room for disappointment when Q2 results land in late July.",
            "source": "Seeking Alpha",
            "sourceUrl": "https://seekingalpha.com/article/4921407-manhattan-associates-stock-q2-justify-premium"
        }
    ],
    "NVDA": [
        {
            "date": "2026-07-16",
            "headline": "Japan to Buy Nvidia Rubin Chips to Build Sovereign AI for Robots",
            "whyItMatters": "Japan's government-backed Noetra Corp. committed to 27,500 next-gen Rubin chips, backed by ~$2.4B in public funding, to build a foundational robotics AI model — Nvidia's largest single sovereign-AI deal to date. The transaction validates the international-government demand leg of the bull case and adds a durable non-hyperscaler revenue stream, countering concerns that the cycle depends entirely on US cloud capex.",
            "source": "Bloomberg",
            "sourceUrl": "https://www.bloomberg.com/news/articles/2026-07-16/japan-to-buy-nvidia-rubin-chips-to-build-sovereign-ai-for-robots"
        },
        {
            "date": "2026-07-16",
            "headline": "Nvidia unveils Cosmos 3 Edge AI model and expands Japan physical-AI ecosystem",
            "whyItMatters": "Huang unveiled Cosmos 3 Edge — a real-time world model for robots and autonomous systems — during a Tokyo visit where Fujitsu, Hitachi, Kawasaki Heavy Industries, and Fanuc joined a physical-AI coalition. The announcements reinforce Nvidia's push beyond GPU data-center revenue into robotics software, diversifying the growth thesis away from pure US hyperscaler capex cycles.",
            "source": "CNBC",
            "sourceUrl": "https://www.cnbc.com/2026/07/16/nvidia-reveals-new-ai-model-and-expands-japans-physical-ai-ecosystem.html"
        },
        {
            "date": "2026-07-15",
            "headline": "Nvidia's Huang Declares Vera Rubin on Track Despite Delay Talk",
            "whyItMatters": "Jensen Huang personally affirmed in Tokyo that Vera Rubin hardware is in production and on track for 'giant' volumes, directly countering the SemiAnalysis Kyber-delay narrative. Coming alongside Japan's sovereign-AI chip deal, the reassurance helped stabilize the stock and confirmed the delay risk is Kyber-specific rather than a broad Rubin program slip.",
            "source": "Bloomberg",
            "sourceUrl": "https://www.bloomberg.com/news/articles/2026-07-15/nvidia-s-huang-declares-vera-rubin-on-track-despite-delay-talk"
        },
        {
            "date": "2026-07-14",
            "headline": "Small Amount of Nvidia AI Chips Sold to China Via US License",
            "whyItMatters": "A US trade official confirmed only a very small volume of H200 chips had shipped to China under newly issued export licenses — well below market expectations. This signals the near-term China AI-chip revenue opportunity remains severely constrained, a headwind to the bull case that Chinese hyperscalers would quickly ramp Nvidia purchases.",
            "source": "Bloomberg",
            "sourceUrl": "https://www.bloomberg.com/news/articles/2026-07-14/small-amount-of-nvidia-ai-chips-shipped-to-china-with-us-license"
        },
        {
            "date": "2026-07-06",
            "headline": "Nvidia's next-gen AI rack system delayed to 2028 on manufacturing snags, SemiAnalysis says",
            "whyItMatters": "SemiAnalysis reported that Nvidia's Kyber rack-scale architecture slipped more than 12 months to 2028 due to PCB midplane manufacturing difficulties, rattling Asian supply-chain stocks. The report renewed concern that Nvidia's annual-release cadence is straining manufacturing limits and could give AMD and rival architectures a rare opening at the high end.",
            "source": "CNBC",
            "sourceUrl": "https://www.cnbc.com/2026/07/06/nvidia-kyber-rack-system-delays-manufacturing-taiwan-rubin-chips-.html"
        }
    ],
    "PAYC": [],
    "ZM": [
        {
            "date": "2026-07-17",
            "headline": "The Zoom hack that says, 'Don't record me'",
            "whyItMatters": "TechCrunch reported on a growing cultural backlash to AI-powered meeting transcription, with VCs renaming themselves in Zoom to signal non-consent to recording. While not a direct revenue threat, the piece crystallizes a brand/trust risk: if AI note-taking breeds meeting avoidance or workarounds, it could soften Zoom's core platform engagement and complicate the AI upsell story bulls are counting on.",
            "source": "TechCrunch",
            "sourceUrl": "https://techcrunch.com/2026/07/17/the-zoom-hack-that-says-dont-record-me/"
        },
        {
            "date": "2026-07-15",
            "headline": "Zoom 'Infusing AI Into Everything We Do,' CFO Chang says; Evercore cites multiple AI monetization paths",
            "whyItMatters": "CFO Michelle Chang appeared on Bloomberg Brief on July 15 describing AI as central to every product line; following a direct meeting with Chang, Evercore published a bullish note arguing Zoom has multiple AI monetization levers across Meetings, Phone, and Contact Center. An unusual combination of management access and favorable sell-side coverage that could move institutional positioning.",
            "source": "Bloomberg",
            "sourceUrl": "https://www.bloomberg.com/news/videos/2026-07-15/zoom-infusing-ai-into-everything-we-do-says-cfo-chang-video"
        },
        {
            "date": "2026-07-14",
            "headline": "Zoom CEO Eric Yuan goes one-on-one with Jim Cramer",
            "whyItMatters": "Yuan appeared on CNBC's Mad Money to discuss AI integration, the Anthropic stake, and growth opportunities — a high-profile investor-facing signal timed around a broader management media push. Cramer coverage tends to move retail sentiment; the appearance reinforces the AI-reacceleration bull thesis at a moment when Zoom bulls are leaning heavily on the Anthropic IPO narrative.",
            "source": "CNBC",
            "sourceUrl": "https://www.cnbc.com/video/2026/07/14/zoom-ceo-eric-yuan-goes-one-on-one-with-jim-cramer.html"
        }
    ]
}

COMPANIES = ["MANH", "NVDA", "PAYC", "ZM"]

def patch_company(company_id):
    profile_path = os.path.join(DATA_ROOT, "data-dumps", company_id, "profile.json")
    data_path    = os.path.join(DATA_ROOT, "data-dumps", company_id, "runs", TODAY, "data.json")

    if not os.path.exists(profile_path):
        print(f"  ✗ profile.json not found: {profile_path}")
        return False
    if not os.path.exists(data_path):
        print(f"  ✗ data.json not found: {data_path}")
        return False

    with open(profile_path) as f:
        profile = json.load(f)
    with open(data_path) as f:
        data = json.load(f)

    # 1. Top-level freshness fields
    profile["marketCloseAsOf"] = data.get("marketCloseAsOf", TODAY)
    profile["freshnessNote"]   = data.get("freshnessNote",
        f"Multiples and trading data refreshed as of {data.get('marketCloseAsOf', TODAY)} close.")
    profile["lastRunDate"] = TODAY
    if "trading" in data:
        profile["trading"] = data["trading"]

    # 2. Update brief.comps with live multiples
    data_comps_by_ticker = {c["ticker"].upper(): c for c in data.get("comps", []) if "ticker" in c}
    for comp in profile.get("brief", {}).get("comps", []):
        ticker = comp.get("ticker", "").upper()
        if ticker in data_comps_by_ticker:
            dc = data_comps_by_ticker[ticker]
            if dc.get("evRevenueLTM") is not None:
                comp["evRevenue"] = dc["evRevenueLTM"]
            if dc.get("revenueGrowth") is not None:
                comp["revenueGrowth"] = dc["revenueGrowth"]
            if dc.get("grossMargin") is not None:
                comp["grossMargin"] = dc["grossMargin"]

    # 3. Prepend new news, deduplicate, cap at MAX_NEWS
    existing_news    = profile.get("brief", {}).get("recentNews", [])
    existing_hdlines = {item.get("headline", "").lower() for item in existing_news}
    new_items = [
        item for item in NEWS.get(company_id.upper(), [])
        if item.get("headline", "").lower() not in existing_hdlines
    ]
    profile["brief"]["recentNews"] = (new_items + existing_news)[:MAX_NEWS]

    # 4. Update run date
    profile["brief"]["runDate"] = TODAY

    with open(profile_path, "w") as f:
        json.dump(profile, f, indent=2)
    print(f"  ✓ saved {profile_path}")
    return True


def main():
    ok, fail = [], []
    for cid in COMPANIES:
        print(f"\nPatching {cid}...")
        if patch_company(cid):
            ok.append(cid)
        else:
            fail.append(cid)

    print("\n" + "="*50)
    print(f"Patched OK ({len(ok)}): {' '.join(ok)}")
    if fail:
        print(f"FAILED ({len(fail)}): {' '.join(fail)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
