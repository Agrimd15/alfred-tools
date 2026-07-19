#!/usr/bin/env python3
"""
Surgical patch script for 2026-07-19 refresh batch.
Updates ONLY: trading, comps multiples, recentNews (new items prepended),
lastRunDate, brief.runDate, marketCloseAsOf, freshnessNote.
All other fields are left byte-for-byte intact.
"""

import json
import os
import sys
from copy import deepcopy

TODAY = "2026-07-19"
DATA_ROOT = os.environ.get("ATLAS_DATA_ROOT", os.getcwd())

# ── News items to prepend (new since last run) ──────────────────────────────
NEWS = {
    "NOW": [
        {
            "date": "2026-07-14",
            "headline": "BNP Paribas sees constructive setup going into Q2 results as Now Assist ACV approaches $1.5B target",
            "whyItMatters": "BNP Paribas flagged that Now Assist AI revenue-per-seat momentum is tracking toward a $1.5B ACV milestone, making the July 22 Q2 print a meaningful catalyst. The constructive setup note reinforces the platformization thesis heading into the quarter.",
            "source": "Seeking Alpha",
            "sourceUrl": "https://seekingalpha.com/news/4614093-servicenow-offers-constructive-setup-going-into-q2-results-bnp-says"
        },
        {
            "date": "2026-07-01",
            "headline": "Guggenheim upgrades ServiceNow to Buy ahead of Q2 2026 earnings on July 22, citing Now Assist AI acceleration and platformization momentum",
            "whyItMatters": "Guggenheim argued ServiceNow's AI seat-level monetization via Now Assist is accelerating ahead of the July 22 Q2 print, with platformization driving durable ARR expansion across IT, HR, and Customer workflows. The upgrade adds buy-side conviction ahead of a catalyst quarter.",
            "source": "Seeking Alpha (citing Bloomberg)",
            "sourceUrl": "https://seekingalpha.com/news/4608762-servicenow-upgraded-guggenheim"
        }
    ],
    "NTNX": [],  # data-only update; no new news confirmed
    "PATH": [
        {
            "date": "2026-07-15",
            "headline": "UiPath downgraded to Hold: 'cheap but without a catalyst'",
            "whyItMatters": "The analyst argued that while UiPath trades at a discount on an absolute basis (~3x EV/Rev), the lack of a near-term earnings catalyst — and the ongoing question of whether agentic AI cannibalizes RPA — makes the risk/reward unattractive until the next earnings print provides a re-rating trigger.",
            "source": "Seeking Alpha",
            "sourceUrl": "https://seekingalpha.com/article/4922257-uipath-cheap-but-without-a-catalyst-im-stepping-back-to-hold-downgrade"
        }
    ],
    "ZS": [
        {
            "date": "2026-07-04",
            "headline": "Recovery thesis: Zscaler's FY27 guidance reset called 'just a hiccup,' flex bookings and consumption pricing cited as structural positives",
            "whyItMatters": "The analysis argues Zscaler's FY2027 billings guidance cut reflects a one-time demand timing shift rather than structural SASE market deterioration. Flex booking accommodations and consumption-based upsells are cited as durable renewal catalysts that should narrow the gap between billings and ARR growth over the coming year.",
            "source": "Seeking Alpha",
            "sourceUrl": "https://seekingalpha.com/article/4918572-zscaler-why-the-fy27-reset-is-just-a-hiccup"
        }
    ],
    "BRZE": [],  # data-only update
    "DOCU": [
        {
            "date": "2026-07-09",
            "headline": "Seeking Alpha analyst upgrades Docusign to Buy citing EBIT +84.7% YoY, 13.9% shareholder yield from buybacks, and 25% sector discount at 18x earnings",
            "whyItMatters": "The upgrade argues the market is excessively discounting Docusign's profitability inflection: EBIT nearly doubled YoY on flat opex while management returned $1B+ through buybacks. At 18x forward earnings — a 25% discount to the broader software sector — the risk/reward is now skewed to the upside if IAM identity-module adoption accelerates.",
            "source": "Seeking Alpha",
            "sourceUrl": "https://seekingalpha.com/article/4920848-docusign-falling-from-excessive-market-fears-buy-the-opportunity-rating-upgrade"
        }
    ],
    "GFS": [
        {
            "date": "2026-07-16",
            "headline": "GlobalFoundries: Valuation doubts proven correct — bear maintains concerns ahead of July 30 Q2 earnings",
            "whyItMatters": "Bearish follow-up reiterates skepticism on GFS's DoC/CHIPS Act letter-of-support runway and questions whether AI infrastructure demand can offset the large SMD end-market exposure. The July 30 Q2 print is framed as a key test for whether the YTD rally (~110%) has gotten ahead of fundamentals.",
            "source": "Seeking Alpha",
            "sourceUrl": "https://seekingalpha.com/article/4922757-globalfoundries-my-valuation-doubts-have-been-proven-correct-and-i-still-have-major-concerns"
        },
        {
            "date": "2026-07-08",
            "headline": "Contrarian sell: GlobalFoundries 'not the AI winner you're looking for' at 14.5x EV/EBITDA with 39% SMD exposure",
            "whyItMatters": "Sell-rated analysis argues the AI infrastructure re-rating is overextended — GFS's 39% exposure to smart-mobile devices (SMD) limits how much AI DC upside can actually flow through. At 36x forward earnings, the valuation embeds a sector-rotation premium that may not survive the first earnings miss.",
            "source": "Seeking Alpha",
            "sourceUrl": "https://seekingalpha.com/article/4920718-globalfoundries-this-is-not-the-ai-winner-youre-looking-for"
        },
        {
            "date": "2026-07-06",
            "headline": "GlobalFoundries: AI infrastructure is creating a better business — Buy, $88 PT",
            "whyItMatters": "Bull case: Communications + Data Center revenues grew 32% and Auto grew 24% in Q1 2026, and silicon photonics is seen as a $2B TAM opportunity by 2030. The buy thesis centers on GFS being an underappreciated CHIPS-Act beneficiary with a TSMC-independent US fab footprint increasingly critical to hyperscaler supply diversification.",
            "source": "Seeking Alpha",
            "sourceUrl": "https://seekingalpha.com/article/4919988-globalfoundries-ai-infrastructure-creating-better-business"
        }
    ],
    "GWRE": [
        {
            "date": "2026-07-16",
            "headline": "Guidewire Software: The cloud story is priced in, but the platform story isn't — Buy, $167 FY2027 PT",
            "whyItMatters": "The analysis argues Guidewire's cloud migration is effectively complete (subscription/support at 66% of revenue, +27% YoY in Q3 FY2026), and the next re-rating driver is platform expansion — cross-selling analytics, digital portals, and marketplace applications on top of the core P&C system of record. At ~17x forward P/E the risk/reward favors the platform expansion thesis.",
            "source": "Seeking Alpha",
            "sourceUrl": "https://seekingalpha.com/article/4922730-guidewire-software-the-cloud-story-is-priced-in-but-the-platform-story-isnt"
        }
    ],
    "MNDY": [
        {
            "date": "2026-07-10",
            "headline": "monday.com's $553M buyback and seats-plus-credits AI pricing model seen as structural backstop against per-seat revenue erosion",
            "whyItMatters": "Analyst community debate: does the consumption-based AI credits model offset AI-driven headcount reductions? Bulls cite $1.21B cash and the buyback as a floor, arguing AI credits create durable upsell beyond seat count. Q2 2026 earnings (est. August 10) will be the first formal test of whether the hybrid model is expanding or compressing net revenue per customer.",
            "source": "Seeking Alpha",
            "sourceUrl": "https://seekingalpha.com/article/4917434-mondaycom-buyback-backstop-and-ai-pricing-reset"
        },
        {
            "date": "2026-07-03",
            "headline": "monday.com files AGM proxy to vote on executive compensation policy for co-CEOs and directors at August 6 shareholder meeting",
            "whyItMatters": "Shareholders will vote on a new compensation framework for co-CEOs Roy Mann and Eran Zinman alongside two director seats at the August 6 AGM — a governance catalyst running concurrent with Q2 earnings. Pay structure for a dual-CEO model at a ~$18B market cap company is an ongoing institutional-investor focus point.",
            "source": "SEC (6-K filing)",
            "sourceUrl": "https://www.sec.gov/Archives/edgar/data/0001845338/000117891326003403/exhibit_99-1.htm"
        }
    ],
    "ORCL": [
        {
            "date": "2026-07-16",
            "headline": "S&P cuts Oracle to BBB- (one notch above junk) citing OpenAI concentration, $97.6B net debt, and uncertain FCF path on $250B data-center expansion",
            "whyItMatters": "The most significant near-term risk crystallized: S&P flagged OpenAI as the 'key credit risk' representing over half of Oracle's $638B backlog. BBB- raises refinancing costs on the debt stack; FCF was already negative $23.7B in FY2026. The rating action forces credit-market scrutiny onto the same concentration and leverage arguments the equity market has so far overlooked.",
            "source": "Bloomberg",
            "sourceUrl": "https://www.bloomberg.com/news/articles/2026-07-16/oracle-risks-falling-behind-in-ai-race-as-spending-binge-bites"
        },
        {
            "date": "2026-07-15",
            "headline": "Oracle leads rivals in race to supply Japan with a classified air-gapped intelligence-sharing cloud",
            "whyItMatters": "Oracle's willingness to deliver a fully air-gapped sovereign cloud in Japan — ahead of AWS and Azure — extends the company's differentiation in regulated government cloud. Sovereign/defense cloud deals typically carry premium pricing and long contract tenors, supporting the backlog-to-revenue conversion thesis for the medium term.",
            "source": "Seeking Alpha (citing Financial Times)",
            "sourceUrl": "https://seekingalpha.com/news/4613805-oracle-leads-rivals-in-race-to-build-japans-secret-cloud-ft"
        },
        {
            "date": "2026-07-08",
            "headline": "Piper Sandler: Oracle Cloud Infrastructure could beat FY2027 revenue estimates as capex-driven capacity ramp translates to sales",
            "whyItMatters": "Constructive read: Oracle's 162% capex jump is capacity the company can now bill against, and analyst estimates for FY2027 cloud revenue (~$42B) may prove too conservative. The note provides an institutional bull anchor ahead of the September FY2027 Q1 earnings — the first formal read on whether the buildout is converting to contracted revenue.",
            "source": "Seeking Alpha",
            "sourceUrl": "https://seekingalpha.com/news/4612014-oracle-cloud-could-top-revenue-estimates-in-fiscal-2027-piper-sandler-says"
        }
    ],
    "PANW": [
        {
            "date": "2026-07-16",
            "headline": "Capital One upgrades Palo Alto Networks to Overweight, raises PT to $421, citing AI security consolidation and federal cybersecurity tailwinds",
            "whyItMatters": "Meaningful institutional upgrade from a neutral stance: analyst argued PANW is best-positioned as the cyber consolidator with AI-native threat detection and a growing federal footprint post-CyberArk integration. Shares rose ~2.5% on the day, adding to a 120%+ YTD run.",
            "source": "Seeking Alpha",
            "sourceUrl": "https://seekingalpha.com/news/4614524-palo-alto-networks-okta-upgraded-at-capital-one"
        },
        {
            "date": "2026-07-14",
            "headline": "Multiple analysts downgrade PANW to Hold/Sell after 120%+ YTD run, citing ~92x forward P/E as extreme exuberance",
            "whyItMatters": "At least three Seeking Alpha analysts published downgrades citing PANW's forward P/E at 275% premium to the IT sector median. Valuation is now the #1 debate heading into Q4 FY2026 earnings (est. mid-September) — any deceleration in NGS ARR growth or platformization bookings could trigger a sharp de-rating from this level.",
            "source": "Seeking Alpha",
            "sourceUrl": "https://seekingalpha.com/article/4920300-palo-alto-networks-extreme-exuberance-is-a-warning-sign-rating-downgrade"
        },
        {
            "date": "2026-07-07",
            "headline": "Needham raises Palo Alto Networks price target to $425 (Street-high), citing stronger NGS ARR growth and CyberArk identity-security integration",
            "whyItMatters": "New Street-high target reinforces that the CyberArk identity-security close in February 2026 is seen as additive to platformization breadth. Needham's bull thesis: identity + network + cloud security in one platform is structurally defensible and will sustain double-digit NGS ARR growth through FY2027.",
            "source": "Seeking Alpha",
            "sourceUrl": "https://seekingalpha.com/news/4611956-palo-alto-networks-in-spotlight-as-needham-ups-price-target"
        }
    ],
    "QLYS": [
        {
            "date": "2026-07-06",
            "headline": "Scotiabank upgrades Qualys to Outperform, joining JPMorgan's late-June upgrade, as vulnerability management demand surges on AI-driven attack surface expansion",
            "whyItMatters": "Two sell-side upgrades in quick succession signal a sentiment shift: VM demand is no longer viewed as structurally impaired by AI — rather, AI-generated code is expanding the attack surface and accelerating enterprise demand for automated vulnerability detection. Q2 2026 earnings on August 3 will be the first formal test of whether the demand pickup is in bookings.",
            "source": "Seeking Alpha",
            "sourceUrl": "https://seekingalpha.com/article/4920042-qualys-recent-tailwinds-should-propel-stock-price-higher"
        }
    ],
    "ADBE": [
        {
            "date": "2026-07-07",
            "headline": "HSBC upgrades Adobe to Buy with $308 PT, calling AI disruption risk 'overstated'",
            "whyItMatters": "HSBC argued Adobe's deep creative-workflow lock-in and embedded Firefly AI integration make material disruption unlikely, and the stock's 27%-plus de-rating from highs has more than priced in execution risk. The upgrade directly counters a same-day BofA sell rating, crystallizing the binary debate that will define ADBE's multiple through Q3 FY2026 earnings in September.",
            "source": "Seeking Alpha",
            "sourceUrl": "https://seekingalpha.com/news/4609643-adobe-rises-after-hsbc-upgrades-to-buy"
        },
        {
            "date": "2026-07-07",
            "headline": "Bank of America reinstates Adobe with Underperform rating and $190 PT, citing generative-AI competitive threat",
            "whyItMatters": "BofA analyst Tal Liani argued that generative AI lowers barriers to content creation and accelerates competition from lower-cost AI-native tools, directly threatening Adobe's premium pricing and ARR growth. At $190 — implying ~13% downside — this is one of the first major-bank sell ratings on the stock and adds a prominent bear voice concurrent with the company's CEO and interim-CFO search.",
            "source": "Seeking Alpha",
            "sourceUrl": "https://seekingalpha.com/news/4611936-adobe-gets-underperform-rating-at-bofa-as-ai-weighs-on-growth"
        }
    ],
    "ADSK": [
        {
            "date": "2026-07-17",
            "headline": "Second analyst upgrade calls Autodesk an 'AI-era software bargain too cheap to ignore' at 15x forward P/E",
            "whyItMatters": "Independent analysis reinforces a growing value thesis: ADSK's CAD/PLM franchise is deepening its moat via AI across Fusion, Revit, and Construction Cloud, and the stock's steep discount vs. historical multiples represents asymmetric upside if MaintainX integration executes as planned. Two upgrades within one week signal growing buy-side conviction that post-deal selling was excessive.",
            "source": "Seeking Alpha",
            "sourceUrl": "https://seekingalpha.com/article/4923197-autodesk-this-ai-era-software-bargain-is-too-cheap-to-ignore"
        },
        {
            "date": "2026-07-11",
            "headline": "Autodesk upgraded to Strong Buy at 52-week lows — MaintainX seen as underappreciated TAM expansion at ~15x forward P/E",
            "whyItMatters": "The upgrade argues ADSK has been excessively penalized for the $3.6B MaintainX deal, now trading well below its historical P/E range despite 16% Q1 FY2027 revenue growth. The bull case is that MaintainX extends Autodesk from design into operations and maintenance, creating a defensible design-to-operate platform with AI as the throughline.",
            "source": "Seeking Alpha",
            "sourceUrl": "https://seekingalpha.com/article/4917692-autodesk-at-15x-pe-this-is-a-compelling-buy-at-52-week-lows-rating-upgrade"
        },
        {
            "date": "2026-07-05",
            "headline": "Autodesk downgraded to Hold on MaintainX near-term P&L uncertainty and integration margin risk",
            "whyItMatters": "Contrasting with the bullish notes, this downgrade argues the $3.6B all-cash MaintainX acquisition introduces meaningful margin dilution and execution risk that clouds FY2027 earnings visibility. The bear case: while the lifecycle-extension rationale is sound, integration costs and revenue-timing uncertainty make risk/reward unattractive until management provides clearer margin guidance at the next print.",
            "source": "Seeking Alpha",
            "sourceUrl": "https://seekingalpha.com/article/4915508-autodesk-rating-downgrade-as-maintainx-makes-near-term-p-and-l-uncertain"
        }
    ],
    "ALAB": [
        {
            "date": "2026-07-17",
            "headline": "Analyst warns Astera Labs is 'one misstep away from a sharp re-rating' ahead of August 4 earnings",
            "whyItMatters": "The note argues ALAB's valuation embeds growth and earnings assumptions that materially exceed current revenue visibility and confirmed Scorpio X supply-chain capacity, leaving the stock acutely vulnerable to any Q2 shortfall or cautious 2H guidance. Director insider selling of ~$16.8M in shares the same week is cited as a corroborating caution signal, raising the execution bar for management on August 4.",
            "source": "Seeking Alpha",
            "sourceUrl": "https://seekingalpha.com/article/4923082-astera-labs-is-one-misstep-away-from-a-sharp-re-rating"
        },
        {
            "date": "2026-07-01",
            "headline": "Astera Labs Director Manuel Alba sells $16.8M in shares (37,535 shares) ahead of August 4 Q2 earnings",
            "whyItMatters": "A board director liquidating ~$16.8M of stock in the weeks before the Q2 earnings print is the most concrete insider-sentiment signal since the Q1 quadruple beat. At a stock trading above 50x forward P/E, pre-earnings insider sales at this scale heighten sensitivity to any execution miss on Scorpio X production volumes or 2H 2026 ramp guidance.",
            "source": "SEC EDGAR (Form 4 filing)",
            "sourceUrl": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001736297&type=4&dateb=&owner=include&count=40"
        }
    ],
    "ARM": [
        {
            "date": "2026-07-14",
            "headline": "HSBC downgrades Arm Holdings to Hold from Buy, raises PT to $315 — AGI CPU narrative 'overdone'",
            "whyItMatters": "HSBC analyst Frank Lee walked back the firm's own March Buy upgrade, arguing that the primary near-term upside catalyst for ARM's AGI CPU — incremental foundry capacity allocation — is unlikely to materialize fast enough to justify the current multiple. A price-target raise paired with a downgrade is a classic 'price has exceeded the thesis' signal, adding institutional weight to July's growing consensus that ARM is priced for perfection.",
            "source": "Seeking Alpha",
            "sourceUrl": "https://seekingalpha.com/news/4613591-arm-downgraded-at-hsbc-as-firm-sees-cpu-narrative-as-overdone"
        },
        {
            "date": "2026-07-10",
            "headline": "Bearish analysis: ARM's merchant-silicon pivot a 'dangerous game' at ~155x forward P/E with no execution margin",
            "whyItMatters": "The note argues ARM's $15B AGI CPU revenue target for FY2031 demands flawless execution across foundry capacity, hyperscaler adoption, and royalty mix shifts — at ~155x forward P/E the stock has fully priced that best-case scenario. Any slip in AGI CPU ramp timing, RISC-V IP penetration, or competitive response could trigger a severe de-rating; three independent bearish notes in July alone signals a meaningful sentiment shift.",
            "source": "Seeking Alpha",
            "sourceUrl": "https://seekingalpha.com/article/4920117-arm-holdings-dangerous-ai-game"
        },
        {
            "date": "2026-07-09",
            "headline": "Analyst flags SoftBank margin-loan liquidation as underappreciated ARM share-price headwind",
            "whyItMatters": "Bear thesis: SoftBank holds ARM equity as collateral for margin loans, creating a structural overhang — balance-sheet pressure on SoftBank could force secondary ARM share sales independent of the company's AGI CPU operational performance. This risk is additive to the fundamental valuation debate and could suppress shares in a down-tape environment regardless of near-term earnings delivery.",
            "source": "Seeking Alpha",
            "sourceUrl": "https://seekingalpha.com/article/4919689-arm-holdings-agentic-silicon-arbitrage-eclipsed-by-softbank-liquidation-threat-rating-downgrade"
        }
    ],
    "GTM": [
        {
            "date": "2026-07-10",
            "headline": "Federal securities class action lawsuit filed against ZoomInfo following 33% stock collapse on Q1 guidance cut",
            "whyItMatters": "Shareholders allege ZoomInfo failed to timely disclose deteriorating demand conditions — AI-driven seat churn and late-quarter buyer pauses — before the Q1 2026 earnings release. The lawsuit adds legal cost and management-bandwidth overhang to a team already executing a disruptive pricing restructuring, and increases headline risk through at least the Q3 2026 print.",
            "source": "Seeking Alpha",
            "sourceUrl": "https://seekingalpha.com/symbol/GTM"
        },
        {
            "date": "2026-07-08",
            "headline": "ZoomInfo enters Q3 with hybrid consumption pricing model now live — first operational test of the turnaround thesis",
            "whyItMatters": "The shift from seat-based SaaS to hybrid consumption pricing takes effect in Q3 2026 (August start), marking the first live implementation of the recovery plan announced at May's Q1 earnings. Bulls see repriced flexibility as the fix for AI-era churn; bears argue the transition will compress revenue before upsell materializes — making Q3 results the first definitive read on whether the model can stabilize.",
            "source": "Seeking Alpha",
            "sourceUrl": "https://seekingalpha.com/news/4590949-zoominfo-forecasts-fy-2026-revenue-1_185b-1_205b-amid-20-percent-workforce-reduction"
        }
    ],
}

# Maximum number of news items to keep in brief.recentNews
MAX_NEWS = 8


def load_json(path):
    with open(path, "r") as f:
        return json.load(f)


def save_json(path, obj):
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)
    print(f"  ✓ saved {path}")


def patch_company(company_id):
    profile_path = os.path.join(DATA_ROOT, "data-dumps", company_id, "profile.json")
    data_path = os.path.join(DATA_ROOT, "data-dumps", company_id, "runs", TODAY, "data.json")

    if not os.path.exists(profile_path):
        print(f"  ✗ profile.json not found: {profile_path}")
        return False
    if not os.path.exists(data_path):
        print(f"  ✗ data.json not found: {data_path}")
        return False

    profile = load_json(profile_path)
    data = load_json(data_path)

    # 1. Update top-level trading / freshness fields
    profile["marketCloseAsOf"] = data.get("marketCloseAsOf", TODAY)
    profile["freshnessNote"] = data.get("freshnessNote", f"All multiples reflect the {TODAY} market close.")
    profile["lastRunDate"] = TODAY

    # Carry trading dict to top level (for any template that reads it)
    if "trading" in data:
        profile["trading"] = data["trading"]

    # 2. Update brief.comps — match by ticker, update live multiples
    data_comps_by_ticker = {}
    for c in data.get("comps", []):
        t = c.get("ticker", "").upper()
        if t:
            data_comps_by_ticker[t] = c

    if "brief" in profile and "comps" in profile["brief"]:
        for comp in profile["brief"]["comps"]:
            ticker = comp.get("ticker", "").upper()
            if ticker in data_comps_by_ticker:
                dc = data_comps_by_ticker[ticker]
                # evRevenue in profile ← evRevenueLTM in data
                if "evRevenueLTM" in dc and dc["evRevenueLTM"] is not None:
                    comp["evRevenue"] = dc["evRevenueLTM"]
                if "revenueGrowth" in dc and dc["revenueGrowth"] is not None:
                    comp["revenueGrowth"] = dc["revenueGrowth"]
                if "grossMargin" in dc and dc["grossMargin"] is not None:
                    comp["grossMargin"] = dc["grossMargin"]

    # 3. Prepend new news items to brief.recentNews
    new_items = NEWS.get(company_id.upper(), [])
    if "brief" in profile:
        profile["brief"]["runDate"] = TODAY
        existing_news = profile["brief"].get("recentNews", [])
        # Avoid duplicates by headline
        existing_headlines = {item.get("headline", "").lower() for item in existing_news}
        items_to_add = [
            item for item in new_items
            if item.get("headline", "").lower() not in existing_headlines
        ]
        # Prepend new, trim to MAX_NEWS
        combined = items_to_add + existing_news
        profile["brief"]["recentNews"] = combined[:MAX_NEWS]

    save_json(profile_path, profile)
    return True


def main():
    companies = [
        "NOW", "NTNX", "PATH", "ZS", "BRZE", "DOCU", "GFS", "GWRE",
        "MNDY", "ORCL", "PANW", "QLYS",
        "ADBE", "ADSK", "ALAB", "ARM", "GTM",
    ]

    results = {"ok": [], "fail": []}
    for cid in companies:
        print(f"\nPatching {cid}...")
        ok = patch_company(cid)
        if ok:
            results["ok"].append(cid)
        else:
            results["fail"].append(cid)

    print(f"\n{'='*50}")
    print(f"Patched OK ({len(results['ok'])}): {' '.join(results['ok'])}")
    if results["fail"]:
        print(f"Failed  ({len(results['fail'])}): {' '.join(results['fail'])}")
    else:
        print("No failures.")
    return 0 if not results["fail"] else 1


if __name__ == "__main__":
    sys.exit(main())
