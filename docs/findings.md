# Findings log

## Setup
- Engine: Perplexity Agent API, preset fast, web_search tool, search context low
- Queries: 84 (76 standard, 8 live_price) across five categories
- Query sources: own GSC queries, competitor keyword data, autocomplete research, seed list
- Retrieved = sources returned by search. Cited = sources marked in the answer text.
- Cite rate = share of (query, domain) pairs where the domain was cited

## Run 1 (2026-09-28)
- Cost about $0.13 for the full run
- Live price queries: 15% cite rate vs 44% on standard queries (only 8 queries)
- Standard queries by category: 41% to 49%, no clear difference
- Exchange domains mostly near the 44% baseline. Binance highest at 68% (15 of 22).
  Coinbase 0 of 4. Counts are small, so these are leads only.

## Open questions
- How stable are cited domains between runs?
- Does the Binance result repeat?

## Limitations
- One engine, one preset, one run so far
- Part of the query set came from exchange keyword data
- Small per-domain counts