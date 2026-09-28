import pandas as pd

df = pd.read_csv("data/citations.csv")
qt = pd.read_csv("data/queries.csv")[["query", "query_type"]]
df = df[df["run_id"] == df["run_id"].max()].merge(qt, on="query", how="left")
df["cited"] = df["cited_in_answer"].eq("yes")

# one row per query and domain: was the domain cited at all in that answer?
dq = (df.groupby(["query", "category", "query_type", "domain"])
        .agg(cited=("cited", "max")).reset_index())

print("Overall domain-level cite rate:", round(dq["cited"].mean(), 3))

print("\nBy query type")
print(dq.groupby("query_type")["cited"].agg(["count", "mean"]).round(3))

std = dq[dq["query_type"] == "standard"]
print("\nBy category, standard queries only")
print(std.groupby("category")["cited"].agg(["count", "mean"]).round(3))

base = std["cited"].mean()
print(f"\nBaseline cite rate (standard queries): {base:.3f}")

exch = ["binance.com", "kraken.com", "crypto.com", "okx.com", "bybit.com",
        "gate.com", "bitget.com", "coinbase.com", "mexc.com"]
rows = []
for dom in exch:
    s = std[std["domain"] == dom]
    if len(s):
        rows.append((dom, len(s), int(s["cited"].sum()), round(s["cited"].mean(), 2)))
print("\nExchange domains vs baseline (standard queries)")
print(pd.DataFrame(rows, columns=["domain", "queries", "cited", "cite_rate"])
      .sort_values("cite_rate").to_string(index=False))