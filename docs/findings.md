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

## Finance institutions check
- On non-fintech queries, finance institutions were cited at 0.76 (54 pairs, pooled
  over 3 runs, so about 18 distinct pairs). Other domain types: 0.37 to 0.49.
- The effect comes from Fidelity (0.95), IG (0.92), and Wise (0.82). PayPal and
  Robinhood are at 0.33. It is not a type-wide effect.
- Possible explanation, untested: these sites are retrieved only on closely matching
  topics, where they are then cited. Needs a larger query set to test.

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
- Cited is defined as a numbered [n] marker in the answer text. Checked on all 252
  raw answers: no other marker format found. A few answers (halving chart and profit
  calculator queries) also use inline links, which are not counted.
- The 153 confirmation queries were drafted from general knowledge, not
  taken from search data. 39 of 40 randomly sampled standard queries were found in Google
  autocomplete. They may read more like textbook questions than real searches. Confirmation 2
  uses queries from autocomplete and People Also Ask suggestions to address this.
- Only 8 (exploration) and 25 (confirmation) live price queries.

  ## Confirmation 1 (runs 2026-10-11 and 2026-10-15)
- 153 queries (128 standard, 25 live_price), drafted from general
  knowledge. Hypotheses, query set, analysis script and labels were committed before the
  tests were run. Same engine, preset (fast), search context (low) and reported model
  (openai/gpt-6-luna) in both runs, 4 days apart.
- The domain labels file was committed empty first and filled by the script in the same
  commit chain (876664d). No results had been seen at that point.
- H1 supported. Live price vs standard gap +0.174 and +0.212, intervals [+0.125, +0.218]
  and [+0.153, +0.264].
- H2 not supported, imprecise. Exchange group +0.054 and +0.057 above baseline, intervals
  include zero. Cannot be told apart from no difference.
- H3 not supported. Finance group +0.139 and +0.130, below the 0.15 threshold, intervals
  include zero. Fidelity fell from 0.95 in exploration to 0.42 and 0.46.
- H4 supported. Mean Jaccard overlap 0.380 on standard queries, interval [0.340, 0.422].
- H5 supported. 11 domains shared between the two top groups (17 and 15 with ties).
- H6a not supported. Kraken +0.071 in run 1 (interval [-0.132, +0.283]) and +0.250 in run 2
  (interval [+0.033, +0.453]). Both runs had to pass.
- H6b untested. OKX appeared in 7 and 2 standard queries, under the 15 needed.
- Result: 3 supported, 3 not supported, 1 untested. Full output in
  docs/confirmation_results.txt.
- One query in run 2 returned 20 sources instead of about 10.
- Baseline cite rate was lower on these queries (0.38 to 0.40) than in exploration
  (0.43 to 0.45). Cause unknown.
- Unlabeled domains made up 0.34 of standard-query pairs (about 0.59 in exploration).