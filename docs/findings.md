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
## Confirmation 2 (runs 2026-10-24 and 2026-10-27)
- 200 queries (160 standard, 40 live_price), taken from Google Autocomplete and People Also Ask
  suggestions (KeywordsPeopleUse, en_US, exported 2026-10-22) by analysis/build_confirm2_set.py using
  fixed rules. 114 from autocomplete, 86 from People Also Ask. Query builder, query set, hypotheses
  (docs/hypotheses_confirm2.md) and analysis script were committed before run 1. Same engine, preset
  (fast), search context (low) and reported model (openai/gpt-6-luna). Runs 3 days apart.
- 72 new domains labeled from names only, with counts hidden. The label file was first committed
  unfilled and then filled by the script in that commit, before any test (see Amendments in the
  hypotheses file).
- H1 not supported. Live price vs standard gap +0.128 [+0.070, +0.181] and +0.119 [+0.064, +0.175],
  below the 0.15 threshold. Live 0.213 and 0.217, standard 0.340 and 0.336. 40 live queries in 17 topics.
- H2 not supported. Exchange group +0.012 [-0.057, +0.076] and +0.055 [-0.019, +0.125].
- H3 supported. Finance group +0.213 [+0.063, +0.361] and +0.143 [+0.008, +0.287], in 37 and 38 queries.
  Per domain, run 1 / run 2: fidelity 0.58 / 0.41, wise 0.67 / 1.00, investor.gov 0.75 / 1.00,
  ig 0.60 / 0.33, paypal 0.33 / 0.29, stripe 0.40 / 0.33, robinhood 0.50 / 0.00.
- H4 supported, narrowly. Mean Jaccard overlap 0.454 on standard queries, interval [0.409, 0.499].
  All queries: 0.438 [0.396, 0.482].
- H5 supported. 14 domains shared between the top groups (15 and 18 with ties).
- H6 not supported. Kraken +0.225 [+0.022, +0.430] and +0.104 [-0.086, +0.297], in 23 and 25 queries.
- Result: 3 supported, 3 not supported. Full output in docs/confirmation2_results.txt.
- Share of standard-query pairs on unlabeled domains: 0.36.

## Across stages (descriptive, not pooled in any test)
- Live price gap: 0.20 to 0.29 (exploration), 0.17 to 0.21 (confirmation 1), 0.12 to 0.13
  (confirmation 2). Direction held in all 7 runs. Size depends on the query set.
- Finance institutions above baseline in all 7 runs (type in exploration, fixed group in confirmations).
- Kraken above baseline in all 7 runs. No stage met the pre-specified standard in both runs.
- Exchanges as a group between 0.00 and +0.06 above baseline in all 7 runs. Intervals include zero in
  both confirmation stages.
- Mean Jaccard overlap: 0.28 to 0.36 (exploration), 0.38 (confirmation 1), 0.45 (confirmation 2).
  Below 0.5 in every stage. Days between runs does not explain the differences, because the query sets differ.

## Limitations added by confirmation 2
- Seeds were chosen by the author. Autocomplete and People Also Ask suggestions are not a random sample
  of searches. Autocomplete suggestions often read as fragments.
- The selection rules were tuned after reading samples of the exports and before any engine run.
- A few odd queries remain (for example "where is etf airways from").
- Place names were excluded, which removes country-specific queries.
- Live price queries cover only 17 topics.
- Some answers returned fewer or more than 10 sources (5, 6, 8, 9 and 20 were seen).
- H4 passed by a very small margin (interval upper end 0.499 against a threshold of 0.5).
