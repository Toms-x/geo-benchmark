import pandas as pd

df = pd.read_csv("data/citations.csv")
df = df[df["domain"].notna()]  # all runs
df["cited"] = df["cited_in_answer"].eq("yes")

dq = df.groupby(["query", "domain"]).agg(cited=("cited", "max")).reset_index()
d = (dq.groupby("domain")
       .agg(queries_retrieved=("query", "count"), queries_cited=("cited", "sum"))
       .reset_index()
       .sort_values("queries_retrieved", ascending=False)
       .head(60))
d["domain_type"] = ""
d.to_csv("analysis/domain_labels.csv", index=False)
print(d.to_string(index=False))