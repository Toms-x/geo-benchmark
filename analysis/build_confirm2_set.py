import csv
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

SEED = 20261022
N_STANDARD_PER_CATEGORY = 16 + 16      # 16 from each source where available
N_LIVE = 40
LIVE_QUOTAS = {"price": 20, "conversion": 10, "other": 10}
CAP_STANDARD_PER_SEED = 10
CAP_LIVE_PER_SEED = 12

PAA = "data/raw_suggestions/kpu_paa_2026-10-22.csv"
AUTO = "data/raw_suggestions/kpu_autocomplete_2026-10-22.csv"
SEEDS = "data/raw_suggestions/seeds.csv"
EARLIER = ["data/queries.csv", "data/queries_confirm.csv"]
OUT = "data/queries_confirm2.csv"
REPORT = "data/confirm2_build_report.txt"

BRANDS = """binance coinbase kraken okx bybit bitget kucoin gemini bitstamp mexc htx huobi bitfinex
robinhood paypal venmo cashapp revolut wise stripe chase citi citibank amex fidelity schwab vanguard
etrade webull metamask phantom ledger trezor exodus zelle apple google samsung uniswap opensea
blackrock grayscale microstrategy saylor trump musk elon paxos wealthfront betterment sofi chime
monzo n26 nubank skrill payoneer remitly moneygram flutterwave paystack opay palmpay kuda moniepoint
alipay wechat paytm phonepe gcash mpesa klarna affirm afterpay tradingview coingecko coinmarketcap
yahoo investopedia reddit quora youtube tiktok twitter amazon walmart tesla nvidia microsoft facebook
""".split()
BRANDS_MULTI = ["cash app", "wells fargo", "bank of america", "capital one", "american express",
                "interactive brokers", "trust wallet", "crypto.com", "apple pay", "google pay",
                "western union", "m-pesa", "binance.us", "x.com"]
PLACES = """india indian russia russian pakistan nigeria nigerian uk usa canada canadian australia
philippines kenya ghana uae dubai turkey brazil germany france spain japan china singapore malaysia
indonesia vietnam europe european""".split()
PLACES_MULTI = ["south africa", "united states", "united kingdom", "near me", "new york", "hong kong"]

RE_ADVICE = re.compile(
    r"\b(should (i|you)|shall i|do i (buy|sell|invest)|good (time|investment)|worth (buying|investing|it)|"
    r"is it (smart|worth|good|safe) to (buy|invest|sell)|best (crypto|coin|coins|altcoin|altcoins) to|"
    r"which (crypto|cryptos|coin|coins|altcoin|altcoins|token|tokens|bitcoin)|what (crypto|coin|coins|altcoin) (will|to)|"
    r"to buy (now|today)|to invest in|next (bitcoin|ethereum|crypto|bull run)|100x|1000x|"
    r"how much will|how high|how low|\bexpected\b|in the future|future price|going forward|what will .* (be|worth)|price (prediction|predictions|forecast|target|targets|outlook)|"
    r"(prediction|predictions|forecast|forecasts|projection|projections|outlook)\b)")
RE_MODAL_MOVE = re.compile(
    r"\b(will|going to|gonna|is .* going|are .* going)\b.*\b(go up|go down|going up|going down|drop|fall|rise|increase|crash|"
    r"recover|rebound|pump|moon|explode|reach|hit|surge|rally|bounce|double|tank|collapse|die|dead|zero)\b")
RE_GOING = re.compile(
    r"(\bwhere (will|is|are) .*\b(go|going)\b|\bprice (go|going)\b|\bwhat price (to )?(buy|sell)\b|"
    r"\bwhen (will|is|are) .*\b(go|going|increase|rise|drop|fall|crash|moon)\b)")
RE_NEWS_OR_OPINION = re.compile(
    r"(^why\b.*\b(crash|crashing|crashed|falling|dropping|dropped|rising|pumping|down|up|surging|tanking|dumping|red|green|drop|drops|dip|dipping|plunge|plunging|jump|jumping|increase|increasing|decreasing|moving)\b|"
    r"\bwhen (will|would)\b|\b(better to|best time to|right time to|time to (buy|sell))\b|"
    r"\b(make you rich|get rich|make money|lose money|millionaire)\b|\bor (bitcoin|ethereum|eth|btc|solana|xrp)\b|"
    r"\b(good|best|safe|smart|worth) (long.term |short.term )?(investment|buy|buying)\b|"
    r"\b(sell or hold|hold or sell|buy or sell|sell or buy)\b|\b(when|what|which|where) to (buy|sell|invest)\b|"
    r"\bwill\b.*\b(bull|bear|bullish|bearish)\b)")
RE_CAN_MOVE = re.compile(r"\b(can|could)\b.*\b(go up|go down|reach|hit|double|moon|explode|go to zero|crash|drop|fall|rise|rebound|recover)\b")
RE_SCENARIO = re.compile(r"(what if (i|you)|if i (invest|invested|bought|buy)|if you (invest|invested|bought)|\$\s?\d)")
RE_YEAR = re.compile(r"\b(19|20)\d\d\b")

HIST_OR_ANALYSIS = re.compile(
    r"\b(affect|affects|affecting|history|historical|chart|charts|started|start|ath|all time|record|ever|explain|mean|means|"
    r"action|discovery|oracle|feed|impact|floor|ceiling|stability|calculator|decided|decide|follow|follows|determined|determine|"
    r"calculated|set|correlation|correlated|compare|vs|versus|buy|sell|where to|highest|lowest)\b")
CUR = "usd|usdt|usdc|eur|euro|euros|gbp|inr|ngn|naira|cad|canadian|aud|jpy|yen|cny|zar|pkr|ksh|php|pesos|aed|btc|eth|dollars?"
RE_CONVERSION = re.compile(rf"\b({CUR})\s+(to|in)\s+({CUR})\b")
RE_EXPLAIN_START = re.compile(r"^(why|should|will|does|do|did|is|are|was|were)\b")
RE_ASK_START = re.compile(r"^(how|when|which|can|could|would|where|who)\b")
RE_NOW = re.compile(r"\b(now|today|right now)\b")
RE_DATA_WORD = re.compile(r"\b(price|prices|rate|rates|market|cap|volume|news|gainers|losers|dominance|index|fear|greed|open|trading at)\b")


CRYPTO_ANCHORS = set("""crypto cryptocurrency cryptocurrencies cryptos bitcoin btc ethereum eth ether usdt usdc tether stablecoin
stablecoins token tokens blockchain defi xrp solana sol altcoin altcoins nft nfts coin coins memecoin memecoins dogecoin
exchange exchanges wallet wallets futures perpetual perpetuals""".split())
FIN_ANCHORS = set("""bank banks banking account accounts credit card cards loan loans savings invest investing investment investments
etf etfs payment payments pay send sending money transfer transfers tax taxes interest apy debit fund funds stock stocks wire
remittance wallet fee fees borrow mortgage currency dollars abroad finance financial""".split())


def has_anchor(q, category):
    toks = set(re.findall(r"[a-z0-9]+", q))
    return bool(toks & (FIN_ANCHORS if category == "fintech" else CRYPTO_ANCHORS))


def norm(t):
    t = str(t).replace("\u2019", "'").replace("\u2018", "'")
    t = re.sub(r"\s+", " ", t.strip().lower())
    return re.sub(r"[?!.]+$", "", t).strip()


def template(t):
    return re.sub(r"\d+", "#", t)


def live_kind(q):
    """Fixed rule for live_price. The answer must be a number or status that changes within a day:
    spot prices, exchange rates, live market stats. Explanations, how-tos and opinions are standard."""
    if RE_YEAR.search(q) or RE_EXPLAIN_START.match(q) or "interest" in q:
        return None
    if RE_CONVERSION.search(q) or "exchange rate" in q:
        return "conversion"
    if RE_ASK_START.match(q) and not RE_NOW.search(q):
        return None
    if re.search(r"\b(price|prices)\b", q) and not HIST_OR_ANALYSIS.search(q):
        if re.search(r"\b(current|currently|now|today|live|usd|dollars?)\b|price of", q) or \
           re.fullmatch(r"(what('s| is)? )?(the )?[a-z ]{2,20} price", q):
            return "price"
    if re.search(r"\bmarket cap\b", q) and not HIST_OR_ANALYSIS.search(q):
        return "other"
    if re.search(r"\b(today|right now|currently|live)\b", q) and RE_DATA_WORD.search(q):
        return "other"
    return None


def drop_reason(q, source):
    words = q.split()
    if len(words) < (3 if source == "kpu_paa" else 4):
        return "too short"
    if len(words) > 12:
        return "too long"
    if not all(ord(c) < 128 for c in q):
        return "non-ascii"
    toks = set(re.findall(r"[a-z0-9.]+", q))
    if toks & set(BRANDS) or any(m in q for m in BRANDS_MULTI):
        return "brand"
    if toks & set(PLACES) or any(m in q for m in PLACES_MULTI):
        return "place or forum"
    if RE_SCENARIO.search(q):
        return "personal scenario"
    years = [int(y.group()) for y in RE_YEAR.finditer(q)]
    if any(y > 2026 for y in years):
        return "future year"
    if RE_ADVICE.search(q) or RE_MODAL_MOVE.search(q) or RE_CAN_MOVE.search(q) or RE_GOING.search(q) or RE_NEWS_OR_OPINION.search(q):
        return "advice or prediction"
    return None


def read_paa(path, seed_cat):
    rows = list(csv.reader(open(path, encoding="utf-8-sig", newline="")))[1:]
    known = defaultdict(set)
    for r in rows:
        if len(r) == 6:
            known[r[0]].add(r[1].strip())
    out, unresolved = [], 0
    for r in rows:
        seed = r[0].strip()
        if len(r) == 6:
            q1, q2 = r[1], r[2]
        else:  # unquoted commas inside the question text
            mid = ",".join(r[1:-3])
            q1 = q2 = None
            for k in sorted(known[seed], key=len, reverse=True):
                if mid.startswith(k + ","):
                    q1, q2 = k, mid[len(k) + 1:]
                    break
            if q1 is None:
                unresolved += 1
                continue
        for q in (q1, q2):
            if q and q.strip():
                out.append((seed, q, "kpu_paa"))
    return out, unresolved


def read_auto(path):
    df = pd.read_csv(path, encoding="utf-8-sig")
    return [(str(r.Query).strip(), str(r.Suggestion), "kpu_autocomplete") for r in df.itertuples()]


def draw(items, n, cap, taken):
    got = []
    for it in items:
        if len(got) >= n:
            break
        if taken[it["seed"]] < cap:
            taken[it["seed"]] += 1
            got.append(it)
    return got


def main():
    for p in [PAA, AUTO, SEEDS] + EARLIER:
        if not Path(p).exists():
            sys.exit(f"Missing {p}. Run from the repo root and use the file names listed at the top of this script.")
    lines = []

    def say(s=""):
        print(s)
        lines.append(s)

    seeds = pd.read_csv(SEEDS)
    seed_cat = dict(zip(seeds["seed"].str.strip(), seeds["category"].str.strip()))
    earlier = set()
    for p in EARLIER:
        earlier |= {norm(q) for q in pd.read_csv(p)["query"]}

    paa, unresolved = read_paa(PAA, seed_cat)
    auto = read_auto(AUTO)
    raw = sorted(paa + auto, key=lambda x: (x[2], x[0], x[1]))
    unknown = {s for s, _, _ in raw if s not in seed_cat}
    if unknown:
        sys.exit(f"Seeds not in seeds.csv: {sorted(unknown)}")
    say(f"Raw rows: {len(paa)} People Also Ask, {len(auto)} autocomplete. Unresolved malformed rows: {unresolved}")

    rng = random.Random(SEED)
    rng.shuffle(raw)

    drops, brand_hits = Counter(), Counter()
    seen_text, seen_tmpl, pool = set(), set(), []
    for seed, text, source in raw:
        q = norm(text)
        reason = drop_reason(q, source)
        kind = live_kind(q) if reason is None else None
        if reason is None and kind != "conversion" and not has_anchor(q, seed_cat[seed]):
            reason = "off-topic (no anchor term)"
        if reason is None and q in earlier:
            reason = "already in an earlier query set"
        if reason is None and q in seen_text:
            reason = "duplicate (repeats and cross-seed)"
        if reason is None and (seed, template(q)) in seen_tmpl:
            reason = "near-duplicate template"
        if reason == "brand":
            for t in set(re.findall(r"[a-z0-9.]+", q)) & set(BRANDS):
                brand_hits[t] += 1
        if reason:
            drops[(source, reason)] += 1
            continue
        seen_text.add(q)
        seen_tmpl.add((seed, template(q)))
        pool.append(dict(query=q, seed=seed, category=seed_cat[seed], source=source,
                         query_type="live_price" if kind else "standard", kind=kind))

    say("\nDropped, by source and rule:")
    for (s, r), n in sorted(drops.items()):
        say(f"  {s:18s} {r:34s} {n}")
    say("Most frequent brand terms removed: " + ", ".join(f"{t} ({n})" for t, n in brand_hits.most_common(15)))

    std = [p for p in pool if p["query_type"] == "standard"]
    live = [p for p in pool if p["query_type"] == "live_price"]
    say(f"\nPool after rules: {len(pool)} ({len(std)} standard, {len(live)} live_price)")
    pc = Counter((p["category"], p["source"]) for p in std)
    for c in sorted(set(seed_cat.values())):
        say(f"  {c:18s} paa {pc[(c, 'kpu_paa')]:4d} | autocomplete {pc[(c, 'kpu_autocomplete')]:4d}")
    say("  live_price pool by kind: " + str(dict(Counter(p["kind"] for p in live))))

    chosen, shortfalls = [], []
    for c in sorted(set(seed_cat.values())):
        taken = Counter()
        pa = [p for p in std if p["category"] == c and p["source"] == "kpu_paa"]
        au = [p for p in std if p["category"] == c and p["source"] == "kpu_autocomplete"]
        half = N_STANDARD_PER_CATEGORY // 2
        got = draw(pa, half, CAP_STANDARD_PER_SEED, taken) + draw(au, half, CAP_STANDARD_PER_SEED, taken)
        if len(got) < N_STANDARD_PER_CATEGORY:
            used = {g["query"] for g in got}
            rest = [p for p in pa + au if p["query"] not in used]
            rng.shuffle(rest)
            got += draw(rest, N_STANDARD_PER_CATEGORY - len(got), CAP_STANDARD_PER_SEED, taken)
        if len(got) < N_STANDARD_PER_CATEGORY:
            shortfalls.append(f"{c}: {len(got)} of {N_STANDARD_PER_CATEGORY}")
        chosen += got

    taken, got = Counter(), []
    for kind, n in LIVE_QUOTAS.items():
        got += draw([p for p in live if p["kind"] == kind], n, CAP_LIVE_PER_SEED, taken)
    if len(got) < N_LIVE:
        used = {g["query"] for g in got}
        rest = [p for p in live if p["query"] not in used]
        got += draw(rest, N_LIVE - len(got), CAP_LIVE_PER_SEED, taken)
    if len(got) < N_LIVE:
        shortfalls.append(f"live_price: {len(got)} of {N_LIVE}")
    chosen += got

    final = pd.DataFrame(chosen)
    final["intent"] = ""
    final = final[["query", "category", "intent", "source", "query_type", "seed"]]
    final.to_csv(OUT, index=False)

    say(f"\nWrote {len(final)} queries to {OUT} (random seed {SEED})")
    say("Shortfalls: " + (", ".join(shortfalls) if shortfalls else "none"))
    say("By category and type:\n" + str(final.groupby(["category", "query_type"]).size()))
    say("By source:\n" + str(final["source"].value_counts()))
    say("By seed (max):\n" + str(final["seed"].value_counts().head(8)))
    say("\nAll live_price queries chosen:")
    for q in final[final.query_type == "live_price"]["query"]:
        say("  " + q)
    with open(REPORT, "w") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()