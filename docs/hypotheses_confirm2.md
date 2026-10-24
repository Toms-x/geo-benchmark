# Pre-specified hypotheses for confirmation 2 (written before any engine run on this set)

## Design
Query set: data/queries_confirm2.csv, frozen at commit 542a1e7. 200 queries, 160 standard
(32 in each of 5 categories) and 40 live_price. Built by analysis/build_confirm2_set.py from
Google Autocomplete and People Also Ask suggestions exported from a third-party tool. No query
was written or chosen by hand. None overlap the earlier sets.
Engine and settings: Perplexity Agent API, preset fast, web_search tool, search context low.
The returned model name is checked in every run and any change is reported.
Exactly two runs, at least 3 days apart (UTC dates). Both runs are used in every test.
A run is repeated only after a technical failure (crash, empty output), never because of its results.
This stage is analyzed separately from the exploration set and from confirmation 1.
Results from other stages are never pooled into the tests below.

## Definitions
Cite rate, cited, baseline, live_price, and domain labels are defined as in docs/hypotheses.md.
Cite rate: the share of (query, domain) pairs where the domain was cited at least once in that answer.
Baseline: the cite rate of all domains on standard queries, in the same run.
live_price: assigned by the rule in analysis/build_confirm2_set.py, from the query text alone.
Uncertainty: 95% intervals from 10,000 resamples with a fixed seed.
  Standard queries are resampled one by one.
  Live price queries are resampled by topic, because many of them ask the same thing in different words.
  The topic of a live query is its currency pair (for conversions), or its entity (bitcoin, ethereum,
  xrp, solana, usdt, stablecoin, crypto) plus whether it asks for a price or a market stat.
Domain labels: domains already in analysis/domain_labels.csv or analysis/domain_labels_confirm.csv keep
their labels. New domains that appear in 3 or more queries are labeled by their main business, from the
domain name alone, with cite counts hidden, in analysis/domain_labels_confirm2.csv. That file is
committed before the tests are run.

## Hypotheses
A hypothesis counts as supported only if its threshold holds for the point estimate in every run and
any extra condition below also holds. All results are reported, including failures. Six tests are run,
so some will pass or fail by chance.

H1. Live price queries have a lower cite rate than standard queries, by at least 0.15, in each run.
    Also required: the 95% interval for the gap excludes zero.
    Basis: supported in confirmation 1 (+0.174 and +0.212).
H2. Exchange domains (domain_type exchange) have a cite rate above baseline by at least 0.03 on
    standard queries, in each run. Also required: the 95% interval for the gap excludes zero.
    Basis: confirmation 1 gave +0.054 and +0.057 with intervals that included zero.
    Exploration found no difference.
H3. Fidelity, IG, Wise, PayPal, Stripe, Robinhood, and investor.gov as a group have a cite rate at least
    0.10 above baseline on standard queries, in each run. Also required: the 95% interval for the gap
    excludes zero. Judged only if the group appears in at least 15 queries per run.
    Basis: confirmation 1 gave +0.139 and +0.130. The threshold is set from that result,
    not from the larger exploration estimate. Per-domain rates are reported alongside.
H4. Mean per-query Jaccard overlap of cited domains between the two runs, on standard queries,
    is below 0.5, and the upper end of its 95% interval is also below 0.5.
    Basis: supported in confirmation 1 (0.380).
H5. At least 8 of the top 15 cited domains in one run are also in the top 15 of the other.
    Top 15 is ranked by number of queries where the domain was cited, using all queries.
    Ties at 15th place are all included.
    Basis: supported in confirmation 1 (11 shared).
H6. Kraken has a cite rate at least 0.10 above baseline on standard queries, in each run.
    Also required: the 95% interval for the gap excludes zero.
    Judged only if Kraken appears in at least 15 queries per run.
    Basis: above baseline in every earlier run, but one run of confirmation 1 missed the threshold.
If a judging condition is not met, the hypothesis is reported as untested.

## Not hypothesized (exploratory only, labeled as such if reported)
OKX, Binance, Coinbase, category differences, price tracker differences, differences between the
Autocomplete and People Also Ask queries, and anything found after the first run.

## Amendments
None yet. Any change after the first run is added here with a date and reason.
The text above is never edited.