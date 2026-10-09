# Pre-specified hypotheses (written before the confirmation query set was run)

## Design
Source of hypotheses: exploratory results on the first 84 queries, runs 1 to 3.
Confirmation set: data/queries_confirm.csv, new queries, none from the first 84.
Engine and settings: Perplexity Agent API, preset fast, web_search tool, search context low.
The returned model name is checked in every run and any change is reported.
Exactly two confirmation runs, at least 3 days apart. Both runs are used in every test.
A run is repeated only after a technical failure (crash, empty output), never because
of its results. No run is dropped.
The confirmation set is analyzed separately from the first 84 queries. Exploration and
confirmation results are never pooled for the hypothesis tests.

## Definitions
Cite rate: the share of (query, domain) pairs where the domain was cited at least once
in that answer. Pairs are formed over the domains retrieved for that query.
Cited: a numbered [n] marker in the answer text points to a source from that domain.
Baseline: the cite rate of all domains on standard queries, in the same run.
live_price: a query whose correct answer changes within a day (spot prices, exchange
rates, live market stats). Assigned from the query text alone and frozen at commit.
Uncertainty: 95% intervals from resampling queries with replacement (10,000 draws),
not pairs. Pairs from the same answer are not independent.
Domain labels: domains in data/domain_labels.csv keep their labels. New domains that
appear in 3 or more queries are labeled by main business with cite counts hidden, and the
labels are committed before the analysis script is run.

## Hypotheses
A hypothesis counts as supported only if its threshold holds for the point estimate in
every confirmation run and the extra condition below, where given, also holds.
All results are reported, including failures. Seven tests are run, so some will pass or
fail by chance.

H1. Live price queries have a lower cite rate than standard queries, by at least 0.15,
    in each run. Also required: the 95% interval for the gap excludes zero.
H2. Exchange domains (domain_type exchange) are within 0.05 of the baseline, in each run.
    The interval is reported. A miss with a wide interval is reported as imprecise,
    not as evidence against.
H3. Fidelity, IG, Wise, PayPal, Stripe, Robinhood, and investor.gov as a group have a cite
    rate at least 0.15 above baseline, in each run, judged only if the group appears in at
    least 15 queries per run. Also required: the 95% interval for the gap excludes zero.
    Per-domain rates are reported alongside.
H4. Mean per-query Jaccard overlap of cited domains between the two runs, on standard
    queries only, is below 0.5, and the upper end of its 95% interval is also below 0.5.
    The all-query figure is reported too.
H5. At least 8 of the top 15 cited domains in one run are also in the top 15 of the other.
    Top 15 is ranked by number of queries where the domain was cited. Ties at 15th place
    are all included.
H6a. Kraken is at least 0.10 above baseline, in each run, judged only if Kraken appears in
     at least 15 queries per run. Also required: the 95% interval for the gap excludes zero.
H6b. OKX is at least 0.05 below baseline, in each run, judged only if OKX appears in at
     least 15 queries per run. Also required: the 95% interval for the gap excludes zero.
If a judging condition is not met, the hypothesis is reported as untested.

## Not hypothesized (exploratory only, labeled as exploratory if reported)
Category differences, Binance, Coinbase, price tracker differences, and anything else
found after the first confirmation run.

## Amendments
None yet.