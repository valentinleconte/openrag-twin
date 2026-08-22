# Golden set

A structured evaluation set for the routing agent, replacing "I asked it a
few questions and it seemed fine" with a measured pass rate.

## What it checks

[`golden_set.yaml`](golden_set.yaml) has 17 cases across 6 categories:

| Category | Count | What passing means |
|---|---|---|
| `knowledge` | 10 | Cites a source page that actually supports the claim, and the answer contains the expected fact |
| `ticket_known` | 3 | Returns the correct mock ticket data, with **no** documentation citation |
| `ticket_unknown` | 1 | Honestly reports the ticket doesn't exist, instead of inventing one |
| `mixed` | 1 | A single question needing both tools gets both — ticket data *and* a cited answer |
| `off_topic` | 1 | A non-question ("Hi, how are you?") doesn't force either tool |
| `out_of_corpus` | 1 | A real OpenSearch question the corpus doesn't cover gets an honest "no relevant sources," not a hallucination |

Ground truth (expected source pages, expected ticket data, expected keywords)
is hand-verified against [`opensearch-docs-md/`](../opensearch-docs-md/) and
[`scripts/twin/ticket_status_component.py`](../scripts/twin/ticket_status_component.py) —
nothing here is guessed at.

## Running it

```bash
uv run --with pyyaml python3 eval/run_eval.py --save eval/last_results.json
```

Calls the real `/v1/chat` backend endpoint for each case (the same path the
frontend uses), scores the actual response text, and prints a per-case
pass/fail plus a summary. Exits non-zero if anything fails, so it's usable
as a gate, not just a report. Requires the stack up (`make twin-up`) and
`.orag_apikey` present.

## Latest run

**17/17 (100%)** — see [`last_results.json`](last_results.json) for the full
question/answer/citation record. This is a snapshot from one run, not a
guarantee that stays true forever — LLM output varies slightly between runs,
so re-run it rather than trusting a stale number.

## Why this scoring approach, not a framework like RAGAS

The checks are plain regex/substring matching on the final answer text —
short enough to read end to end, which matters more here than generality.
For a 17-case set demonstrating a specific routing behavior, a framework
built for large, statistically-evaluated RAG pipelines would be more
machinery than the thing being tested.
