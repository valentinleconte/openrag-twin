# Engineering log

The bug registry referenced from [README.md](README.md) — five real issues hit while getting
openrag-twin running and while building the routing agent, each with root cause and fix. This is
the English, public-facing extract of a longer working log I keep in French for my own
session-to-session notes ([CLAUDE.md](CLAUDE.md), if you're curious what that looks like).

## Bug #1 — Broken OpenSearch healthcheck (cosmetic, upstream)

- **Symptom**: the `openrag-opensearch` container stays permanently `unhealthy` in Docker, even
  though the cluster itself reports `GREEN`.
- **Root cause**: the `healthcheck` in `docker-compose.yml` runs
  `curl -ku admin:$OPENSEARCH_PASSWORD ...`, but that specific container's `environment:` block only
  injects `OPENSEARCH_INITIAL_ADMIN_PASSWORD` — `OPENSEARCH_PASSWORD` is never set inside it, so the
  healthcheck's own auth fails every time, unconditionally.
- **Fix**: none needed. No other service waits on `condition: service_healthy` for this container,
  so nothing is actually blocked. Real health is checked directly:
  `curl -sk -u admin:$PW https://localhost:9200/_cluster/health`. A genuine upstream bug, not a
  local misconfiguration.

## Bug #2 — `LANGFLOW_SECRET_KEY` must be a valid Fernet key

- **Symptom**: on startup, Langflow logs a loop of
  `Error processing <VAR> variable: Fernet key must be 32 url-safe base64-encoded bytes`, then the
  backend fails to generate its Langflow API key (`400 Bad Request` on `/api/v1/api_key/`), which
  blocks flow creation entirely.
- **Root cause**: Langflow encrypts its global variables with Fernet, which requires the key to be
  exactly 32 random bytes, base64 urlsafe-encoded. An arbitrary alphanumeric string is not a valid
  Fernet key, so encryption fails, cascading into everything downstream that depends on it.
- **Fix**: generate the key correctly —
  `python3 -c "import os,base64; print(base64.urlsafe_b64encode(os.urandom(32)).decode())"` —
  and reset `langflow-data/` (it had persisted a `secret_key` derived from the earlier invalid one).

## Bug #3 — `LANGFLOW_ALLOW_CUSTOM_COMPONENTS=false` blocks onboarding

- **Symptom**: the onboarding UI (choosing an embedding provider) fails with a generic `Error`;
  backend logs show `Failed to call custom_component/update: HTTP 403 - Custom component creation
  is disabled`.
- **Root cause**: the security-hardened default (`LANGFLOW_ALLOW_CUSTOM_COMPONENTS=false`) disables
  the `custom_component/update` endpoint, which onboarding relies on to register the selected model
  into the flow templates.
- **Fix**: `LANGFLOW_ALLOW_CUSTOM_COMPONENTS=true` in `.env`, then recreate the langflow/backend
  containers. (Needed anyway for the custom ticket-routing tool built later.)

## Bug #4 — Version-skew in the Docling/Embedding components (the big one)

- **Symptom**: running a flow throws
  `500 Error creating class. ModuleNotFoundError(No module named
  'lfx.components.models_and_agents.model_selection')` (the EmbeddingModel component), and after
  fixing that, `ImportError(Cannot import name 'coerce_docling_document' from
  'lfx.base.data.docling_utils')` (the ExportDoclingDocument component).
- **Root cause**: the `flows/*.json` files shipped in the repo **embed each component's actual
  Python source code** inline (in a `template.code.value` field). That code had been exported from
  a *newer* version of Langflow than the one actually installed in the
  `langflowai/openrag-*:latest` Docker image. The functions it imports
  (`model_selection.apply_model_overrides`, `docling_utils.coerce_docling_document`) don't exist in
  the installed `lfx` package, so the component class can't be constructed at all.
- **Fix**: replace each broken component's embedded code with the version *actually installed* in
  the running container (read via `docker exec openrag-langflow cat
  /opt/app-root/.../lfx/components/.../<component>.py`), then re-apply:
  - `EmbeddingModel` (in all three flows: ingestion, url_ingest, agent) → installed code,
    hardcoded to Ollama's `nomic-embed-text:latest` via `host.docker.internal:11434`.
  - `ExportDoclingDocument` (ingestion flow) → installed code.

  Applied by editing the versioned `flows/*.json` files, then pushing the change live via the
  Langflow API (`PATCH /api/v1/flows/{id}`).
- **Note**: `DoclingRemote` was suspected of the same issue but ingestion ran end-to-end without
  patching it — turned out not to be necessary.
- **The interview-worthy lesson**: when a product serializes application code into its own
  configuration artifacts — here, Langflow flows — it creates an implicit version coupling between
  that artifact and the runtime executing it. That's a real architectural fragility, worth being
  able to explain clearly, not just having fixed once.

## Bug #5 — Version-skew in the Agent & LanguageModel components (same root cause, but latent)

- **Symptom**: the very first time the agent flow was actually *run* (as opposed to just loaded),
  a chain of 500 errors: `ModuleNotFoundError: lfx.components.models_and_agents.agent_helpers`
  (the Agent component), then `ModuleNotFoundError: ...model_selection` (a separate LanguageModel
  component).
- **Root cause**: exactly Bug #4's mechanism — embedded component code exported from a newer
  Langflow version than the one installed — but on components that only execute at *runtime*, so
  the failure stayed completely invisible through every earlier check (the flow loaded fine, edited
  fine, saved fine). The embedded Agent component used a newer LangChain architecture
  (`create_agent` + middlewares + `agent_helpers`) absent from the installed package.
- **Fix**:
  - Agent → replaced with the installed version's `agent.py` (the older `LCToolsAgentComponent`
    architecture).
  - The separate LanguageModel node turned out to be actively harmful beyond just being broken: it
    was overriding the Agent's own inline model config (Anthropic `claude-opus-5`,
    `api_key=ANTHROPIC_API_KEY`) with a default that pointed at OpenAI, for which no key was
    configured (`401`). Since the Agent already had a working Anthropic config of its own, the
    external node and its connecting edge were removed entirely rather than fixed.
- **The interview-worthy lesson**: this reinforces #4, with a sharper edge — a config/runtime
  version coupling like this is worse than a normal breaking bug precisely because it's *latent*: a
  component can look completely fine through every check up to the point it actually executes. It's
  a concrete argument for testing the real run path, not just "does it load."
