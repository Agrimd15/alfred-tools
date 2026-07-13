#!/usr/bin/env python3
"""
Surgical refresh patcher — Step 3 of SKILL.md
Updates trading/comps/marketCloseAsOf/freshnessNote/dates in profile.json.
Also prepends new news items when provided.
Preserves all existing brief structure; only updates stale numbers and adds news.
"""
import json
import sys
from pathlib import Path

TODAY = "2026-07-13"
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


def patch(company_id: str, new_news: list = None, new_earnings: dict = None,
          structural_updates: dict = None):
    profile_path = DATA_ROOT / company_id / "profile.json"
    data_path = DATA_ROOT / company_id / "runs" / TODAY / "data.json"

    with open(profile_path) as f:
        profile = json.load(f)
    with open(data_path) as f:
        data = json.loads(f.read())

    trading = data.get("trading", {})

    # ── Trading data (top-level) ──────────────────────────────────────────────
    profile["trading"] = trading
    profile["marketCloseAsOf"] = data.get("marketCloseAsOf", TODAY)
    profile["freshnessNote"] = data.get("freshnessNote", "")
    profile["lastRunDate"] = TODAY
    # Also update top-level comps array (raw peer data)
    profile["comps"] = data.get("comps", [])

    # ── Run date ─────────────────────────────────────────────────────────────
    profile.setdefault("brief", {})["runDate"] = TODAY

    # ── Comps (brief.comps) — surgical: preserve notes, update numbers ────────
    # Build lookup from today's data.json peer comps
    data_comps_by_ticker = {c["ticker"]: c for c in data.get("comps", [])}
    existing_brief_comps = profile.get("brief", {}).get("comps", [])
    updated_brief_comps = []
    for c in existing_brief_comps:
        if not isinstance(c, dict):
            continue
        ticker = c.get("ticker", "")
        comp_type = c.get("type", "Peer")
        if comp_type == "Subject" or ticker == company_id:
            # Update from trading data (subject)
            c["evRevenue"] = trading.get("evRevenueLTM", c.get("evRevenue", "?"))
            c["revenueGrowth"] = trading.get("revenueGrowthYoY", c.get("revenueGrowth", "?"))
            c["grossMargin"] = trading.get("grossMargin", c.get("grossMargin", "?"))
        elif ticker in data_comps_by_ticker:
            live = data_comps_by_ticker[ticker]
            c["evRevenue"] = live.get("evRevenueLTM", c.get("evRevenue", "?"))
            c["revenueGrowth"] = live.get("revenueGrowth", c.get("revenueGrowth", "?"))
            c["grossMargin"] = live.get("grossMargin", c.get("grossMargin", "?"))
        updated_brief_comps.append(c)
    if updated_brief_comps:
        profile["brief"]["comps"] = updated_brief_comps

    # ── Prepend new news items ────────────────────────────────────────────────
    if new_news:
        existing_news = profile.get("brief", {}).get("recentNews", [])
        seen = set()
        combined = []
        for item in new_news + existing_news:
            key = item.get("headline", "")[:60]
            if key not in seen:
                seen.add(key)
                combined.append(item)
        profile["brief"]["recentNews"] = combined[:8]

    # ── Replace earnings takeaways if new quarter data ────────────────────────
    if new_earnings:
        profile["brief"]["earningsTakeaways"] = new_earnings

    # ── Structural updates (businessOverview, productModel, etc.) ────────────
    if structural_updates:
        for field, value in structural_updates.items():
            if field.startswith("brief."):
                subfield = field[len("brief."):]
                profile.setdefault("brief", {})[subfield] = value
            else:
                profile[field] = value

    # ── Write back ────────────────────────────────────────────────────────────
    with open(profile_path, "w") as f:
        json.dump(profile, f, indent=2)
    actions = ["trading/comps/dates"]
    if new_news:
        actions.append(f"+{len(new_news)} news")
    if new_earnings:
        actions.append("earnings updated")
    if structural_updates:
        actions.append(f"structural ({', '.join(structural_updates.keys())})")
    print(f"✓ {company_id}: patched " + ", ".join(actions))


# ── Per-company new news (only items dated strictly after last run) ────────────
# Last run dates: MPWR/TER/TENB/SNAP/PCOR = 2026-06-27
#                 FIG/INTC/ADI/EGAN/MDB = 2026-06-28

NEW_NEWS = {
    "FIG": [
        {
            "date": "2026-07-07",
            "headline": "Figma acquires team behind a vibe-coding app (Bud), expanding platform from design into agentic coding and prototyping",
            "whyItMatters": "Acquiring the Bud (Y Combinator-backed AI app/agent builder) team extends Figma's platform from collaborative design into agentic coding and rapid prototyping — reinforcing the AI-as-growth-catalyst thesis and reducing the perceived threat from AI coding tools by bringing them in-house.",
            "source": "TechCrunch",
            "sourceUrl": "https://techcrunch.com/2026/07/07/figma-acquires-team-behind-a-vibe-coding-app/"
        },
        {
            "date": "2026-07-07",
            "headline": "BofA resumes Figma coverage at Buy with $30 price target, citing AI as structural growth catalyst for design-to-dev platform",
            "whyItMatters": "BofA (analyst Tal Liani) resumed coverage at Buy at 8× CY27 EV/Sales, arguing AI is a tailwind rather than a headwind for Figma's platform; shares rose ~6% on the reinstatement, signaling institutional re-rating momentum ahead of Figma's post-IPO growth phase.",
            "source": "Seeking Alpha",
            "sourceUrl": "https://seekingalpha.com/news/4611931-figma-in-focus-as-bofa-puts-buy-rating-on-stock"
        },
    ],
    "TER": [
        {
            "date": "2026-07-06",
            "headline": "Goldman Sachs reaffirms Buy on Teradyne, raises price target to $465 from $350 on AI/datacenter test cycle tailwinds",
            "whyItMatters": "Goldman's 33% PT raise to $465 drove TER up >8% intraday; the note highlights that AI/datacenter test demand is accelerating beyond initial 2026 estimates, reinforcing the bull case for secular ATE spending through HBM and next-gen AI chip cycles.",
            "source": "Seeking Alpha",
            "sourceUrl": "https://seekingalpha.com/symbol/TER/analysis"
        },
        {
            "date": "2026-06-30",
            "headline": "Teradyne hits all-time stock price high as Micron's record Q3 FY2026 results validate AI/HBM test demand",
            "whyItMatters": "TER touched an intraday ATH of ~$488 after Micron reported blowout Q3 FY2026 results — confirming the sustained HBM memory test demand that underpins Teradyne's semiconductor test franchise and growth outlook through 2027.",
            "source": "Investing.com",
            "sourceUrl": "https://www.investing.com/news/company-news/teradyne-ter-hits-all-time-high-as-major-customer-reports-stellar-earnings-4773764"
        },
        {
            "date": "2026-07-01",
            "headline": "Teradyne director Mercedes Johnson sells 167 shares (~$77K) under pre-arranged Rule 10b5-1 plan",
            "whyItMatters": "Routine Form 4 disclosure of a pre-arranged insider sale near ATH levels; no strategic significance — the plan was filed well before this window. Noted for transparency given the stock's >3× YTD move at that point.",
            "source": "Investing.com",
            "sourceUrl": "https://www.investing.com/news/insider-trading-news/teradyne-director-mercedes-johnson-sells-76820-in-stock-93CH-4773764"
        },
    ],
    "INTC": [
        {
            "date": "2026-07-08",
            "headline": "Intel Stock: AI Efficiency Improvements Could Counter Semiconductor Demand — bear-case risk ahead of July 23 earnings",
            "whyItMatters": "Analysis arguing that AI model-efficiency gains (compression, quantization, inference optimization) could reduce the volume of compute needed per AI task — a structural risk to Intel's pricing/volume assumptions even as near-term CPU supply tightens. Sets up a key debate for the July 23 earnings call.",
            "source": "Seeking Alpha",
            "sourceUrl": "https://seekingalpha.com/article/4919808-intel-ai-efficiency-could-counter-semiconductor-demand"
        },
        {
            "date": "2026-07-06",
            "headline": "Intel confirms price hikes on select Xeon 6 server CPUs and Core Ultra laptop chips, citing AI data-center supply tightness",
            "whyItMatters": "Intel raised list prices on flagship Xeon 6 Granite Rapids (Xeon 6980P +$1,495 to $13,955) and Core Ultra SKUs, citing AI data-center demand outstripping fab capacity — confirming the HSBC supply-tightening thesis and providing direct pricing-power evidence ahead of Q2 earnings.",
            "source": "Tom's Hardware",
            "sourceUrl": "https://www.tomshardware.com/pc-components/cpus/intel-confirms-price-hikes-on-select-consumer-and-server-cpus-citing-supply-costs-and-demand-select-xeon-processors-now-over-usd1-000-more-expensive"
        },
        {
            "date": "2026-07-02",
            "headline": "HSBC doubles Intel price target to $200, maintains Buy; initiates sum-of-parts foundry valuation, raises server CPU growth forecast to +25% YoY",
            "whyItMatters": "HSBC's largest-on-street PT ($200, highest at the time) marks a significant re-rating event — new sum-of-parts methodology assigns standalone foundry value for the first time. The +25% YoY server shipment forecast implies Q2 and FY2026 estimates may still be too conservative.",
            "source": "Seeking Alpha",
            "sourceUrl": "https://seekingalpha.com/news/4609693-intel-in-spotlight-as-hsbc-ups-price-target-sees-more-value-from-servers-foundry"
        },
    ],
    "TENB": [
        {
            "date": "2026-07-07",
            "headline": "Tenable Holdings stock hits 52-week high of $42.44, up ~75% YTD on FedRAMP win + JPMorgan Focus List + OpenAI partnership",
            "whyItMatters": "Three catalysts in two weeks (FedRAMP High June 29, JPMorgan Focus List June 30, 52-week high July 7) confirm a structural re-rating, not a momentum trade; the cybersecurity budget tailwind from AI-driven attack surfaces is translating into tangible contract expansion for Tenable's exposure-management platform.",
            "source": "Investing.com",
            "sourceUrl": "https://www.investing.com/news/company-news/tenable-holdings-inc-stock-hits-52week-high-at-4244-usd-93CH-4779776"
        },
        {
            "date": "2026-06-30",
            "headline": "JPMorgan raises Tenable price target to $40 (Overweight), adds to Analyst Focus List on Hexa AI momentum and FedRAMP federal TAM expansion",
            "whyItMatters": "Focus List addition by JPMorgan drives incremental institutional visibility and forced-buy flows; $40 PT reflects confidence in Tenable One's federal market expansion following the June 29 FedRAMP High authorization — a material step-change in addressable opportunity for DoD and intelligence agency contracts.",
            "source": "Investing.com",
            "sourceUrl": "https://www.investing.com/news/analyst-ratings/jpmorgan-raises-tenable-stock-price-target-on-ai-product-momentum-93CH-4766997"
        },
        {
            "date": "2026-06-29",
            "headline": "Tenable achieves FedRAMP High and Impact Level 5 Authorization for Tenable One Cloud Exposure platform",
            "whyItMatters": "FedRAMP High + IL5 (the most stringent US government cloud certifications) opens DoD and intelligence agency contracts — a step-change in federal market TAM for exposure management. TENB shares rallied ~23% on the announcement, one of the largest single-day moves in the company's history.",
            "source": "GlobeNewswire",
            "sourceUrl": "https://www.globenewswire.com/news-release/2026/06/29/3318993/0/en/tenable-achieves-fedramp-high-and-impact-level-5-authorization.html"
        },
    ],
    "SNAP": [
        {
            "date": "2026-07-08",
            "headline": "Goldman Sachs raises Snap price target to $6 (from $5), maintains Neutral; cites Specs AR monetization potential as upside optionality",
            "whyItMatters": "Goldman's modest PT raise acknowledges AR hardware optionality from the new consumer Specs glasses but stops short of Buy — a reflection of Street skepticism on whether AR can materially re-rate Snap before Direct Response ad revenue re-acceleration is proven at scale.",
            "source": "Seeking Alpha",
            "sourceUrl": "https://seekingalpha.com/symbol/SNAP/analysis"
        },
        {
            "date": "2026-07-07",
            "headline": "Wells Fargo raises Snap to $5; DA Davidson initiates at Buy with $7 target — diverging targets reflect AR bull/bear debate",
            "whyItMatters": "The $5 vs. $7 spread frames the key debate: WF focuses on near-term DAU/ARPU headwinds, while DA Davidson sees Specs AR as a structural platform differentiator. Q2 earnings (expected early August) are the next catalyst to resolve this divergence.",
            "source": "Seeking Alpha",
            "sourceUrl": "https://seekingalpha.com/symbol/SNAP/analysis"
        },
    ],
    "ADI": [
        {
            "date": "2026-07-07",
            "headline": "Analog Devices completes $1.5B acquisition of Empower Semiconductor, extending AI power portfolio from grid to silicon core",
            "whyItMatters": "Empower's integrated voltage regulators (IVR) and silicon capacitors for AI processors address the rack-level power-density bottleneck — the fastest-growing and least-solved problem at hyperscaler AI data centers. Completion gives ADI a credible 'grid-to-core' AI signal chain.",
            "source": "PR Newswire",
            "sourceUrl": "https://www.prnewswire.com/news-releases/analog-devices-completes-acquisition-of-empower-semiconductor-302819437.html"
        },
        {
            "date": "2026-07-07",
            "headline": "ADI Form 8-K: completion of Empower Semiconductor acquisition for $1.5B all-cash; Empower CEO to lead IVR initiatives inside ADI",
            "whyItMatters": "Primary SEC filing confirming $1.5B all-cash close with no remaining regulatory conditions; Empower CEO Tim Phillips continuing as internal lead signals commitment to integration velocity rather than acqui-hire absorption.",
            "source": "SEC EDGAR",
            "sourceUrl": "https://www.sec.gov/Archives/edgar/data/0000006281/000119312526294488/d112344d8k.htm"
        },
        {
            "date": "2026-06-29",
            "headline": "Cantor Fitzgerald raises ADI price target to $550 from $510, keeps Overweight; Stifel and Wells Fargo also raise ahead of Empower deal close",
            "whyItMatters": "Broad Street PT cluster ($498–$550) ahead of the Empower close indicates consensus confidence in ADI's AI power-delivery TAM expansion thesis; deal timing (industrial/auto cycle recovery + AI data center ATE growth) makes the acquisition strategically compelling at the deal size.",
            "source": "MarketBeat",
            "sourceUrl": "https://www.marketbeat.com/stocks/NASDAQ/ADI/forecast/"
        },
    ],
    "EGAN": [
        {
            "date": "2026-07-08",
            "headline": "eGain launches AI Agent for Zoom Contact Center, enabling agentic customer service automation directly inside the Zoom ecosystem",
            "whyItMatters": "The Zoom integration expands eGain's distribution to Zoom's 90,000+ contact-center seats without requiring a separate deployment, lowering the buyer's barrier; agentic automation inside the UC layer is the growth thesis for eGain's Conversation Hub.",
            "source": "Investing.com",
            "sourceUrl": "https://www.investing.com/news/press-releases/egain-ai-agent-zoom-contact-center"
        },
        {
            "date": "2026-07-03",
            "headline": "B. Riley initiates eGain with Neutral rating; acknowledges AI differentiation but flags limited revenue scale and CCaaS competition",
            "whyItMatters": "Neutral initiation from a specialty tech bank signals limited near-term upside catalyst; bears point to eGain's $90M revenue scale as a headwind against larger CCaaS incumbents (NICE, FIVN) deploying similar agentic AI tooling.",
            "source": "Investing.com",
            "sourceUrl": "https://www.investing.com/news/analyst-ratings/b-riley-neutral-egain"
        },
    ],
    "PCOR": [
        {
            "date": "2026-07-09",
            "headline": "Procore announces Q2 2026 earnings call scheduled for July 29-30, 2026; street models revenue of ~$379M (+9% YoY)",
            "whyItMatters": "Earnings call timing confirmation sets up a key de-risking event for Procore's construction AI narrative; consensus looks for stabilization around 9-10% growth with margin expansion as the operating leverage story matures.",
            "source": "BusinessWire",
            "sourceUrl": "https://ir.procore.com/news-releases/2026/07/09/procore-q2-earnings-date"
        },
        {
            "date": "2026-07-02",
            "headline": "Procore board member Erin Chapple departs; company discloses director resignation in Form 8-K",
            "whyItMatters": "Director departures at this level are generally administrative; no strategic significance indicated. Chapple had served since 2022. Procore's board composition remains strong with deep construction and SaaS expertise.",
            "source": "SEC EDGAR",
            "sourceUrl": "https://www.sec.gov/Archives/edgar/data/1611052/000119312526294952/d165711d8k.htm"
        },
    ],
    "MDB": [
        {
            "date": "2026-07-10",
            "headline": "Needham raises MongoDB price target to $430 (from $410), reiterates Buy; cites Atlas AI momentum and developer-platform TAM expansion",
            "whyItMatters": "PT raise ahead of Q2 FY2027 earnings (expected August/September) reflects confidence in MongoDB Atlas's ability to capture AI/ML workloads where document-native + vector-search architecture has a structural advantage over relational incumbents.",
            "source": "Seeking Alpha",
            "sourceUrl": "https://seekingalpha.com/news/mongodb-needham-pt-430"
        },
        {
            "date": "2026-07-06",
            "headline": "MongoDB shareholders approve elimination of supermajority voting provisions, enhancing shareholder rights governance",
            "whyItMatters": "Removal of the 66.7% supermajority vote requirement for certain bylaw amendments signals stronger alignment with institutional shareholders — a governance improvement flagged by activist-leaning funds and a positive for ESG-focused holders.",
            "source": "SEC EDGAR",
            "sourceUrl": "https://www.sec.gov/Archives/edgar/data/1441816/000162828026047228/mdb-20260630.htm"
        },
    ],
}

# ── ADI structural updates: Empower Semiconductor acquisition now closed ──────

_ADI_BO = (
    "Analog Devices (NASDAQ: ADI) is the world's #2 high-performance analog and mixed-signal "
    "semiconductor company, behind Texas Instruments. Its chips sit at the boundary between the "
    "physical and digital worlds — sensing, measuring, converting and managing real-world signals "
    "(temperature, motion, sound, power, RF) into data that digital systems can use. ADI sells tens "
    "of thousands of data converters, amplifiers, power-management ICs, RF/microwave parts, MEMS and "
    "sensors into four diversified end markets: Industrial (~47% of revenue and the largest), "
    "Automotive (~25%), Communications (~15%) and Consumer (~13%). Long product life cycles, deep "
    "customer entrenchment and a catalog spanning 100,000+ customers give ADI durable, high-margin, "
    "high-free-cash-flow economics — gross margin runs around 64% and non-GAAP operating margin "
    "reached 49% in Q2 FY2026. The company was scaled into its current form by the $14.8B "
    "acquisition of Linear Technology (2017), the $21B acquisition of Maxim Integrated (2021), and "
    "the $1.5B all-cash acquisition of Empower Semiconductor (closed July 2026), which extends "
    "ADI's power management franchise into AI rack power-delivery — completing a 'grid-to-core' "
    "AI signal-chain portfolio. ADI is led by long-tenured Chair & CEO Vincent Roche, who frames "
    "strategy around the AI-driven 'intelligent edge.'"
)

_ADI_PM = (
    "ADI monetizes a vast portfolio of high-performance analog/mixed-signal components, where it is "
    "the market leader in data converters. The business is differentiated by precision, performance "
    "and reliability rather than raw digital scaling, which yields pricing power, ~64% gross margins "
    "and very long design-win lifetimes (parts can ship for a decade or more). Revenue is diversified: "
    "Industrial (~47%, recovering ~38% YoY in Q1 FY2026 on automation, test/instrumentation, "
    "aerospace & defense, healthcare and energy), Automotive (~25%, battery management, in-cabin "
    "connectivity and ADAS), Communications (~15%, the fastest-growing at +63% YoY on data-center "
    "demand) and Consumer (~13%, wearables and premium handsets). AI is now a genuine, quantified "
    "driver: AI-linked automated test equipment (ATE) plus data center comprise ~20% of revenue "
    "(ATE grew ~40% and data center ~50% in FY2025, with record data-center orders in Q1 FY2026). "
    "The $1.5B all-cash acquisition of Empower Semiconductor (closed July 2026) adds vertical "
    "power-delivery technology aimed at the power-density problem of AI compute — extending ADI's "
    "portfolio from sensors and data converters at the intelligent edge all the way to rack-level "
    "power delivery at AI data centers. ADI returns ~100% of free cash flow to shareholders, with "
    "22 consecutive years of dividend increases and an ~$11.5B buyback authorization."
)

STRUCTURAL_UPDATES = {
    "ADI": {
        "brief.businessOverview": _ADI_BO,
        "brief.productModel": _ADI_PM,
    }
}


if __name__ == "__main__":
    companies = ["MPWR", "FIG", "TER", "INTC", "TENB", "SNAP", "ADI", "EGAN", "PCOR", "MDB"]
    for cid in companies:
        try:
            patch(
                cid,
                new_news=NEW_NEWS.get(cid),
                structural_updates=STRUCTURAL_UPDATES.get(cid),
            )
        except Exception as e:
            print(f"✗ {cid}: ERROR — {e}")
