import json, re
from collections import Counter
from pathlib import Path

odd, examples, n_files = Counter(), {}, 0
for f in sorted(Path("data/raw").glob("*.json")):
    resp = json.load(open(f))["response"]
    text = resp.get("output_text") or ""
    if not text:
        for item in resp.get("output", []) or []:
            if item.get("type") == "message":
                for c in item.get("content", []) or []:
                    if isinstance(c, dict) and c.get("text"):
                        text += c["text"] + "\n"
    n_files += 1
    for m in re.findall(r"\[[^\]]*\]", text):
        if not re.fullmatch(r"\[\d+\]", m):
            odd[m] += 1
            examples.setdefault(m, f.name)
    if re.search(r"\]\(https?://", text):
        odd["markdown link"] += 1
        examples.setdefault("markdown link", f.name)
    if not text.strip():
        odd["EMPTY ANSWER"] += 1
        examples.setdefault("EMPTY ANSWER", f.name)

print(f"Scanned {n_files} answers")
if not odd:
    print("Every bracket in every answer is a plain [n] marker.")
else:
    for k, v in odd.most_common():
        print(v, repr(k), "e.g.", examples[k])