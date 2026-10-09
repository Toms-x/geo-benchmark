import pandas as pd

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 20)

df = pd.read_csv("data/citations.csv")
qt = pd.read_csv("data/queries.csv")[["query", "query_type", "category"]]
labels = pd.read_csv("analysis/domain_labels.csv")[["domain", "domain_type"]]
df["cited"] = df["cited_in_answer"].eq("yes")

dq = (df.groupby(["run_id", "query", "domain"]).agg(cited=("cited", "max")).reset_index()
        .merge(qt, on="query", how="left").merge(labels, on="domain", how="left"))
dq["domain_type"] = dq["domain_type"].fillna("unlabeled")

def table(data, by):
    t = data.groupby([by, "run_id"])["cited"].mean().unstack("run_id").round(3)
    t["min"], t["max"] = t.min(axis=1), t.iloc[:, :3].max(axis=1)
    return t

print("Cite rate by query type, per run")
print(table(dq, "query_type"))

std = dq[dq["query_type"] == "standard"]
print("\nCite rate by category (standard queries), per run")
print(table(std, "category"))

print("\nCite rate by domain type (standard queries), per run")
t = table(std, "domain_type")
t["n_pairs_run3"] = std[std["run_id"] == std["run_id"].max()].groupby("domain_type").size()
print(t)

exch = ["binance.com", "kraken.com", "crypto.com", "okx.com", "bybit.com",
        "gate.com", "bitget.com", "coinbase.com", "mexc.com"]
e = std[std["domain"].isin(exch)]
print("\nExchange domains: cite rate per run (standard queries)")
print(table(e, "domain"))
print("\nAll-domain baseline per run:", std.groupby("run_id")["cited"].mean().round(3).to_dict())