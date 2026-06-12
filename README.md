# The Case for Private Markets, Told Entirely From Public Data

A reproducible research notebook. Every figure is pulled **live from a primary
government source** — the Federal Reserve, the SEC, the IRS, and the U.S. Census
Bureau — by the code in [`private_markets.ipynb`](private_markets.ipynb). No analyst
spreadsheets, no third-party estimates: run the notebook and the numbers regenerate
from the public record.

## Findings (as of June 11, 2026 — rerun for current values)

| # | Finding | Source |
|---|---|---|
| 1 | Listed U.S. companies per million people peaked in **1996** and have fallen **57%** since. | World Bank, via FRED |
| 2 | **59,898 Form D** private placements were filed in the last 12 months (~164/day) vs **612 priced IPOs** — 98×. Operating companies raised **\$28B in IPOs vs ~\$949B in exempt offerings** in the SEC's latest reporting year. | SEC EDGAR; SEC capital-formation statistics |
| 3 | **12.3 million** U.S. tax returns (7.9% of filers) show income above the \$200k accreditation line — a large audience that is also **geographically scattered**: 13.3% of households earn \$200k+, yet in only 331 of 30,547 ZIP codes is that the median. | IRS Statistics of Income (TY2022); Census ACS 2024 |

GitHub renders the executed notebook — including all charts —
[directly in the browser](private_markets.ipynb).

## Run it yourself

**Requirements:** Python 3.12+, [uv](https://docs.astral.sh/uv/), and a free
[FRED API key](https://fred.stlouisfed.org/docs/api/api_key_request.html) (takes ~30 seconds).

```bash
git clone https://github.com/StartEngine/private-markets-research
cd private-markets-research
uv sync

# One-time: load the IRS and Census datasets into local stores (~1–2 min total).
# Census needs its own free key: https://api.census.gov/data/key_signup.html
uv run mcpwright-soi setup
CENSUS_API_KEY=your-census-key uv run mcpwright-census setup

# Run the notebook
export FRED_API_KEY=your-fred-key
uv run jupyter lab private_markets.ipynb
```

Or execute headlessly and view the refreshed result:

```bash
FRED_API_KEY=your-fred-key uv run jupyter nbconvert --to notebook --execute --inplace private_markets.ipynb
```

To produce the article-formatted PDF (prose and charts only, no code — StartEngine
brand styling):

```bash
uv run python make_article_pdf.py     # -> private_markets_article.pdf
```

The SEC asks API consumers to identify themselves; the notebook sets a descriptive
`User-Agent` by default (override with `EDGAR_MCP_USER_AGENT="your-app you@example.com"`).

## How the data is pulled

The notebook uses four open-source [Model Context Protocol](https://modelcontextprotocol.io)
servers — the same connectors work inside an AI assistant, which is how this analysis was
first prototyped:

| Source | Package |
|---|---|
| FRED® (Federal Reserve economic data, incl. vintage history) | [`mcpwright-fred`](https://pypi.org/project/mcpwright-fred/) |
| SEC EDGAR (filings, offerings, full-text search) | [`mcpwright-edgar`](https://pypi.org/project/mcpwright-edgar/) |
| IRS Statistics of Income (income & tax by ZIP) | [`mcpwright-soi`](https://pypi.org/project/mcpwright-soi/) |
| U.S. Census ACS (income, demographics by ZIP) | [`mcpwright-census`](https://pypi.org/project/mcpwright-census/) |

All four: [mcpwright.com](https://mcpwright.com) · [github.com/mcpwright](https://github.com/mcpwright)

## Disclaimers

This repository is for informational and educational purposes only. It is not investment
advice, an offer to sell, or a solicitation of an offer to buy any security. Past or
aggregate market activity does not predict the performance of any investment. Investments
in private companies involve a high degree of risk, including the possible loss of your
entire investment.

This product uses the FRED® API but is not endorsed or certified by the Federal Reserve
Bank of St. Louis. FRED® is a registered trademark of the Federal Reserve Bank of
St. Louis. SEC EDGAR, IRS SOI, and U.S. Census data are public records.

---

© 2026 StartEngine · research by the StartEngine engineering team
