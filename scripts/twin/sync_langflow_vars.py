#!/usr/bin/env python3
"""Idempotently (re)apply the Langflow global variables the openrag-twin demo
needs, without going through the browser onboarding wizard.

Why this exists: the onboarding wizard (Settings > LLM/embedding provider) is
the *only* UI path that sets SELECTED_EMBEDDING_MODEL(_PROVIDER) and
OLLAMA_BASE_URL. If `langflow-data/` is ever wiped (fresh clone, `docker
compose down -v`, accidental delete), those variables disappear and the demo
breaks in ways that are non-obvious to debug (see CLAUDE.md bug log). This
script recreates them directly via the Langflow API, in a few seconds,
without touching a browser.

Also clears OPENRAG-QUERY-FILTER: the OpenSearch component's filter parser
raises "Invalid filter_expression JSON type" if that variable is set to a
non-empty, non-JSON-object string — which is its state after a fresh
onboarding run in this version. See CLAUDE.md.

Usage:
    uv run python scripts/twin/sync_langflow_vars.py
Reads LANGFLOW_SUPERUSER / LANGFLOW_SUPERUSER_PASSWORD from .env (repo root).
"""

from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = REPO_ROOT / ".env"
LANGFLOW_BASE = "http://localhost:7860"

# name -> (value, type). type "Credential" masks the value in the UI/API reads,
# matching how the onboarding wizard creates these same variables.
DESIRED_VARS: dict[str, tuple[str, str]] = {
    "OLLAMA_BASE_URL": ("http://host.docker.internal:11434", "Credential"),
    "SELECTED_EMBEDDING_MODEL": ("nomic-embed-text:latest", "Credential"),
    "SELECTED_EMBEDDING_MODEL_PROVIDER": ("Ollama", "Credential"),
    # Must stay empty: a non-empty, non-JSON-object value breaks the
    # OpenSearch component's filter_expression parser (see CLAUDE.md).
    "OPENRAG-QUERY-FILTER": ("", "Credential"),
}


def _read_env_var(name: str) -> str:
    text = ENV_PATH.read_text()
    m = re.search(rf"^{re.escape(name)}=(.*)$", text, re.MULTILINE)
    if not m:
        raise SystemExit(f"{name} not found in {ENV_PATH}")
    return m.group(1).strip().strip("'").strip('"')


def _request(method: str, path: str, token: str | None = None, body: dict | None = None):
    url = LANGFLOW_BASE + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept-Encoding", "identity")  # avoid gzip parsing headaches
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read()
            return resp.status, (json.loads(raw) if raw else None)
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw)
        except json.JSONDecodeError:
            return e.code, raw.decode(errors="replace")


def login() -> str:
    user = _read_env_var("LANGFLOW_SUPERUSER")
    password = _read_env_var("LANGFLOW_SUPERUSER_PASSWORD")
    url = LANGFLOW_BASE + "/api/v1/login"
    body = f"username={user}&password={password}".encode()
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    req.add_header("Accept-Encoding", "identity")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())["access_token"]
    except urllib.error.URLError as e:
        raise SystemExit(f"Could not reach Langflow at {LANGFLOW_BASE}: {e}") from e


def main() -> None:
    token = login()
    status, existing = _request("GET", "/api/v1/variables/", token=token)
    if status != 200:
        raise SystemExit(f"Failed to list variables: {status} {existing}")
    by_name = {v["name"]: v for v in existing}

    for name, (value, vtype) in DESIRED_VARS.items():
        if name in by_name:
            var_id = by_name[name]["id"]
            body = {"id": var_id, "name": name, "value": value, "type": vtype}
            status, resp = _request("PATCH", f"/api/v1/variables/{var_id}", token=token, body=body)
            action = "updated"
        else:
            body = {"name": name, "value": value, "type": vtype, "default_fields": []}
            status, resp = _request("POST", "/api/v1/variables/", token=token, body=body)
            action = "created"

        if status not in (200, 201):
            print(f"FAILED to set {name}: HTTP {status} {resp}", file=sys.stderr)
            sys.exit(1)
        print(f"  {name}: {action}")

    print("Langflow global variables synced.")


if __name__ == "__main__":
    main()
