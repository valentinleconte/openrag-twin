#!/usr/bin/env bash
# Single entry point to bring the full openrag-twin demo stack up from a cold
# machine (fresh boot, or after `make stop` / a reboot) and verify it actually
# works end-to-end — not just "containers are Up".
#
# Handles the parts that are NOT managed by docker compose:
#   - Ollama (LaunchAgent, normally auto-starts, but we check anyway)
#   - the nomic-embed-text model (pulled once, cached — no-op if present)
#   - docling-serve (native process, does NOT survive a reboot, must be
#     restarted every time)
#   - the Langflow global variables that the onboarding wizard would
#     otherwise require a browser to set (self-healing even if
#     langflow-data/ was wiped)
#
# Usage: scripts/twin/up.sh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

blue()  { printf '\033[34m%s\033[0m\n' "$1"; }
green() { printf '\033[32m%s\033[0m\n' "$1"; }
red()   { printf '\033[31m%s\033[0m\n' "$1"; }

wait_http_200() {
    local url="$1" label="$2" max_attempts="${3:-30}" delay="${4:-2}"
    local i=0
    while [ "$i" -lt "$max_attempts" ]; do
        code=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
        if [ "$code" = "200" ]; then
            green "  $label: up (${i}x${delay}s)"
            return 0
        fi
        i=$((i + 1))
        sleep "$delay"
    done
    red "  $label: NOT UP after $((max_attempts * delay))s (last HTTP $code)"
    return 1
}

blue "== 1/6 Ollama =="
if ! curl -s -o /dev/null http://localhost:11434 2>/dev/null; then
    echo "  starting..."
    brew services start ollama >/dev/null
fi
wait_http_200 "http://localhost:11434" "ollama" 15 2

if ! ollama list 2>/dev/null | grep -q "^nomic-embed-text"; then
    blue "  pulling nomic-embed-text (first run only)..."
    ollama pull nomic-embed-text
fi
green "  nomic-embed-text: present"

blue "== 2/6 docling-serve =="
make docling

i=0
while [ "$i" -lt 40 ]; do
    code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5001/health 2>/dev/null || echo "000")
    [ "$code" = "200" ] && break
    i=$((i + 1))
    sleep 3
done
if [ "$code" = "200" ]; then
    green "  docling-serve: healthy"
else
    red "  docling-serve: NOT healthy after $((i * 3))s"
    exit 1
fi

blue "== 3/6 Docker stack (make dev-cpu) =="
make dev-cpu

blue "== 4/6 waiting for Langflow + backend =="
wait_http_200 "http://localhost:7860/health" "langflow" 30 2 || exit 1
wait_http_200 "http://localhost:3000/api/settings" "backend (via frontend proxy)" 30 2 || exit 1

blue "== 5/6 syncing Langflow global variables =="
python3 scripts/twin/sync_langflow_vars.py

blue "== 6/6 smoke test (RAG citation + ticket routing) =="
if [ ! -f "$REPO_ROOT/.orag_apikey" ]; then
    red "  .orag_apikey missing — this happens only if the backend's own DB was wiped."
    red "  Generate one manually: open http://localhost:3000 -> Settings -> API Keys -> Create,"
    red "  then: echo -n 'orag_...' > $REPO_ROOT/.orag_apikey && chmod 600 $REPO_ROOT/.orag_apikey"
    exit 1
fi
KEY=$(cat "$REPO_ROOT/.orag_apikey")

ask() {
    curl -s -X POST http://localhost:3000/api/v1/chat \
        -H "X-API-Key: $KEY" -H "Content-Type: application/json" \
        -d "{\"message\":$(python3 -c 'import json,sys;print(json.dumps(sys.argv[1]))' "$1"),\"stream\":false}"
}

rag_resp=$(ask "What is an index in OpenSearch?")
rag_ok=$(echo "$rag_resp" | python3 -c "import json,sys; d=json.load(sys.stdin); print('yes' if 'docs.opensearch.org' in d.get('response','') else 'no')" 2>/dev/null || echo "no")

ticket_resp=$(ask "What is the status of ticket #101?")
ticket_ok=$(echo "$ticket_resp" | python3 -c "import json,sys; d=json.load(sys.stdin); r=d.get('response',''); print('yes' if ('Open' in r and 'Alice' in r) else 'no')" 2>/dev/null || echo "no")

if [ "$rag_ok" = "yes" ]; then
    green "  RAG + citation: OK"
else
    red "  RAG + citation: FAILED"
    echo "$rag_resp"
fi

if [ "$ticket_ok" = "yes" ]; then
    green "  ticket routing: OK"
else
    red "  ticket routing: FAILED"
    echo "$ticket_resp"
fi

echo ""
if [ "$rag_ok" = "yes" ] && [ "$ticket_ok" = "yes" ]; then
    green "✅ openrag-twin is up and validated."
    echo "   Frontend: http://localhost:3000"
    exit 0
else
    red "❌ Stack is up but the smoke test failed — see output above."
    exit 1
fi
