import pandas as pd

df = pd.read_csv("data/citations.csv")
df = df[df["run_id"] == df["run_id"].max()]  # latest run only
df["cited"] = df["cited_in_answer"].eq("yes")

per_q = df.groupby(["query", "category"]).agg(
    retrieved=("position", "count"),
    cited=("cited", "sum"),
    cost=("cost", "first"),  # cost repeats on every row, so take it once per query
).reset_index()
per_q["cited_share"] = per_q["cited"] / per_q["retrieved"]

print(f"Queries: {len(per_q)} | total cost: ${per_q['cost'].sum():.3f}")

print("\nBy category")
print(per_q.groupby("category").agg(
    queries=("query", "count"),
    avg_cited=("cited", "mean"),
    avg_share=("cited_share", "mean"),
).round(2))

print("\nTop 15 domains cited (number of queries where the domain was cited)")
top = (df[df["cited"]]
       .drop_duplicates(["query", "domain"])
       .groupby("domain")["query"].count()
       .sort_values(ascending=False).head(15))
print(top)

print("\nRetrieved often but cited rarely (domains retrieved in 5+ queries)")
dq = df.groupby(["query", "domain"]).agg(cited=("cited", "max")).reset_index()
d = dq.groupby("domain").agg(retrieved=("query", "count"), cited=("cited", "sum"))
d = d[d["retrieved"] >= 5]
d["cite_rate"] = (d["cited"] / d["retrieved"]).round(2)
print(d.sort_values("cite_rate").head(10))

print("\nQueries with the fewest citations")
print(per_q.sort_values("cited").head(10)[["query", "category", "cited"]].to_string(index=False))