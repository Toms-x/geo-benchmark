import itertools
import pandas as pd

df = pd.read_csv("data/citations.csv")
df["cited"] = df["cited_in_answer"].eq("yes")
runs = sorted(df["run_id"].unique())
print("Runs:", runs)

def cited_sets(run_id):
    rows = df[(df["run_id"] == run_id) & df["cited"]]
    return rows.groupby("query")["domain"].apply(set).to_dict()

sets = {r: cited_sets(r) for r in runs}
queries = sorted(set(df["query"]))

print("\nPairwise per-query overlap (Jaccard)")
for a, b in itertools.combinations(runs, 2):
    vals = []
    for q in queries:
        sa, sb = sets[a].get(q, set()), sets[b].get(q, set())
        u = sa | sb
        if u:
            vals.append(len(sa & sb) / len(u))
    gap = (pd.Timestamp(b) - pd.Timestamp(a)).days
    print(f"{a} vs {b} ({gap} days apart): mean {sum(vals)/len(vals):.3f}, n={len(vals)}")

print("\nTop-15 cited domains: how many are shared across all runs")
def top(run_id, n=15):
    rows = df[(df["run_id"] == run_id) & df["cited"]].drop_duplicates(["query", "domain"])
    return set(rows.groupby("domain")["query"].count().sort_values(ascending=False).head(n).index)
tops = [top(r) for r in runs]
print("In all runs:", sorted(set.intersection(*tops)))

print("\nDomain cite counts per run (queries where the domain was cited)")
counts = {}
for r in runs:
    rows = df[(df["run_id"] == r) & df["cited"]].drop_duplicates(["query", "domain"])
    counts[r] = rows.groupby("domain")["query"].count()
tab = pd.DataFrame(counts).fillna(0).astype(int)
tab["total"] = tab.sum(axis=1)
print(tab.sort_values("total", ascending=False).head(15))