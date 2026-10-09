import json, random, re
from pathlib import Path

files = sorted(Path("data/raw").glob("*.json"))
random.seed(1)
for f in random.sample(files, 8):
    d = json.load(open(f))
    resp = d["response"]
    text = resp.get("output_text") or ""
    if not text:
        for item in resp.get("output", []) or []:
            if item.get("type") == "message":
                for c in item.get("content", []) or []:
                    if isinstance(c, dict) and c.get("text"):
                        text += c["text"] + "\n"
    sources = []
    for item in resp.get("output", []) or []:
        if item.get("type") == "search_results":
            sources += item.get("results", []) or []
    ids = set(re.findall(r"\[(?:[a-z]+:)?(\d+)\]", text))
    print("=" * 80)
    print(f.name, "|", d["query"])
    print(text[:1500])
    print("\nParser says cited ids:", sorted(ids, key=int))
    for r in sources:
        print(r.get("id"), r.get("url"))