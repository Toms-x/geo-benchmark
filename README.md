# geo-benchmark

A small, early-stage study of which sources an AI answer engine retrieves versus which ones it actually cites, for crypto and fintech queries. It also measures how stable those citations are from run to run.

## Research question

When an AI answer engine searches the web for a query, which pages does it retrieve, which of those does it cite in its answer, and how repeatable is that over time?

This extends my earlier paper on the gap between being cited and being clicked: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7468658. That paper looked at what happens after a citation. This project looks at what earns one, and at how reliably it can be measured.

## Main results so far

Three runs of the same 84 queries (2026-09-28, 2026-10-02, 2026-10-09), one engine. Treat these as preliminary.

- **Per-query citations are unstable.** The overlap between cited domains for the same query was low: mean Jaccard 0.36 for runs 4 days apart, 0.33 for 7 days, and 0.28 for 11 days. For some queries, two runs shared no cited domains at all.
- **Aggregates are more stable, with limits.** Nine domains appear in the top 15 most-cited domains in all three runs, and the overall standard-query cite rate stays within 2 points (0.43 to 0.45). Category-level rates move more, by up to 11 points, so differences between categories are not reported.
- **Live price queries are cited much less.** Cite rate was 0.15 to 0.23 for 8 live price queries (for example "bitcoin price today"), against 0.43 to 0.45 for the other 76. The ranges do not overlap. The sample of live price queries is small.
- **Exchange domains as a group are cited at the baseline rate** (0.45 to 0.46 against a baseline of 0.43 to 0.45).
- **A claim I retracted.** After run 1, Binance looked cited unusually often (0.68). Its rate fell in each later run (0.60, then 0.46) and is at baseline in run 3, so the apparent lead is not supported.
- **Possible lead: a few finance sites.** Fidelity, IG, and Wise were cited in 82 to 95% of the query-domain pairs where they were retrieved, while other finance institutions (PayPal, Robinhood) were not. This rests on about 7 domains and a small number of distinct queries, so it is not a finding yet.

Full notes, including limitations, are in `docs/findings.md`.

## Method

- **Query set:** 84 unbranded crypto and fintech queries in five categories (crypto education, exchanges, trading, fintech, market data). Each is labeled `standard` or `live_price`. Query text came from my own Search Console data, competitor keyword research, autocomplete research, and a seed list, recorded in a `source` column. Only the query text is published, not traffic or volume figures.
- **Engine:** Perplexity Agent API, preset `fast`, web search tool, search context `low`. These settings are held fixed across runs and logged on every row.
- **Data collected:** for each query, every source the search returned (retrieved) and whether the answer text cited it (cited).
- **Cite rate:** the share of (query, domain) pairs where the domain was cited at least once in that answer.
- **Stability:** per-query Jaccard overlap of cited domains between runs, plus overlap of the top 15 domains.
- **Domain types:** the top 60 domains were labeled exchange, price tracker, education or media, finance institution, or other, by each site's main business and before looking at cite rates by type. Domains outside the top 60 are unlabeled.

## Repo layout

- `data/queries.csv`: the query set
- `data/citations.csv`: one row per retrieved source per query per run
- `scrapers/perplexity_scraper.py`: runs the query set and saves results
- `analysis/first_look.py`, `second_look.py`: first summaries by category, domain, and query type
- `analysis/stability.py`, `stability_all.py`: run-to-run overlap
- `analysis/pooled.py`: all metrics per run, side by side
- `analysis/list_domains.py`, `apply_domain_labels.py`, `domain_labels.csv`: domain type labeling
- `docs/findings.md`: running notes on results and limitations

## Run it

1. Install: `pip install requests python-dotenv pandas`
2. Put `PERPLEXITY_API_KEY=your-key` in a `.env` file in the repo root
3. Run `python3 scrapers/perplexity_scraper.py` (use `--limit 3` to test)
4. Run the analysis scripts, for example `python3 analysis/pooled.py`

A full run of 84 queries costs roughly $0.13 in API credits. The scraper is resumable within a day. Each calendar day (UTC) counts as one run.

## Limitations

- One engine and one preset, so findings may not carry over to other engines
- Three runs over 11 days, which cannot separate short-term noise from longer drift
- Small counts per category, query type, and domain
- Part of the query set came from exchange keyword data, which may favor exchange domains
- Most cited domains outside the top 60 are unlabeled, so domain type results cover only the labeled share
- One query in run 2 returned 20 sources instead of the usual 10
- Click and traffic data are not included, so this study covers the citation side only

## Status

v0.1. The pipeline works and three runs are complete. Planned next: a larger query set, and possibly a second engine.

## License

MIT