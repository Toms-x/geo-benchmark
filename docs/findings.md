# Findings log

## Setup
- Engine: Perplexity Agent API, preset fast, web_search tool, search context low
- Queries: 84 (76 standard, 8 live_price) across five categories
- Query sources: own GSC queries, competitor keyword data, autocomplete research, seed list
- Retrieved = sources returned by search. Cited = sources marked in the answer text.
- Cite rate = share of (query, domain) pairs where the domain was cited
- Domain type labels (exchange, price_tracker, education_media, finance_institution, other)
  were assigned by each domain's main business, before looking at any cite-rate results

## Run 1 (2026-09-28)
- Cost about $0.13
- Live price queries: 15% cite rate vs 44% on standard queries (8 queries, small sample)
- Standard queries by category: 41% to 49%, no clear difference
- Exchange domains mostly near the 44% baseline. Binance highest at 68% (15 of 22).
  Coinbase 0 of 4.

## Run 2 (2026-10-02)
- One query ("best demo accounts for crypto trading") returned 20 sources instead of
  the usual 10. All other queries returned 9 or 10. Noted as a property of the API,
  not a script error.

## Stability check (run 1 vs run 2, 4 days apart)
- Per-query overlap in cited domains: mean Jaccard 0.363, median 0.333
- Several queries shared zero cited domains between the two runs despite both
  returning citations (e.g. "what is a token unlock and why does it matter",
  "current btc usdt price on exchanges")
- Top 15 most-cited domains overlapped 12 of 15 across runs
- Reading: citation at the single-query, single-run level is close to random.
  Citation frequency aggregated across the full query set is comparatively stable.
  This is the main methodological finding so far.

## Open questions
- Does the Jaccard figure change with a longer gap between runs, or a shorter one?
  Run 3 planned for approximately 2026-10-09 to check.
- Does the live-price-vs-standard gap hold once both runs are pooled?
- Does Binance's aggregate lead hold in run 3?

## Limitations
- One engine, one preset, two runs so far
- Part of the query set came from exchange keyword data
- Small per-domain and per-query counts
- No click or traffic data included yet