#!/usr/bin/env python3
"""Run the golden set against the live openrag-twin agent and score it.

Usage:
    uv run --with pyyaml python3 eval/run_eval.py [--save results.json]

Scores each case in eval/golden_set.yaml against the real agent response
(via POST /v1/chat on the backend — the same endpoint the frontend uses, so
this exercises the actual routing/citation behavior, not a mocked shortcut).
Each category has its own pass criteria; see the comment block at the top of
golden_set.yaml for what each one checks and why.

This is intentionally a lightweight, content-based harness (regex/substring
checks on the final answer text), not a framework like RAGAS — the scoring
logic is short enough to read end to end in one sitting, which matters more
here than generality.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
GOLDEN_SET_PATH = REPO_ROOT / "eval" / "golden_set.yaml"
API_KEY_PATH = REPO_ROOT / ".orag_apikey"
CHAT_URL = "http://localhost:3000/api/v1/chat"

SOURCE_LINK_RE = re.compile(r"\[source\]\((https://docs\.opensearch\.org[^\s)]+)\)", re.IGNORECASE)
TICKET_MARKER_RE = re.compile(r"TICKET-\d+", re.IGNORECASE)


def load_api_key() -> str:
    if not API_KEY_PATH.exists():
        sys.exit(
            f"{API_KEY_PATH} not found. Generate a backend API key "
            "(Settings -> API Keys in the UI) and save it there first."
        )
    return API_KEY_PATH.read_text().strip()


def ask(api_key: str, question: str) -> str:
    body = json.dumps({"message": question, "stream": False}).encode()
    req = urllib.request.Request(CHAT_URL, data=body, method="POST")
    req.add_header("X-API-Key", api_key)
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept-Encoding", "identity")
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read())["response"]
    except urllib.error.HTTPError as e:
        return f"__HTTP_ERROR_{e.code}__: {e.read().decode(errors='replace')[:300]}"
    except urllib.error.URLError as e:
        sys.exit(f"Could not reach {CHAT_URL}: {e}\nIs the stack up? Try `make twin-up`.")


def any_kw(text: str, keywords: list[str]) -> bool:
    low = text.lower()
    return any(kw.lower() in low for kw in keywords)


def all_kw(text: str, keywords: list[str]) -> bool:
    low = text.lower()
    return all(kw.lower() in low for kw in keywords)


def cited_sources(text: str) -> list[str]:
    return SOURCE_LINK_RE.findall(text)


def score_case(case: dict[str, Any], response: str) -> tuple[bool, str]:
    category = case["category"]
    sources = cited_sources(response)
    has_ticket_marker = bool(TICKET_MARKER_RE.search(response))

    if category == "knowledge":
        cited_ok = any(any(sub in src for sub in case["expected_source_substrings"]) for src in sources)
        kw_ok = any_kw(response, case["expected_keywords"])
        if not sources:
            return False, "no [source](...) citation found"
        if not cited_ok:
            return False, f"cited {sources}, expected one containing {case['expected_source_substrings']}"
        if not kw_ok:
            return False, f"missing all expected keywords {case['expected_keywords']}"
        return True, f"cited {sources}"

    if category == "ticket_known":
        if sources:
            return False, f"cited docs sources {sources}, should have used the ticket tool instead"
        if not all_kw(response, case["expected_keywords"]):
            return False, f"missing one of {case['expected_keywords']}"
        return True, "ticket data present, no doc citation"

    if category == "ticket_unknown":
        if not any_kw(response, case["expected_keywords"]):
            return False, f"missing a 'not found' style admission {case['expected_keywords']}"
        return True, "correctly reported unknown ticket"

    if category == "mixed":
        ticket_ok = all_kw(response, case["expected_keywords"])
        cited_ok = any(any(sub in src for sub in case["expected_source_substrings"]) for src in sources)
        if not ticket_ok:
            return False, f"missing ticket keywords {case['expected_keywords']}"
        if not cited_ok:
            return False, f"missing expected knowledge citation {case['expected_source_substrings']}"
        return True, f"both tools reflected in the answer, cited {sources}"

    if category == "off_topic":
        if sources or has_ticket_marker:
            return False, "forced a tool on a non-question"
        return True, "answered without forcing a tool"

    if category == "out_of_corpus":
        if not any_kw(response, case["expected_keywords"]):
            return False, f"did not admit the gap; response: {response[:200]!r}"
        return True, "honestly reported no relevant sources"

    return False, f"unknown category {category!r}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--save", type=Path, default=None, help="Save full results as JSON to this path")
    args = parser.parse_args()

    api_key = load_api_key()
    golden_set = yaml.safe_load(GOLDEN_SET_PATH.read_text())
    cases = golden_set["cases"]

    results = []
    by_category: dict[str, list[bool]] = {}

    print(f"Running {len(cases)} cases against {CHAT_URL}\n")

    for case in cases:
        t0 = time.monotonic()
        response = ask(api_key, case["question"])
        elapsed = time.monotonic() - t0
        passed, reason = score_case(case, response)

        by_category.setdefault(case["category"], []).append(passed)
        results.append(
            {
                "id": case["id"],
                "category": case["category"],
                "question": case["question"],
                "passed": passed,
                "reason": reason,
                "response": response,
                "elapsed_s": round(elapsed, 1),
            }
        )

        mark = "PASS" if passed else "FAIL"
        print(f"[{mark}] {case['id']:<12} ({case['category']:<14} {elapsed:>4.1f}s)  {reason}")
        if not passed:
            print(f"         Q: {case['question']}")
            print(f"         A: {response[:220]}{'...' if len(response) > 220 else ''}")

    total = len(results)
    passed_total = sum(r["passed"] for r in results)

    print(f"\n{'=' * 60}")
    print(f"TOTAL: {passed_total}/{total} passed ({100 * passed_total / total:.0f}%)")
    print("By category:")
    for cat, outcomes in by_category.items():
        p = sum(outcomes)
        print(f"  {cat:<14} {p}/{len(outcomes)}")

    if args.save:
        args.save.write_text(json.dumps(results, indent=2))
        print(f"\nFull results saved to {args.save}")

    sys.exit(0 if passed_total == total else 1)


if __name__ == "__main__":
    main()
