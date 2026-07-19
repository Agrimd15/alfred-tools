#!/usr/bin/env python3
"""
Surgical patch for 2026-07-19 refresh — Batch 3: CDNS, CRDO, DASH, FTNT, GEN, INTU, PYPL, SE
Updates: marketCloseAsOf, freshnessNote, lastRunDate, trading, brief.comps, brief.recentNews, brief.runDate
Everything else left byte-for-byte intact.
"""
import json, os, sys

TODAY = "2026-07-19"
DATA_ROOT = os.environ.get("ATLAS_DATA_ROOT", os.getcwd())
MAX_NEWS = 8

NEWS = {
    "CDNS": [
        {
            "date": "2026-07-17",
            "headline": "Cadence Sinks ~9% as Moonshot's Kimi K3 AI Designs Chip in 48 Hours Without Proprietary EDA Tools; BNP Paribas Says Buy the Dip",
            "whyItMatters": "Moonshot AI's demonstration that its Kimi K3 model could complete a full chip design flow in 48 hours using open-source EDA tools — without Cadence or Synopsys — sent both stocks down sharply (~9% CDNS, ~8% SNPS). The event crystallizes the core bear case for EDA incumbents: that AI-native open-source workflows could erode the stranglehold of proprietary toolchains. BNP Paribas moved to Buy on the pullback, arguing the demo was constrained to simpler designs and that Cadence's full-stack verification, signoff, and advanced-node relationships are structurally defensible — but the debate is now front-of-mind ahead of Cadence's July 27 Q2 earnings, where management will need to address EDA disruption risk directly.",
            "source": "Seeking Alpha",
            "sourceUrl": "https://seekingalpha.com/news/4615018-cadence-synopsys-sink-as-moonshot-brings-eda-disruption-risks-bnp-says-buy-the-dip"
        },
        {
            "date": "2026-07-17",
            "headline": "Cadence Partners with Rapidus to Integrate Agentic AI Into 2nm SoC Design, Targeting 2X Faster Turnaround",
            "whyItMatters": "Cadence and Japan's Rapidus (building a 2nm foundry in Hokkaido targeting 2027 volume production) struck a partnership to embed Cadence's agentic AI capabilities directly into the SoC design flow for 2nm chips, with a stated target of 2x faster design turnaround. The deal reinforces Cadence's position as the EDA partner of choice for leading-edge node entrants and diversifies its foundry relationships beyond TSMC/Samsung — a direct counter-narrative to the open-source-EDA disruption fear triggered the same day by Moonshot's Kimi K3 demo.",
            "source": "HPCwire",
            "sourceUrl": "https://www.hpcwire.com/off-the-wire/cadence-and-rapidus-partner-on-agentic-ai-for-advanced-soc-design/"
        },
        {
            "date": "2026-07-16",
            "headline": "Benchmark Initiates Cadence Design Systems and Synopsys with Buy Ratings on AI-Driven EDA Outlook",
            "whyItMatters": "Benchmark Capital initiated both CDNS and SNPS at Buy, arguing that AI is a structural tailwind for EDA spending rather than a disruptor — as chip designs grow more complex (AI accelerators, 2nm/gate-all-around), the dollar value of EDA software per design increases. The initiation added a new buy-side voice to the bull camp days before the Moonshot-triggered selloff, framing AI as demand expansion for Cadence's platform rather than a replacement threat.",
            "source": "Investing.com",
            "sourceUrl": "https://www.investing.com/news/stock-market-news/benchmark-initiates-synopsys-cadence-with-buy-ratings-on-aidriven-eda-outlook-4795934"
        }
    ],
    "CRDO": [
        {
            "date": "2026-07-18",
            "headline": "Insider Selling Overhang and Samsung-Triggered Semiconductor Sector Rout Crush Credo Shares 8.3%",
            "whyItMatters": "CRDO fell 8.3% in a single session as a Samsung earnings-driven semiconductor sector selloff compounded an ongoing cluster of high-profile insider sales. The combined insider-selling + sector-rout dynamic raises the question of whether the stock's ~27x EV/Rev premium can hold as the AI-interconnect cycle matures — especially with insiders reducing exposure near all-time highs even as Wall Street raises price targets.",
            "source": "TipRanks",
            "sourceUrl": "https://www.tipranks.com/news/catalyst/insider-selling-and-sector-rout-crush-credo-shares"
        },
        {
            "date": "2026-07-15",
            "headline": "Credo COO Sells $12.6M in Shares; Co-Founder Exits Multi-Million Block as Insiders Collectively Dump Near Highs",
            "whyItMatters": "Credo's COO sold 55,998 shares for $12.6M and a co-founder exited a large block in the same week, adding to a cluster of insider disposals near all-time highs. While insider selling at a 157%-growth company after a large stock-price run is not automatically bearish, the volume and breadth of sales — spanning C-suite and founding team — is a factor the market is pricing as an overhang. Bears will cite it as smart-money distribution; bulls argue it is routine diversification by founders after a major appreciation.",
            "source": "Motley Fool",
            "sourceUrl": "https://www.fool.com/coverage/filings/2026/07/16/credo-technology-coo-sells-55998-shares-for-126-million/"
        },
        {
            "date": "2026-07-06",
            "headline": "Wall Street Hikes Aggressive AI Price Targets on Credo as Insiders Simultaneously Trim Stakes",
            "whyItMatters": "Multiple Wall Street analysts raised Credo price targets — including BofA raising to $340 — citing AI-driven active-copper-cable demand as a multi-year structural opportunity. The bullish analyst action contrasted sharply with simultaneous insider sales, setting up a visible bull/bear tension: institutional sell-side sees a durable re-rating ahead, while company insiders are reducing. This divergence is worth tracking through the next earnings print.",
            "source": "StocksToTrade",
            "sourceUrl": "https://stockstotrade.com/news/credo-technology-group-holding-ltd-crdo-news-2026_07_06-2/"
        }
    ],
    "DASH": [
        {
            "date": "2026-07-14",
            "headline": "DoorDash Integrates Directly with Shopify to Connect Brick-and-Mortar Retailers with On-Demand Delivery",
            "whyItMatters": "DoorDash's Shopify integration gives every Shopify merchant (millions of SMBs) a direct path to same-day local delivery through DoorDash Drive On-Demand — without custom API work. This extends DoorDash's last-mile network beyond restaurant food into general retail, a key growth vector for monetizing idle delivery capacity and competing with Amazon's same-day network. For the DoorDash bull case, each Shopify merchant that adopts the integration is a new incremental GTV stream.",
            "source": "Seeking Alpha",
            "sourceUrl": "https://seekingalpha.com/news/4613601-doordash-partners-with-shopify-to-offer-delivery-options-for-smaller-merchants"
        },
        {
            "date": "2026-07-14",
            "headline": "DoorDash, Observe.AI, and AWS Partner to Scale Customer-Centric AI Across 19,000 Agents",
            "whyItMatters": "DoorDash is deploying Observe.AI's conversation intelligence platform across its 19,000-agent customer service operation, powered by AWS. The initiative targets reducing handle time, improving resolution rates, and generating structured data for coaching — the kind of operational leverage at contact-center scale that feeds directly into DoorDash's margin-expansion thesis. It also signals DoorDash as an early enterprise-scale adopter of AI contact-center automation, relevant to the platform's credibility with Dasher + merchant + consumer support at scale.",
            "source": "PR Newswire",
            "sourceUrl": "https://www.prnewswire.com/news-releases/doordash-observeai-and-aws-partner-to-scale-customer-centric-ai-across-19000-agents-302824595.html"
        },
        {
            "date": "2026-07-06",
            "headline": "Wells Fargo Cuts DoorDash Price Target to $199, Most Bearish Call on the Street",
            "whyItMatters": "Wells Fargo's cut to $199 — below consensus and positioning it as the most bearish major institutional call on DASH — argues that the stock's premium multiple (~5x EV/Rev) leaves little margin for error as competition from Uber Eats, Amazon Fresh, and international players intensifies. The call reinforces the structural bear view that DoorDash's high market share in US restaurant delivery is difficult to extend into adjacent verticals at comparable economics, while customer acquisition costs and Dasher incentive costs remain structurally elevated.",
            "source": "MarketBeat",
            "sourceUrl": "https://www.marketbeat.com/instant-alerts/doordash-nasdaqdash-price-target-cut-to-19900-by-analysts-at-wells-fargo-company-2026-07-06/"
        }
    ],
    "FTNT": [
        {
            "date": "2026-07-14",
            "headline": "Fortinet Expands FortiEndpoint with New AI-Era Capabilities Including AI Visibility, Native DLP, and Zero-Trust Access",
            "whyItMatters": "Fortinet expanded its endpoint platform with AI-visibility dashboards, native data-loss-prevention, and zero-trust network-access controls — positioning FortiEndpoint as a unified AI-security layer rather than a point tool. The expansion is directly relevant to Fortinet's platform consolidation thesis: as enterprises tighten security stacks, having DLP + ZTNA + AI visibility natively embedded in the endpoint agent creates cross-sell opportunities for existing firewall/SD-WAN customers and makes point-product displacement harder.",
            "source": "GlobeNewswire",
            "sourceUrl": "https://www.globenewswire.com/news-release/2026/07/14/3326925/0/en/fortinet-expands-fortiendpoint-with-new-capabilities-for-the-ai-era.html"
        },
        {
            "date": "2026-07-14",
            "headline": "BTIG Research Raises Fortinet Price Target to $186 from $150, Maintains Buy Rating",
            "whyItMatters": "BTIG's $186 target raise — a 24% increase — joins a broader analyst price-target upgrade cycle into Fortinet's July 29 Q2 earnings. BTIG cited accelerating firewall-refresh demand and improving SASE attach rates as the key drivers, arguing Fortinet's ASICs + OT security + SD-WAN bundle creates durable pricing power that the market is undervaluing. Multiple simultaneous PT raises ahead of earnings tend to lift consensus and draw momentum capital.",
            "source": "Daily Political",
            "sourceUrl": "https://www.dailypolitical.com/2026/07/14/recent-analysts-ratings-changes-for-fortinet-ftnt.html"
        },
        {
            "date": "2026-07-13",
            "headline": "TD Cowen and Cantor Fitzgerald Both Raise Fortinet Price Targets Sharply Ahead of Q2 Earnings",
            "whyItMatters": "TD Cowen and Cantor Fitzgerald both raised their Fortinet price targets ahead of the July 29 Q2 earnings call, adding momentum to a growing analyst bull camp on the name. The back-to-back upgrades signal building sell-side conviction that Fortinet's platform-consolidation narrative is tracking well — particularly as enterprise security budgets shift toward unified SASE/firewall vendors over point-solution sprawl. The earnings print will be the first chance for management to confirm whether the bullish channel checks are translating into bookings.",
            "source": "Yahoo Finance",
            "sourceUrl": "https://finance.yahoo.com/markets/stocks/articles/td-cowen-cantor-fitzgerald-increase-083052954.html"
        }
    ],
    "GEN": [
        {
            "date": "2026-07-15",
            "headline": "Gen H1 2026 Threat Report: Breach Notification Alerts +628%, 1.9B Tracking Attempts Blocked",
            "whyItMatters": "Gen's half-year threat intelligence report showed a 628% year-over-year surge in breach notification alerts, 114 million blocked e-shop scam attacks (+109%), and 1.9 billion blocked tracking attempts across its ~500 million user base. The data validates accelerating structural demand for the Cyber Safety Platform and LifeLock identity protection, supporting the thesis that rising consumer vulnerability is a durable tailwind for Gen's FY2027 8-10% revenue growth target. Elevated threat volume also reduces churn as customers see the platform actively protecting them and creates upsell leverage into premium identity-theft tiers.",
            "source": "PR Newswire",
            "sourceUrl": "https://www.prnewswire.com/news-releases/gen-half-year-threat-report-attackers-are-moving-closer-to-the-systems-people-trust-302826372.html"
        },
        {
            "date": "2026-07-14",
            "headline": "Gen Digital Sets Q1 FY2027 Earnings Call for August 6, 2026",
            "whyItMatters": "August 6 is the next hard investment catalyst for GEN — the first quarterly report under Gen's FY2027 guidance framework of 8-10% revenue growth and $2.85-$2.95 EPS. The market will focus on whether the Trust-Based Solutions segment (MoneyLion integration) is tracking those targets and whether Cyber Safety Platform momentum is sustained. With GEN trading at a deep discount (~4.8x EV/Rev) relative to enterprise-cyber peers, a strong Q1 print could catalyze a meaningful re-rating.",
            "source": "PR Newswire",
            "sourceUrl": "https://www.morningstar.com/news/pr-newswire/20260714la04512/gen-to-announce-fiscal-2027-first-quarter-results-on-august-6-2026"
        }
    ],
    "INTU": [
        {
            "date": "2026-07-14",
            "headline": "Piper Sandler Initiates Intuit at Underweight With $250 Price Target, Stock Falls 3.4%",
            "whyItMatters": "Piper Sandler's Underweight initiation at $250 — implying roughly 10% additional downside from $280 — piles a fresh institutional bear thesis onto an already-battered stock (down 50%+ YTD) and drove a 3.4% single-day decline. The call argued TurboTax structural risks (IRS Direct File competition, declining total filer counts, free-file pricing pressure) remain underappreciated even after the selloff. Combined with Stifel's June downgrade to Hold, the bear camp is gaining sell-side representation that matters for institutional flow mechanics heading into Intuit's next earnings.",
            "source": "Seeking Alpha",
            "sourceUrl": "https://seekingalpha.com/news/4613617-intuit-stock-declines-after-piper-sandler-assumes-coverage-with-sell-equivalent-rating"
        },
        {
            "date": "2026-07-13",
            "headline": "Intuit Hit With Multiple Securities Class Action Lawsuits Over Alleged TurboTax Misrepresentations",
            "whyItMatters": "BFA Law, Levi & Korsinsky, and Robbins Geller filed federal securities fraud class actions in a three-day window (July 13-16), alleging Intuit made materially false and misleading statements about TurboTax's competitive advantages and growth prospects during the August 22, 2025 – May 20, 2026 class period. The suits were triggered by the May 21 disclosure of weak tax-season results that caused a 20% single-day stock plunge. The litigation cluster adds a meaningful legal overhang to an already distressed name, with the September 8, 2026 lead-plaintiff deadline keeping headline pressure elevated through Q3.",
            "source": "Business Wire",
            "sourceUrl": "https://www.businesswire.com/news/home/20260713519990/en/INTU-Breaking-News-Intuit-Inc.-Sued-for-Securities-Fraud-After-Reporting-Weak-Tax-Season-Revenue-Precipitating-20-Stock-Drop-Investors-Notified-to-Contact-BFA-Law"
        },
        {
            "date": "2026-07-08",
            "headline": "Seeking Alpha: Intuit 'Signs of a Bottom' — 'Shares Way Too Cheap' After 50%+ YTD Selloff",
            "whyItMatters": "A contrarian bull thesis is emerging as Intuit trades near multi-year lows (~$280) despite raising FY2026 guidance to $21.3-21.4B and authorizing an $8B buyback on top of $3.34B already repurchased YTD. The bull view argues Intuit now trades at roughly 10x forward P/E vs. its historical 30-40x range — suggesting TurboTax headwinds are fully priced while QuickBooks/Global Business Solutions momentum (+10% Q3 revenue growth) and AI platform optionality (Credit Karma, Intuit Enterprise Suite mid-market push) are being ignored. The piece signals the bear thesis may be running out of room.",
            "source": "Seeking Alpha",
            "sourceUrl": "https://seekingalpha.com/article/4920614-intuit-signs-of-a-bottom-shares-way-too-cheap-as-the-ai-trade-wobbles"
        }
    ],
    "PYPL": [
        {
            "date": "2026-07-15",
            "headline": "Stripe and Advent Reportedly Offered to Buy PayPal for Around $53.4 Billion",
            "whyItMatters": "TechCrunch reported that Stripe and private-equity firm Advent International jointly offered to acquire PayPal for approximately $53.4 billion (~$60.50/share), representing a ~28% premium to PayPal's pre-report price. If completed, this would be among the largest fintech acquisitions ever and would combine PayPal's 400M+ consumer accounts and merchant acceptance network with Stripe's developer-first payments infrastructure — creating a payments super-platform that could challenge Visa/Mastercard across online + offline commerce. The deal remains unconfirmed and faces significant regulatory scrutiny; PayPal has not commented publicly. The report immediately re-priced the takeover optionality embedded in PYPL's depressed valuation.",
            "source": "TechCrunch",
            "sourceUrl": "https://techcrunch.com/2026/07/15/stripe-and-advent-reportedly-offered-to-buy-paypal-for-around-53-4b/"
        },
        {
            "date": "2026-07-15",
            "headline": "KKR Markets Europe's First Securitization Backed by PayPal Buy Now, Pay Later Loans",
            "whyItMatters": "KKR brought the first European ABS securitization backed by PayPal BNPL receivables to market, a transaction that validates PayPal's credit portfolio as institutional-grade collateral and provides a capital-efficient funding channel for scaling the BNPL book. Access to the securitization market reduces PayPal's balance-sheet exposure as it grows BNPL volume, lowers funding costs, and signals that institutional fixed-income investors view the underlying credit quality favorably — a direct counter to concerns about credit deterioration in consumer lending portfolios.",
            "source": "Bloomberg",
            "sourceUrl": "https://www.bloomberg.com/news/articles/2026-07-15/kkr-markets-debt-backed-by-paypal-s-buy-now-pay-later-loans"
        },
        {
            "date": "2026-07-08",
            "headline": "Barclays Initiates PayPal Coverage with Underweight Rating",
            "whyItMatters": "Barclays initiated PayPal at Underweight (the equivalent of a Sell), arguing that even after the 80% decline from 2021 peaks, the stock's valuation does not adequately discount the structural take-rate compression, branded-checkout market-share losses to Apple Pay and Shop Pay, and the uncertainty around new CEO Enrique Lores's turnaround timeline. The initiation adds a major-bank bear voice to PayPal's sell-side mix at a moment when bulls are pointing to the $6B+ FCF yield and $6B annual buyback as the floor. Barclays's bear case puts the Stripe/Advent acquisition bid — if real — in sharper relief as a potential exit for long-suffering shareholders.",
            "source": "Seeking Alpha",
            "sourceUrl": "https://seekingalpha.com/news/4614635-sa-analyst-upgrades-downgrades-sndk-aapl-pypl-now"
        }
    ],
    "SE": [
        {
            "date": "2026-07-16",
            "headline": "Sea Limited: 3 Growth Engines, 1 Undervalued Stock — Analysts Highlight Shopee, Monee, Garena Convergence",
            "whyItMatters": "A detailed analyst piece argued Sea Limited is structurally undervalued as its three growth engines — Shopee (GMV +30%), Monee/SeaMoney (loan book +71%), and Garena (Free Fire bookings +20%) — are converging simultaneously into profitability for the first time, yet the stock trades ~48% below its 52-week high. The thesis is that the market is pricing in a single-engine slowdown that isn't occurring: all three are growing and throwing off positive cash flow, creating flywheel effects (gaming engagement drives e-commerce, e-commerce drives fintech, fintech drives loyalty). The piece reinforces the core bull case ahead of the next quarterly print.",
            "source": "Seeking Alpha",
            "sourceUrl": "https://seekingalpha.com/article/4922831-sea-limited-3-growth-engines-1-undervalued-stock"
        },
        {
            "date": "2026-07-07",
            "headline": "Sea Limited Shares Slip After 7-Day Win Streak as Stock Remains ~15% Above Late-June Lows",
            "whyItMatters": "After a 7-day rally that lifted Sea Limited ~15% off its late-June lows, the stock gave back a modest portion of gains — a normal consolidation after a sharp move. The context matters: the pullback came with no negative company-specific news, suggesting the prior rally was driven by improving risk appetite for Southeast Asian growth stocks and Sea's Q1 2026 results beat rather than any fundamental change. The stock remaining well above lows signals the market is maintaining a floor built on Sea's Q1 profitability inflection and the structural Southeast Asian digital-economy story.",
            "source": "Seeking Alpha",
            "sourceUrl": "https://seekingalpha.com/symbol/SE"
        }
    ]
}

COMPANIES = ["CDNS", "CRDO", "DASH", "FTNT", "GEN", "INTU", "PYPL", "SE"]

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
