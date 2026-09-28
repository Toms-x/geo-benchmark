import argparse
import csv
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("PERPLEXITY_API_KEY")
API_URL = "https://api.perplexity.ai/v1/agent"
PRESET = "fast"          # keep fixed across runs so weeks are comparable
SEARCH_CONTEXT = "low"   # keep fixed across runs

ROOT = Path(__file__).resolve().parent.parent
QUERIES_FILE = ROOT / "data" / "queries.csv"
RAW_DIR = ROOT / "data" / "raw"
OUT_FILE = ROOT / "data" / "citations.csv"

FIELDS = [
    "run_id", "timestamp", "preset", "search_context", "response_model",
    "query", "category", "intent", "source",
    "position", "result_id", "cited_url", "domain", "title", "cited_in_answer",
    "input_tokens", "output_tokens", "cost",
]


def ask(query):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "preset": PRESET,
        "input": query,
        "tools": [{"type": "web_search", "search_context_size": SEARCH_CONTEXT}],
    }
    for attempt in range(5):
        try:
            resp = requests.post(API_URL, headers=headers, json=body, timeout=120)
        except requests.exceptions.RequestException as e:
            wait = 2 ** (attempt + 1)
            print(f"  network error ({type(e).__name__}), retrying in {wait}s")
            time.sleep(wait)
            continue
        if resp.status_code == 200:
            return resp.json()
        if resp.status_code == 401:
            raise SystemExit("401: API key is wrong or missing. Check your .env file.")
        if resp.status_code == 402:
            raise SystemExit("402: out of credits. Top up in the API portal.")
        if resp.status_code == 429 or resp.status_code >= 500:
            wait = 2 ** (attempt + 1)
            print(f"  status {resp.status_code}, retrying in {wait}s")
            time.sleep(wait)
            continue
        raise SystemExit(f"Unexpected error {resp.status_code}: {resp.text[:500]}")
    return None


def get_answer(data):
    text = data.get("output_text")
    if text:
        return text
    parts = []
    for item in data.get("output", []) or []:
        if item.get("type") == "message":
            for c in item.get("content", []) or []:
                if isinstance(c, dict) and c.get("text"):
                    parts.append(c["text"])
    return "\n".join(parts)


def get_sources(data):
    sources = []
    for item in data.get("output", []) or []:
        if item.get("type") == "search_results":
            sources.extend(item.get("results", []) or [])
    return sources


def already_done(run_id):
    done = set()
    if OUT_FILE.exists():
        with open(OUT_FILE, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row["run_id"] == run_id:
                    done.add(row["query"])
    return done


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None, help="only run the first N queries")
    args = parser.parse_args()

    if not API_KEY:
        raise SystemExit("PERPLEXITY_API_KEY not found. Add it to your .env file.")

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    run_id = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    with open(QUERIES_FILE, newline="", encoding="utf-8") as f:
        queries = list(csv.DictReader(f))
    if args.limit:
        queries = queries[: args.limit]

    done = already_done(run_id)
    write_header = not OUT_FILE.exists()

    with open(OUT_FILE, "a", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(out, fieldnames=FIELDS)
        if write_header:
            writer.writeheader()

        for i, q in enumerate(queries, start=1):
            query = q["query"]
            if query in done:
                print(f"[{i}/{len(queries)}] skip (already done): {query}")
                continue

            print(f"[{i}/{len(queries)}] {query}")
            data = ask(query)
            if data is None:
                print("  failed after retries, moving on")
                continue

            raw_path = RAW_DIR / f"{run_id}_{i:03d}.json"
            raw_path.write_text(
                json.dumps({"query": query, "response": data}, indent=2),
                encoding="utf-8",
            )

            answer = get_answer(data)
            sources = get_sources(data)
            cited_ids = set(re.findall(r"\[(?:[a-z]+:)?(\d+)\]", answer))

            usage = data.get("usage", {}) or {}
            cost = usage.get("cost")
            if isinstance(cost, dict):
                cost = cost.get("total_cost")

            base = {
                "run_id": run_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "preset": PRESET,
                "search_context": SEARCH_CONTEXT,
                "response_model": data.get("model", ""),
                "query": query,
                "category": q.get("category", ""),
                "intent": q.get("intent", ""),
                "source": q.get("source", ""),
                "input_tokens": usage.get("input_tokens", usage.get("prompt_tokens", "")),
                "output_tokens": usage.get("output_tokens", usage.get("completion_tokens", "")),
                "cost": cost if cost is not None else "",
            }

            if not sources:
                writer.writerow({**base, "position": 0, "result_id": "", "cited_url": "",
                                 "domain": "", "title": "", "cited_in_answer": ""})
            n_cited = 0
            for pos, r in enumerate(sources, start=1):
                rid = str(r.get("id", pos))
                url = r.get("url", "") or ""
                cited = rid in cited_ids
                n_cited += cited
                writer.writerow({
                    **base,
                    "position": pos,
                    "result_id": rid,
                    "cited_url": url,
                    "domain": urlparse(url).netloc.replace("www.", ""),
                    "title": r.get("title", ""),
                    "cited_in_answer": "yes" if cited else "no",
                })
            out.flush()
            print(f"  {len(sources)} sources, {n_cited} cited in the answer")
            time.sleep(1)

    print(f"Done. Results in {OUT_FILE}")


if __name__ == "__main__":
    main()