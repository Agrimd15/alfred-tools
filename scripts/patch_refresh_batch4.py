#!/usr/bin/env python3
"""
Surgical patch for 2026-07-19 refresh — Batch 4: ABNB, ANET, BE, COIN, CPNG, FICO, IOT, MELI, PTC
Updates: marketCloseAsOf, freshnessNote, lastRunDate, trading, brief.comps, brief.recentNews, brief.runDate
Everything else left byte-for-byte intact.
"""
import json, os, sys

TODAY = "2026-07-19"
DATA_ROOT = os.environ.get("ATLAS_DATA_ROOT", os.getcwd())
MAX_NEWS = 8

NEWS = {
    "ABNB": [
        {
            "date": "2026-07-09",
            "headline": "Airbnb to Announce Second Quarter 2026 Results",
            "whyItMatters": "Confirms Q2 results on August 6, 2026 — the next major catalyst for ABNB after its beat-and-raise Q1; sets the timeline for investors ahead of the key summer-travel earnings print.",
            "source": "Airbnb Investor Relations",
            "sourceUrl": "https://investors.airbnb.com/news-details/2026/Airbnb-to-Announce-Second-Quarter-2026-Results/default.aspx"
        }
    ],
    "ANET": [
        {
            "date": "2026-07-09",
            "headline": "Arista Networks Could Post A Surprise In Q2",
            "whyItMatters": "Analyst argues ANET is positioned to beat its $2.8B Q2 revenue guide as AI Ethernet demand accelerates toward the company's $3.5B full-year AI fabric target; supply chain checks suggest gross margin may bottom at 62–64% before recovering.",
            "source": "Seeking Alpha",
            "sourceUrl": "https://seekingalpha.com/article/4920946-arista-networks-could-post-a-surprise-in-q2"
        }
    ],
    "BE": [
        {
            "date": "2026-07-08",
            "headline": "Bloom Energy falls amid Hunterbrook short report (update)",
            "whyItMatters": "Short-seller Hunterbrook Capital disclosed a short position alongside a report alleging Bloom remains reliant on Chinese scandium and questioning its AI data center revenue claims — driving a ~6% single-day drop and raising fundamental credibility questions about supply chain integrity and revenue quality.",
            "source": "Seeking Alpha",
            "sourceUrl": "https://seekingalpha.com/news/4612375-bloom-energy-falls-amid-hunterbook-short-report"
        },
        {
            "date": "2026-07-09",
            "headline": "Bloom Energy Faces Scrutiny Over Scandium Supply Chain, Shares Swing",
            "whyItMatters": "Bloomberg's independent coverage amplified the Hunterbrook controversy around Bloom's scandium sourcing, a critical input for its solid-oxide fuel cells; Bloom categorically rejected the claims but ongoing stock volatility signals the market is weighing the risk seriously.",
            "source": "Bloomberg",
            "sourceUrl": "https://www.bloomberg.com/news/articles/2026-07-09/bloom-energy-criticism-spotlights-vital-but-obscure-rare-mineral"
        },
        {
            "date": "2026-07-15",
            "headline": "Cramer's lightning round: Buy Bloom Energy",
            "whyItMatters": "Cramer's public buy call on Mad Money post-Hunterbrook sell-off signals a vocal retail-sentiment counter-narrative to the short report, potentially supporting near-term price stabilization and recovery.",
            "source": "CNBC",
            "sourceUrl": "https://www.cnbc.com/2026/07/15/cramers-lightning-round-buy-bloom-energy.html"
        }
    ],
    "COIN": [
        {
            "date": "2026-07-15",
            "headline": "Coinbase Announces Date of Second Quarter 2026 Financial Results",
            "whyItMatters": "Sets July 30, 2026 as the Q2 earnings date — a near-term catalyst where investors will scrutinize trading volume trends, stablecoin revenue contribution, and progress on derivatives and tokenized equities amid a Bitcoin rally of 10%+ in July.",
            "source": "Coinbase Investor Relations",
            "sourceUrl": "https://investor.coinbase.com/news/news-details/2026/Coinbase-Announces-Date-of-Second-Quarter-2026-Financial-Results/default.aspx"
        }
    ],
    "CPNG": [
        {
            "date": "2026-07-09",
            "headline": "Coupang faces 300B won tax assessment following NTS special audit",
            "whyItMatters": "South Korea's National Tax Service levied a ~$220M tax bill on Coupang following a special audit, adding a material financial and regulatory overhang to an already-loss-making Developing Offerings segment. The assessment could pressure cash flows and signals heightened regulatory scrutiny of Coupang's domestic operations.",
            "source": "Seeking Alpha",
            "sourceUrl": "https://seekingalpha.com/news/4612707-coupang-faces-300b-won-tax-assesment-following-nts-special-audit"
        }
    ],
    "FICO": [
        {
            "date": "2026-07-15",
            "headline": "Fair Isaac Corporation Announces Date for Reporting of Third Quarter Fiscal 2026 Financial Results",
            "whyItMatters": "FICO set its Q3 FY2026 earnings announcement — a near-term catalyst for investors watching whether the Scores business can sustain the +60% YoY growth seen in Q2, and whether VantageScore adoption is materially denting mortgage-score volumes.",
            "source": "FICO Newsroom",
            "sourceUrl": "https://www.fico.com/en/newsroom/fair-isaac-corporation-announces-date-reporting-third-quarter-fiscal-2026-financial-results"
        }
    ],
    "IOT": [
        {
            "date": "2026-07-15",
            "headline": "Samsara Study Reveals Equipment Theft and Loss Costs Mid-Size Operations an Average of $18M Annually",
            "whyItMatters": "Samsara published proprietary data on physical asset losses, reinforcing the ROI case for its Connected Operations platform and providing an independent validation of the addressable problem it solves. Research-led demand generation of this kind supports enterprise sales cycles.",
            "source": "BNN Bloomberg",
            "sourceUrl": "https://www.bnnbloomberg.ca/press-releases/2026/07/15/samsara-study-reveals-equipment-theft-and-loss-costs-mid-size-operations-an-average-of-18m-annually/"
        },
        {
            "date": "2026-05-28",
            "headline": "Samsara Sweeps Fleet Technology Rankings With 23 No. 1 Rankings Across Reports",
            "whyItMatters": "Samsara earned 23 top-ranked positions in the G2 Summer 2026 grid reports for fleet management, reinforcing its market-leadership position and providing third-party social proof that supports the land-and-expand motion among new enterprise customers.",
            "source": "Samsara Newsroom",
            "sourceUrl": "https://www.samsara.com/company/news/press-releases/summer-2026-grid-reports"
        }
    ],
    "MELI": [
        {
            "date": "2026-07-07",
            "headline": "MercadoLibre: Near-Term Margin Pressure Creates A Buying Opportunity",
            "whyItMatters": "A Seeking Alpha analyst argued that the deliberate margin investment (lower free-shipping thresholds, 1P retail expansion, credit scaling) that compressed Q1 2026 operating margin to ~6.9% is transient, and that the structural compounding of GMV/TPV growth makes the dip a buying opportunity — framing the core bull/bear debate for the stock.",
            "source": "Seeking Alpha",
            "sourceUrl": "https://seekingalpha.com/article/4920197-mercadolibre-stock-near-term-margin-pressure-creates-a-buying-opportunity"
        },
        {
            "date": "2026-07-05",
            "headline": "MercadoLibre Stock: The Dip Is Here, But So Is A New Problem",
            "whyItMatters": "A Seeking Alpha analysis flagged that while MercadoLibre's pullback offers valuation entry, rising credit losses and elevated fintech risk in Brazil present a 'new problem' alongside the established competitive pressure from Sea Limited and Amazon — crystallizing the two-sided risk investors must weigh.",
            "source": "Seeking Alpha",
            "sourceUrl": "https://seekingalpha.com/article/4919876-mercadolibre-the-dip-is-here-but-so-is-a-new-problem"
        }
    ],
    "PTC": [
        {
            "date": "2026-07-14",
            "headline": "PTC Introduces Onshape Labs to Accelerate AI Inside the Product Development Process",
            "whyItMatters": "PTC launched Onshape Labs as an AI experimentation environment within its cloud-native CAD platform, signaling a faster path to embedding generative AI into product development workflows. This expands the Onshape growth story beyond pure CAD into AI-enabled PLM, a key differentiator versus legacy on-prem competitors.",
            "source": "PRNewswire",
            "sourceUrl": "https://www.prnewswire.com/news-releases/ptc-introduces-onshape-labs-to-accelerate-ai-inside-the-product-development-process-302825032.html"
        },
        {
            "date": "2026-07-14",
            "headline": "Customer & Partner Updates: RCE Vulnerability in PTC's Windchill and FlexPLM",
            "whyItMatters": "PTC disclosed a remote code execution vulnerability in Windchill and FlexPLM, its core on-prem PLM product — a risk flagged to enterprise customers that could slow on-prem renewals and accelerate cloud migration to Windchill+, but also introduces near-term support/remediation burden.",
            "source": "PTC Trust Center",
            "sourceUrl": "https://www.ptc.com/en/about/trust-center/advisory-center/active-advisories/windchill-flexplm-rce-vulnerability"
        },
        {
            "date": "2026-07-08",
            "headline": "PTC to Announce Fiscal Q3'26 Results on Wednesday, July 29, 2026",
            "whyItMatters": "PTC set its Q3 FY2026 earnings call for July 29 — the next major catalyst where investors will assess whether constant-currency ARR growth is tracking to the 7.5-9.5% FY2026 guide and whether the ThingWorx/Kepware divestiture has freed up capital allocation for buybacks or further M&A.",
            "source": "PTC Investor Relations",
            "sourceUrl": "https://investor.ptc.com/resources/news/news-details/2026/PTC-to-Announce-Fiscal-Q326-Results-on-Wednesday-July-29-2026/default.aspx"
        },
        {
            "date": "2026-07-07",
            "headline": "Whatfix and PTC Partner to Improve PLM Adoption for Modern Manufacturers",
            "whyItMatters": "PTC and Whatfix partnered to embed digital adoption tooling directly into the PLM workflow, addressing a key friction point in enterprise PLM deployment. Easier onboarding supports ARR expansion and retention in PTC's largest revenue segment.",
            "source": "PRNewswire",
            "sourceUrl": "https://www.prnewswire.com/news-releases/whatfix-and-ptc-partner-to-improve-plm-adoption-for-modern-manufacturers-302819014.html"
        }
    ],
}

COMPANIES = ["ABNB", "ANET", "BE", "COIN", "CPNG", "FICO", "IOT", "MELI", "PTC"]


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
