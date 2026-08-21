# openrag-twin — Video Pitch Source

> This document is written to be read aloud, not skimmed. It is the primary
> source for a NotebookLM Video Overview pitching this project. Upload this
> file (and optionally README.md for extra detail) as a NotebookLM source,
> then use the customization prompt in `docs/notebooklm-prompt.md` when
> generating the video.

## What this project is

openrag-twin is a working, hands-on replica of OpenRAG — IBM's agentic
retrieval-augmented-generation product, built on Langflow, Docling, and
OpenSearch. It was built to prepare for a Field/Client Engineer interview at
IBM: instead of reading about the product, the goal was to run the real
open-source codebase, break it, fix it, and extend it with an original
scenario — the way an engineer would actually work with this stack on the
job, not the way a student studies for an exam.

The project starts from the genuine upstream OpenRAG repository, Apache 2.0
licensed. Everything running is the real product. On top of that foundation
sit three original additions: a real document corpus, a custom agent
behavior, and a one-command reproducible setup.

## The architecture, in plain terms

Four systems work together, each with one clear job.

Docling turns messy real-world documents — web pages, PDFs — into clean,
structured text. OpenSearch stores that text as both vector embeddings and
searchable keywords, and answers hybrid semantic-plus-keyword queries in
milliseconds. Langflow is the orchestration layer: it defines the ingestion
pipeline and the agent's decision logic as a graph of swappable components.
And two more pieces complete the loop: Ollama runs the embedding model
locally, so ingestion has no external cost or dependency, and Claude, from
Anthropic, does the actual reasoning — deciding what to do and writing the
final answer.

All of this runs locally, in Docker, on a single command.

## The scenario: an agent that decides, not just retrieves

Most RAG demonstrations stop at retrieval-then-generation: a question comes
in, the system searches a knowledge base, and answers from what it finds.
That's necessary, but it isn't what makes an *agentic* system interesting.

The scenario built here is a support agent with two completely different
jobs, and no keyword-matching or hard-coded rule decides between them — the
underlying language model reads the question and the tools available to it,
and picks.

Ask it a knowledge question — "what is hybrid search in OpenSearch?" — and
it searches the indexed documentation, answers strictly from what it
retrieves, and cites the exact source page for every claim. Ask it about a
support ticket — "what's the status of ticket 101?" — and it skips the
document search entirely, calls a separate tool that looks up live ticket
data, and returns the actual status: open, in progress, resolved, whatever
it is.

That's the point being proven: retrieval is one tool among several, and a
real agent has to know when *not* to use it. A classic RAG pipeline would
retrieve for the ticket question too, find nothing relevant in the
documentation, and either hallucinate an answer or awkwardly refuse — because
searching documents is the only thing it knows how to do. This agent has a
second option, and the judgment to choose it.

## Evidence of understanding, not just usage

Running someone else's product is easy to fake. Fixing it when it breaks is
not.

Building this surfaced five real bugs in the underlying stack — from a
cosmetic but confusing healthcheck, to a cryptographic key format
requirement that silently broke Langflow's internal encryption, to the most
instructive one: Langflow flows embed each component's Python source code
directly inside their configuration files. The bundled flows had been
exported from a newer version of Langflow than the one actually installed,
so components called functions that didn't exist yet in the running
package — and the failure stayed completely invisible until the moment those
components actually executed, not when the flow merely loaded. That's a
textbook case of a hidden, hard-to-test coupling between a configuration
file and the version of the engine running it — exactly the kind of
production issue a field engineer has to diagnose under pressure, not just
read about.

Every one of these five bugs is documented with its root cause and its fix.

## Built to actually run, every time

The last original piece is reproducibility. Several parts of this stack —
a local embedding server, a native background process, a handful of runtime
configuration values — do not survive a simple restart on their own. A
single command brings all of it back up from a completely cold machine,
reapplies the configuration that would otherwise require manually clicking
through a setup wizard, and runs an automatic smoke test — one knowledge
question, one ticket question — before declaring the system ready. Verified
by actually killing everything and bringing it back up cold, timed at about
two minutes, with zero manual steps in a browser.

## The takeaway

This project demonstrates comprehension of a real agentic RAG stack at every
layer: the retrieval architecture, the orchestration layer, the agent's
decision logic, and the operational reality of running it — including what
breaks and why. It's a small, deliberately scoped project built to be
defended in detail, not a large one built to look impressive from a
distance.
