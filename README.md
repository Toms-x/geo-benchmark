# geo-benchmark

A small study of which sources an AI answer engine retrieves versus which ones it actually cites, for crypto and fintech queries. It also measures how stable those citations are from run to run.

## Research question

When an AI answer engine searches the web for a query, which pages does it retrieve, which of those does it cite in its answer, and how repeatable is that over time?

This extends my earlier paper on the gap between being cited and being clicked: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7468658. That paper looked at what happens after a citation. This project looks at what earns one, and at how reliably it can be measured.

## Stages and main results

One engine throughout: Perplexity Agent API, preset `fast`, web search tool, search context `low`. The API reported the same model name (`openai/gpt-6-luna`) in every run.

- **Exploration:** 84 queries, 3 runs (2026-09-28, 2026-10-02, 2026-10-09).
- **Confirmation 1:** 153 queries drafted by an AI assistant, 2 runs (2026-10-11, 2026-10-15). Hypotheses (`docs/hypotheses.md`) and the query set were committed before the first run.
- **Confirmation 2:** 200 queries taken from Google Autocomplete and People Also Ask suggestions by a fixed-rule script, 2 runs (2026-10-24, 2026-10-27). The query builder, query set, hypotheses (`docs/hypotheses_confirm2.md`) and analysis code were all committed before the first run.

Confirmation 1 supported 3 of 6 tested hypotheses (1 was untested). Confirmation 2 supported 3 of 6. Full output is in `docs/confirmation_results.txt` and `docs/confirmation2_results.txt`.

**Held up across stages**
- Per-query citations are unstable. Mean overlap of cited domains between two runs was 0.28 to 0.36 in exploration, 0.38 in confirmation 1, and 0.45 in confirmation 2 (95% interval 0.41 to 0.50). It was below 0.5 in every stage.
- Aggregates are more stable. Nine domains were in the top 15 in all three exploration runs, 11 were shared in confirmation 1, and 14 in confirmation 2.
- Live price queries are cited less. The gap to other queries was 0.20 to 0.29 in exploration, 0.17 to 0.21 in confirmation 1, and 0.12 to 0.13 in confirmation 2, with intervals above zero in both confirmations. The size depends on the query set, and in confirmation 2 it fell below the pre-specified 0.15.
- Finance institutions are cited more than baseline. The group (Fidelity, Wise, investor.gov, and others) was above baseline in all 7 runs, and in confirmation 2 by +0.21 and +0.14 with intervals above zero. It is carried by a few domains, and PayPal, Stripe and Robinhood are near baseline.

**Not established**
- Exchanges as a group: between 0.00 and +0.06 above baseline in every run, with intervals that include zero in both confirmations.
- Kraken: above baseline in all 7 runs, but no stage met the pre-specified standard in both runs.
- Withdrawn: Binance looked unusually high in run 1 of exploration (cite rate 0.68), fell in later runs, and was at baseline by run 3.

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
- `data/queries_confirm2.csv`, `data/citations_confirm2.csv`: confirmation 2 queries and results
- `data/raw_suggestions/seeds.csv`, `checksums.txt`: the seed words and checksums of the raw tool exports (the exports themselves are not redistributed)
- `analysis/build_confirm2_set.py`: builds the confirmation 2 query set with fixed rules
- `analysis/confirm2_analysis.py`, `apply_confirm2_labels.py`: tests the pre-specified hypotheses and labels new domains
- `docs/hypotheses_confirm2.md`, `docs/confirmation2_results.txt`: hypotheses and results for confirmation 2

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
- Raw exports from the query tool are not redistributed; SHA-256 checksums are in data/raw_suggestions/checksums.txt
- Confirmation 2 seeds were chosen by the author. Autocomplete suggestions often read as fragments, and a few odd queries remain.
- Place names were excluded from confirmation 2, so country-specific queries are not covered.

## Status

v0.2. Exploration and both confirmation stages are complete, and a paper draft is in progress. Possible next steps: a second engine, or rerunning the same queries a month later to see whether citations drift over a longer span.

## License

MIT