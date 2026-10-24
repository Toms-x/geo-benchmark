import argparse
import os
import re
import subprocess
import sys

import numpy as np
import pandas as pd

CITATIONS = "data/citations_confirm2.csv"
QUERIES = "data/queries_confirm2.csv"
LABEL_FILES = ["analysis/domain_labels.csv", "analysis/domain_labels_confirm.csv"]
LABELS_NEW = "analysis/domain_labels_confirm2.csv"
SCRIPT = "analysis/confirm2_analysis.py"
HYPOTHESES = "docs/hypotheses_confirm2.md"
BUILDER = "analysis/build_confirm2_set.py"
RESULTS = "docs/confirmation2_results.txt"

ALLOWED = {"exchange", "price_tracker", "education_media", "finance_institution", "other"}
FINANCE_GROUP = ["fidelity.com", "ig.com", "wise.com", "paypal.com",
                 "stripe.com", "robinhood.com", "investor.gov"]
N_BOOT = 10000
SEED = 20261022
MIN_QUERIES = 15

rng = np.random.default_rng(SEED)
lines = []

CUR = "usd|usdt|usdc|eur|euro|euros|gbp|inr|ngn|naira|cad|canadian|aud|jpy|yen|cny|zar|pkr|ksh|php|pesos|aed|btc|eth|dollars?"
CUR_MAP = {"naira": "ngn", "euro": "eur", "euros": "eur", "canadian": "cad", "yen": "jpy",
           "pesos": "php", "dollar": "usd", "dollars": "usd"}


def say(text=""):
    print(text)
    lines.append(text)


def topic(q):
    """Topic of a live_price query: unordered currency pair, or entity plus price or market stat."""
    cur = [CUR_MAP.get(m, m) for m in re.findall(rf"\b({CUR})\b", q)]
    cur = sorted(set(cur))
    if len(cur) >= 2:
        return "pair:" + "-".join(cur[:2])
    toks = set(re.findall(r"[a-z0-9]+", q))
    for name, words in [("bitcoin", {"bitcoin", "btc"}), ("ethereum", {"ethereum", "eth"}),
                        ("xrp", {"xrp"}), ("solana", {"solana", "sol"}),
                        ("usdt", {"usdt", "tether", "trc20"}), ("stablecoin", {"stablecoin", "stablecoins"}),
                        ("crypto", {"crypto", "cryptocurrency", "cryptocurrencies"})]:
        if toks & words:
            entity = name
            break
    else:
        entity = "other"
    return f"{entity}|{'price' if 'price' in toks else 'market'}"


def read_labels(path):
    if not os.path.exists(path):
        return {}
    d = pd.read_csv(path)
    d = d[d["domain_type"].notna() & (d["domain_type"].astype(str).str.strip() != "")]
    bad = set(d["domain_type"]) - ALLOWED
    if bad:
        sys.exit(f"Unknown domain_type in {path}: {sorted(bad)}. Allowed: {sorted(ALLOWED)}")
    return dict(zip(d["domain"], d["domain_type"]))


def load_and_check():
    for p in (CITATIONS, QUERIES, *LABEL_FILES):
        if not os.path.exists(p):
            sys.exit(f"Missing {p}. Run this from the repo root.")
    raw = pd.read_csv(CITATIONS)
    q = pd.read_csv(QUERIES)[["query", "query_type"]]
    runs = sorted(raw["run_id"].unique())
    if len(runs) != 2:
        sys.exit(f"Expected exactly 2 runs, found {len(runs)}: {runs}")
    gap_days = (pd.Timestamp(runs[1]) - pd.Timestamp(runs[0])).days
    if gap_days < 3:
        sys.exit(f"The runs are only {gap_days} days apart. The plan requires at least 3.")
    for r in runs:
        missing = set(q["query"]) - set(raw.loc[raw["run_id"] == r, "query"])
        if missing:
            sys.exit(f"Run {r} is missing {len(missing)} queries. Rerun the scraper to finish it.")
    return raw, q, runs, gap_days


def build_pairs(raw, q):
    df = raw[raw["domain"].notna() & (raw["domain"].astype(str) != "")].copy()
    df["cited"] = df["cited_in_answer"].eq("yes")
    pairs = df.groupby(["run_id", "query", "domain"])["cited"].max().reset_index()
    return pairs.merge(q, on="query", how="left")


def check_git_clean():
    paths = [SCRIPT, HYPOTHESES, BUILDER, CITATIONS, QUERIES, *LABEL_FILES, LABELS_NEW]
    try:
        out = subprocess.run(["git", "status", "--porcelain", "--"] + paths,
                             capture_output=True, text=True, check=True).stdout
    except Exception:
        print("Warning: could not run git, skipping the committed-files check.")
        return
    if out.strip():
        print("These files have uncommitted changes. Commit them before running the tests:")
        print(out)
        sys.exit(1)


def per_query(pr, queries):
    g = pr.groupby("query")["cited"].agg(["sum", "size"]).reindex(queries).fillna(0)
    return g["sum"].to_numpy(float), g["size"].to_numpy(float)


def pct(d):
    d = d[~np.isnan(d)]
    if len(d) < 100:
        return float("nan"), float("nan")
    lo, hi = np.percentile(d, [2.5, 97.5])
    return float(lo), float(hi)


def group_vs_baseline(pairs, std_q, run, domains):
    pr = pairs[(pairs["run_id"] == run) & pairs["query"].isin(std_q)]
    gn, gd = per_query(pr[pr["domain"].isin(domains)], std_q)
    bn, bd = per_query(pr, std_q)
    g_rate = gn.sum() / gd.sum() if gd.sum() else float("nan")
    b_rate = bn.sum() / bd.sum()
    n = len(std_q)
    idx = rng.integers(0, n, size=(N_BOOT, n))
    with np.errstate(divide="ignore", invalid="ignore"):
        d = gn[idx].sum(1) / gd[idx].sum(1) - bn[idx].sum(1) / bd[idx].sum(1)
    lo, hi = pct(d)
    return dict(n_q=int((gd > 0).sum()), group=g_rate, base=b_rate, gap=g_rate - b_rate, lo=lo, hi=hi)


def line(run, r):
    return (f"  {run}: group {r['group']:.3f} in {r['n_q']} queries, baseline {r['base']:.3f}, "
            f"gap {r['gap']:+.3f}, 95% interval [{r['lo']:+.3f}, {r['hi']:+.3f}]")


def test_h1(pairs, q, runs):
    std_q = q.loc[q["query_type"] == "standard", "query"].tolist()
    live_q = q.loc[q["query_type"] == "live_price", "query"].tolist()
    topics = pd.Series({qq: topic(qq) for qq in live_q})
    say("H1. Live price vs standard. Need gap >= 0.15 and interval above 0, in each run. "
        "Live queries are resampled by topic.")
    say(f"  {len(live_q)} live queries in {topics.nunique()} topics: " + ", ".join(sorted(topics.unique())))
    oks = []
    for run in runs:
        pr = pairs[(pairs["run_id"] == run)]
        sn, sd = per_query(pr, std_q)
        ln, ld = per_query(pr, live_q)
        s_rate, l_rate = sn.sum() / sd.sum(), ln.sum() / ld.sum()
        tn = np.array([ln[[i for i, qq in enumerate(live_q) if topics[qq] == t]].sum() for t in topics.unique()])
        td = np.array([ld[[i for i, qq in enumerate(live_q) if topics[qq] == t]].sum() for t in topics.unique()])
        i1 = rng.integers(0, len(std_q), size=(N_BOOT, len(std_q)))
        i2 = rng.integers(0, len(tn), size=(N_BOOT, len(tn)))
        with np.errstate(divide="ignore", invalid="ignore"):
            d = sn[i1].sum(1) / sd[i1].sum(1) - tn[i2].sum(1) / td[i2].sum(1)
        lo, hi = pct(d)
        gap = s_rate - l_rate
        ok = gap >= 0.15 and lo > 0
        oks.append(ok)
        say(f"  {run}: standard {s_rate:.3f} ({len(std_q)} queries), live_price {l_rate:.3f} "
            f"({len(live_q)} queries), gap {gap:+.3f}, 95% interval [{lo:+.3f}, {hi:+.3f}] "
            f"-> {'pass' if ok else 'fail'}")
    return "SUPPORTED" if all(oks) else "NOT SUPPORTED"


def test_group(name, text, domains, min_gap, pairs, std_q, runs, judge_min=False, per_domain=False):
    say(f"{name}. {text}")
    rs = {run: group_vs_baseline(pairs, std_q, run, domains) for run in runs}
    for run in runs:
        say(line(run, rs[run]))
        if per_domain:
            pr = pairs[(pairs["run_id"] == run) & pairs["query"].isin(std_q)]
            for d in domains:
                s = pr[pr["domain"] == d]
                rate = f"{s['cited'].mean():.2f}" if len(s) else "n/a"
                say(f"      {d}: retrieved in {len(s)} queries, cited in {int(s['cited'].sum())}, rate {rate}")
    if judge_min and not all(rs[run]["n_q"] >= MIN_QUERIES for run in runs):
        return "UNTESTED (appears in fewer than 15 queries in at least one run)"
    ok = all(rs[run]["gap"] >= min_gap and rs[run]["lo"] > 0 for run in runs)
    return "SUPPORTED" if ok else "NOT SUPPORTED"


def test_h4(pairs, q, runs):
    cs = {r: pairs[(pairs["run_id"] == r) & pairs["cited"]].groupby("query")["domain"]
          .apply(set).to_dict() for r in runs}

    def jaccards(qs):
        vals = []
        for qq in qs:
            a, b = cs[runs[0]].get(qq, set()), cs[runs[1]].get(qq, set())
            u = a | b
            if u:
                vals.append(len(a & b) / len(u))
        return np.array(vals)

    def boot_mean(v):
        idx = rng.integers(0, len(v), size=(N_BOOT, len(v)))
        return pct(v[idx].mean(1))

    std_q = q.loc[q["query_type"] == "standard", "query"].tolist()
    v_std, v_all = jaccards(std_q), jaccards(q["query"].tolist())
    lo, hi = boot_mean(v_std)
    lo_a, hi_a = boot_mean(v_all)
    say("H4. Mean per-query Jaccard overlap between the two runs, standard queries, "
        "below 0.5 with the interval's upper end also below 0.5.")
    say(f"  standard queries: mean {v_std.mean():.3f} over {len(v_std)} queries, 95% interval [{lo:.3f}, {hi:.3f}]")
    say(f"  all queries (reported only): mean {v_all.mean():.3f} over {len(v_all)} queries, "
        f"95% interval [{lo_a:.3f}, {hi_a:.3f}]")
    return "SUPPORTED" if (v_std.mean() < 0.5 and hi < 0.5) else "NOT SUPPORTED"


def test_h5(pairs, runs):
    def top15(run):
        c = (pairs[(pairs["run_id"] == run) & pairs["cited"]]
             .groupby("domain")["query"].nunique().sort_values(ascending=False))
        cutoff = c.iloc[14] if len(c) >= 15 else c.min()
        return set(c[c >= cutoff].index)

    a, b = top15(runs[0]), top15(runs[1])
    say("H5. At least 8 of the top 15 cited domains are shared between the runs "
        "(all queries, ties at 15th place included).")
    say(f"  {runs[0]}: {len(a)} domains in the top group. {runs[1]}: {len(b)} domains.")
    say(f"  shared: {len(a & b)}")
    say(f"  only in {runs[0]}: {sorted(a - b)}")
    say(f"  only in {runs[1]}: {sorted(b - a)}")
    return "SUPPORTED" if len(a & b) >= 8 else "NOT SUPPORTED"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list-new-domains", action="store_true")
    args = ap.parse_args()

    raw, q, runs, gap_days = load_and_check()
    pairs = build_pairs(raw, q)
    labels = {}
    for p in LABEL_FILES:
        labels.update(read_labels(p))
    new = read_labels(LABELS_NEW)
    labels.update(new)
    n_q = pairs.groupby("domain")["query"].nunique()
    need = sorted(d for d in n_q[n_q >= 3].index if d not in labels)

    if args.list_new_domains:
        rows = list(new.items()) + [(d, "") for d in need]
        pd.DataFrame(rows, columns=["domain", "domain_type"]).sort_values("domain").to_csv(LABELS_NEW, index=False)
        print(f"{len(need)} domains appear in 3 or more queries and have no label.")
        print(f"Open {LABELS_NEW} and fill in domain_type for each, using only: {sorted(ALLOWED)}")
        print("Label by the site's main business, from the domain name alone. Cite counts are not shown.")
        print("Then commit the file before running the tests.")
        for d in need:
            print("  ", d)
        return

    if need:
        sys.exit(f"{len(need)} domains in 3+ queries still need labels. "
                 f"Run with --list-new-domains and fill in {LABELS_NEW} first.")
    check_git_clean()

    std_q = q.loc[q["query_type"] == "standard", "query"].tolist()
    exch = [d for d, t in labels.items() if t == "exchange"]
    say(f"Confirmation 2 runs: {runs[0]} and {runs[1]} ({gap_days} days apart)")
    for col in ("preset", "search_context", "response_model"):
        per = {r: sorted(str(x) for x in raw.loc[raw["run_id"] == r, col].dropna().unique()) for r in runs}
        flag = "" if per[runs[0]] == per[runs[1]] else "   <-- DIFFERENT, report this"
        say(f"  {col}: {per[runs[0]]} vs {per[runs[1]]}{flag}")
    ps = pairs[pairs["query"].isin(std_q)]
    say(f"  share of standard-query pairs on unlabeled domains: {(~ps['domain'].isin(labels)).mean():.2f}")
    say()

    results = []
    for name, fn in [
        ("H1", lambda: test_h1(pairs, q, runs)),
        ("H2", lambda: test_group("H2", "Exchange domains above baseline by >= 0.03 and interval above 0, in each run "
                                        "(standard queries).", exch, 0.03, pairs, std_q, runs)),
        ("H3", lambda: test_group("H3", "Finance group above baseline by >= 0.10 and interval above 0, in each run "
                                        "(standard queries). Judged only if retrieved in >= 15 queries per run.",
                                  FINANCE_GROUP, 0.10, pairs, std_q, runs, judge_min=True, per_domain=True)),
        ("H4", lambda: test_h4(pairs, q, runs)),
        ("H5", lambda: test_h5(pairs, runs)),
        ("H6", lambda: test_group("H6", "kraken.com above baseline by >= 0.10 and interval above 0, in each run "
                                        "(standard queries). Judged only if retrieved in >= 15 queries per run.",
                                  ["kraken.com"], 0.10, pairs, std_q, runs, judge_min=True)),
    ]:
        v = fn()
        results.append((name, v))
        say(f"  RESULT {name}: {v}")
        say()

    say("SUMMARY")
    for name, v in results:
        say(f"  {name}: {v}")
    say("Six tests were run, so some will pass or fail by chance. Report all of them.")
    with open(RESULTS, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\nSaved to {RESULTS}")


if __name__ == "__main__":
    main()