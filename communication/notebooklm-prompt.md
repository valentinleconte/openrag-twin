# NotebookLM setup — video pitch for openrag-twin

## 1. Sources to upload

In a new NotebookLM notebook, add these as sources:

1. **`video-pitch-source.md`** (required — this is the primary script NotebookLM should draw from)
2. **`README.md`** (optional, adds detail — the two Mermaid diagrams won't render for NotebookLM, but the surrounding prose about architecture and the classic-vs-agentic comparison is useful extra context)

Do **not** add `CLAUDE.md` — it's a working engineering log, not pitch material, and will pull the tone toward a bug list instead of a pitch.

## 2. Customization prompt

Go to **Studio → Video Overview → Customize**, and paste this:

```
Create a confident, technical pitch video for a software portfolio project,
aimed at a technical interviewer (Field/Client Engineer role at IBM) who
will watch this before or during a job interview.

Target length: 2 to 3 minutes. Tighter is better than padded — cut detail
before you cut clarity.

Structure to follow, in this order:
1. A one-sentence hook: what this project is and why it exists (interview
   prep — a working replica of IBM's own OpenRAG product, not a toy demo).
2. The architecture: name each component (Docling, OpenSearch, Langflow,
   Ollama, Claude) and its one job, briefly. Don't read a component list —
   explain the flow of a request through the system.
3. The core scenario: an agent that DECIDES between two tools — searching
   documentation with citations, or calling a separate tool for live ticket
   status — instead of always retrieving. Make the contrast with a "classic"
   RAG pipeline explicit and concrete: a classic pipeline retrieves for
   every question, including ones retrieval can't answer.
4. One concrete example of engineering depth: the version-skew bug, where
   Langflow components embed their own source code in config files and a
   version mismatch caused invisible runtime failures. Explain it well
   enough that a technical viewer understands the actual failure mode, not
   just that "a bug was fixed."
5. Close on reproducibility and scope: this runs from a cold machine with
   one command, verified end to end, and is deliberately small enough to
   defend every part of it in conversation.

Tone: precise and confident, like an engineer explaining their own work to
a peer — not a marketing narrator, no hype language, no exclamation points
in the narration style, no "revolutionary" or "game-changing." Technical
vocabulary is fine and expected; the audience is technical.

Avoid: reciting file paths or directory names, listing dependency version
numbers, restating the same point in the intro and the conclusion, generic
AI-product-demo phrasing ("in today's fast-paced world of AI...").

If you generate slide visuals, prefer simple architecture/flow diagrams
over walls of bullet text, and keep on-screen text short enough to read in
the time it's shown.
```

## 3. After generating

- Watch it once before publishing. NotebookLM sometimes over-simplifies the
  bug explanation (step 4) — if it does, regenerate with a note added to the
  prompt: *"Give the version-skew bug more technical precision — a viewer
  who works with software should understand exactly what broke."*
- Export the video, upload it (YouTube unlisted is the simplest — GitHub
  READMEs can't embed a video file directly, but a linked thumbnail works).
- To embed it in `README.md`, add near the top:

  ```markdown
  [![Project pitch video](docs/static/img/openrag-logo-dog.svg)](YOUR_VIDEO_URL)
  ```

  Replace the thumbnail image with an actual video thumbnail if you have
  one (a screenshot of the video's first frame works well), and
  `YOUR_VIDEO_URL` with the real link once it's uploaded. Ask me to wire
  this in once you have the URL.
