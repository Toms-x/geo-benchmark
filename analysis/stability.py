import pandas as pd

df = pd.read_csv("data/citations.csv")
df["cited"] = df["cited_in_answer"].eq("yes")
runs = sorted(df["run_id"].unique())
if len(runs) < 2:
    raise SystemExit(f"Only one run found ({runs}). Run the scraper again first.")

r1, r2 = runs[-2], runs[-1]
print(f"Comparing {r1} vs {r2}")

def cited_set(run_id, query):
    rows = df[(df["run_id"] == run_id) & (df["query"] == query)]
    return set(rows.loc[rows["cited"], "domain"])

queries = sorted(set(df["query"]))
overlaps = []
for q in queries:
    a, b = cited_set(r1, q), cited_set(r2, q)
    union = a | b
    jaccard = len(a & b) / len(union) if union else None
    overlaps.append({"query": q, "cited_run1": len(a), "cited_run2": len(b),
                      "shared": len(a & b), "jaccard": jaccard})

ov = pd.DataFrame(overlaps)
print(f"\nMean overlap (Jaccard) across {len(ov)} queries: {ov['jaccard'].mean():.3f}")
print(f"Median: {ov['jaccard'].median():.3f}")

print("\nMost unstable queries (lowest overlap)")
print(ov.sort_values("jaccard").head(10)[["query", "cited_run1", "cited_run2", "shared", "jaccard"]]
      .to_string(index=False))

print("\nMost stable queries (highest overlap)")
print(ov.sort_values("jaccard", ascending=False).head(10)[["query", "cited_run1", "cited_run2", "shared", "jaccard"]]
      .to_string(index=False))

# domain-level: did the same domains stay on top across both runs?
def top_domains(run_id, n=15):
    rows = df[(df["run_id"] == run_id) & df["cited"]]
    return set(rows.drop_duplicates(["query", "domain"]).groupby("domain")["query"]
               .count().sort_values(ascending=False).head(n).index)

t1, t2 = top_domains(r1), top_domains(r2)
print(f"\nTop 15 cited domains, overlap between runs: {len(t1 & t2)} of 15")
print("In run 1 only:", sorted(t1 - t2))
print("In run 2 only:", sorted(t2 - t1))