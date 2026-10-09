import pandas as pd

pd.set_option("display.width", 200)
df = pd.read_csv("data/citations.csv")
qt = pd.read_csv("data/queries.csv")[["query", "query_type", "category"]]
lab = pd.read_csv("analysis/domain_labels.csv")[["domain", "domain_type"]]
df["cited"] = df["cited_in_answer"].eq("yes")

dq = (df.groupby(["run_id", "query", "domain"]).agg(cited=("cited", "max")).reset_index()
        .merge(qt, on="query").merge(lab, on="domain", how="left"))
dq["domain_type"] = dq["domain_type"].fillna("unlabeled")
std = dq[dq["query_type"] == "standard"].copy()
std["fintech_query"] = std["category"].eq("fintech")

print("Cite rate by domain type, split by fintech vs other queries (all runs pooled)")
print(std.groupby(["fintech_query", "domain_type"])["cited"].agg(["count", "mean"]).round(3))

print("\nFinance institutions, by domain")
fi = std[std["domain_type"] == "finance_institution"]
print(fi.groupby("domain")["cited"].agg(["count", "mean"]).round(3))