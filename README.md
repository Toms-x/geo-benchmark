# geo-benchmark

A small study of which sources an AI answer engine retrieves versus which ones it actually cites, for crypto and fintech queries. It also measures how stable those citations are from run to run.

## Research question

When an AI answer engine searches the web for a query, which pages does it retrieve, which of those does it cite in its answer, and how repeatable is that over time?

This extends my earlier paper on the gap between being cited and being clicked: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7468658. That paper looked at what happens after a citation. This project looks at what earns one, and at how reliably it can be measured.

## Stages and main results

One engine throughout: Perplexity Agent API, preset `fast`, web search tool, search context `low`. The API reported the same model (`openai/gpt-6-luna`) in every run.

- **Exploration:** 84 queries, 3 runs (2026-09-28, 2026-10-02, 2026-10-09).
- **Confirmation 1:** 153 queries drafted by from general knowledge and one GSC data, 2 runs (2026-10-11, 2026-10-15). Hypotheses (`docs/hypotheses.md`), queries, analysis script and domain labels were committed before the tests were run.
- **Confirmation 2:** planned, with queries taken from Google Autocomplete and People Also Ask suggestions.

**Held up in both stages**
- Per-query citations are unstable. Overlap of cited domains for the same query was 0.36 to 0.28 in exploration (runs 4 to 11 days apart) and 0.38 in confirmation (95% interval 0.34 to 0.42).
- Aggregates are more stable. Nine domains were in the top 15 cited domains in all three exploration runs, and 11 were shared between the two confirmation runs.
- Live price queries are cited much less. The gap to other queries was 0.20 to 0.29 in exploration (8 queries) and 0.17 to 0.21 in confirmation (25 queries), with intervals above zero.

**Leads that did not replicate at the pre-specified size**
- Binance: cite rate fell across the exploration runs (0.68, 0.60, 0.46) and was at baseline by run 3.
- Finance institutions: about +0.3 above baseline in exploration, +0.13 in both confirmation runs, with intervals including zero. Fidelity fell from 0.95 to about 0.44.
- Kraken: above baseline in every exploration run, but in confirmation one run passed (+0.25) and one did not (+0.07), and the intervals are wide.
- Exchanges as a group: near baseline in exploration, about 0.05 above in confirmation. The study cannot tell this from zero.
- OKX: not tested in confirmation, because it appeared in too few queries.

Of seven pre-specified hypotheses, three were supported, three were not, and one was untested. Full output is in `docs/confirmation_results.txt` and notes are in `docs/findings.md`.

## Method

- **Query sets:** unbranded crypto and fintech queries in five categories (crypto education, exchanges, trading, fintech, market data), each labeled `standard` or `live_price`. Exploration queries came from my own Search Console data, competitor keyword research, autocomplete research, and an AI-written seed list. Only query text is published, not traffic or volume figures.
- **Data collected:** for each query, every source the search returned (retrieved) and whether the answer text cited it (cited).
- **Cited:** a numbered [n] marker in the answer text points to the source. Checked on all raw answers from the exploration runs.
- **Cite rate:** the share of (query, domain) pairs where the domain was cited at least once in that answer.
- **Uncertainty:** 95% intervals from resampling queries, not pairs, since pairs from one answer are not independent.
- **Stability:** per-query Jaccard overlap of cited domains between runs, and overlap of the top 15 domains.
- **Domain types:** domains were labeled exchange, price tracker, education or media, finance institution, or other, by each site's main business, before cite rates by type were examined.

## Repo layout

- `data/queries.csv`, `data/citations.csv`: exploration queries and results
- `data/queries_confirm.csv`, `data/citations_confirm.csv`: confirmation 1 queries and results
- `scrapers/perplexity_scraper.py`: runs a query set and saves results
- `analysis/`: summaries, stability checks, domain labeling, and `confirm_analysis.py`, which tests the pre-specified hypotheses
- `docs/hypotheses.md`: hypotheses written before confirmation 1
- `docs/confirmation_results.txt`: output of the pre-specified tests
- `docs/findings.md`: running notes on results and limitations

## Run it

1. Install: `pip install requests python-dotenv pandas numpy`
2. Put `PERPLEXITY_API_KEY=your-key` in a `.env` file in the repo root
3. Exploration set: `python3 scrapers/perplexity_scraper.py` (use `--limit 3` to test)
4. Another set: `python3 scrapers/perplexity_scraper.py --queries data/queries_confirm.csv --out data/citations_confirm.csv --raw data/raw_confirm`

A run of 153 queries costs about 25 cents. The scraper is resumable within a day, and each UTC calendar day counts as one run.

## Limitations

- One engine and one preset, so findings may not carry over to other engines
- Short time spans: 11 days for exploration, 4 days for confirmation
- Small counts per category, query type and domain, and few live price queries (8 and 25)
- The 153 confirmation queries were drafted from general knowledge and a single GSC data, not taken from search data. 39 of 40 sampled queries were found in Google autocomplete, but they may read more like textbook questions than real searches. Confirmation 2 addresses this.
- Part of the exploration query set came from exchange keyword data, which may favor exchange domains
- Domain type labels cover about two thirds of confirmation query-domain pairs
- The baseline cite rate was lower on confirmation queries (0.38 to 0.40) than in exploration (0.43 to 0.45), cause unknown
- A few queries returned 20 sources instead of about 10
- Click and traffic data are not included, so this covers the citation side only

## Status

Exploration and confirmation 1 are complete. Confirmation 2 is being set up.

## License

MIT