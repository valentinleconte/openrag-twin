# openrag-twin — contexte projet

> Ce fichier documente le **projet méta** (pourquoi ce repo existe, où il en est).
> Pour les instructions techniques sur le code d'OpenRAG lui-même (skills, structure),
> voir [AGENTS.md](AGENTS.md).

## Objectif

Préparation d'un entretien **FDE / Client Engineer chez IBM**. Ce repo est une
réplique fonctionnelle d'**OpenRAG**, le produit RAG agentique d'IBM
(bâti sur Langflow + Docling + OpenSearch), pour démontrer une compréhension
en profondeur de la stack — pas un projet d'apprentissage from-scratch : on
part du repo upstream officiel et on le fait tourner, on l'instrumente, on le
comprend, on peut en défendre chaque choix technique à l'oral.

Repo upstream cloné : https://github.com/langflow-ai/openrag.git (remote `upstream`)
Origin personnel : https://github.com/valentinleconte/openrag-twin.git (remote `origin`)

## Stack

- **Langflow** — orchestration des flows agentiques (chat, ingestion, ingestion URL, nudges), UI sur `:7860`
- **Docling** — parsing/extraction de documents pour l'ingestion. Tourne en service **natif** (`docling-serve` sur `:5001`, lancé via `make docling`, PAS dans Docker), appelé par les flows Langflow
- **OpenSearch** — moteur de recherche vectoriel + lexical (BM25 + kNN), API sur `:9200`, Dashboards sur `:5601`
- **Backend OpenRAG** (FastAPI, `openrag-backend`) — orchestre Langflow ↔ OpenSearch, expose l'API applicative, génère sa clé API Langflow au démarrage, crée/synchronise les flows depuis `flows/*.json`
- **Frontend OpenRAG** — UI applicative (chat + ingestion), `:3000`
- **Ollama** (natif, `:11434`) — sert le modèle d'**embedding** `nomic-embed-text` (768 dim). Choisi car Anthropic ne fournit pas d'embeddings et on n'a pas de clé OpenAI/watsonx
- **Docker Compose** — orchestration locale (`make dev-cpu` = stack CPU-only, pas de build GPU)
- Modèle LLM (agent) : **Anthropic** (`ANTHROPIC_API_KEY` dans `.env`, non commité)

## Scénario fonctionnel (défini)

**Corpus** : 11 pages de la doc technique OpenSearch, converties HTML→Markdown
(`opensearch-docs-md/`, regénérables via `scripts/twin/fetch_opensearch_docs.py`).
Ingérées : **108 chunks** dans OpenSearch (index `documents`).

**Agent à routage** — l'agent doit DÉCIDER entre deux comportements selon la question :
- (a) **Question de connaissance OpenSearch** → RAG classique (`search_documents` sur
  OpenSearch) avec **citation de la source** (quelle page a servi à la réponse).
- (b) **Demande liée à un "ticket support"** (ex. « statut du ticket #123 ? ») →
  l'agent appelle un **outil externe mock** au lieu de chercher dans la doc.

Objectif de démo : prouver que l'agent sait router, pas juste faire du RAG passif.

Jeu de validation (pas encore le golden set — ça viendra en phase éval) :
3-5 questions de chaque type pour valider le routage.

## Phase actuelle : ingestion terminée, construction de l'agent en cours

- [x] **Phase 0** — Prérequis : Docker Desktop 29.7.2, Python 3.13.14 (via `uv`), uv 0.12.2, Ollama, docling-serve
- [x] **Phase 1** — Clone upstream dans `~/dev/openrag-twin`, remotes `origin`/`upstream` configurés, poussé
- [x] **Phase 2** — `.env` configuré (voir « Config .env » ci-dessous)
- [x] **Phase 3** — `make dev-cpu` : 5 conteneurs up, tous les endpoints répondent
- [x] **Ingestion** — 11 pages OpenSearch converties en Markdown et ingérées (108 chunks, embedding Ollama)
- [x] **Agent à routage** — outil mock `get_ticket_status` ajouté + prompt de routage + citation. Fonctionne.
- [x] **Validation** — 7/7 questions OK (3 connaissance avec citation, 3 ticket dont 1 inconnu, 1 mélange → 2 outils)
- [x] **Reproductibilité** — `make twin-up` : une seule commande, remonte tout depuis un état froid, s'auto-valide
- [ ] **Éval** (plus tard) — golden set structuré

### Reproductibilité — `make twin-up`
**Pour relancer la démo après un reboot / arrêt complet, une seule commande :**
```bash
make twin-up
```
Ce que ça fait (dans l'ordre, ~2 min, s'arrête avec un message clair si une étape échoue) :
1. Vérifie/démarre Ollama (LaunchAgent, survit normalement à un reboot — vérifié quand même)
2. Vérifie/télécharge le modèle `nomic-embed-text` (no-op si déjà présent)
3. Démarre `docling-serve` — **NE survit PAS à un reboot** (process natif, pas un service système),
   c'est la seule pièce qui doit être relancée à chaque fois
4. `make dev-cpu` (les 5 conteneurs Docker)
5. Attend Langflow + backend prêts
6. **Réapplique les 4 variables globales Langflow** (`scripts/twin/sync_langflow_vars.py`, idempotent,
   via API) — celles que l'assistant d'onboarding du navigateur configure normalement. Ça rend le setup
   **auto-réparateur** même si `langflow-data/` était wipé, sans repasser par le navigateur.
7. **Smoke test automatique** : pose une question de connaissance (vérifie la citation) + une question
   de ticket (vérifie le routage). Échoue bruyamment si l'un des deux casse.

**Ce qui ne peut PAS être auto-réparé** : la clé API backend (`.orag_apikey`, gitignorée — stockée dans
la DB du backend, qui survit à un simple restart). Si le volume `data/` du backend est lui-même wipé
(scénario rare), il faut en recréer une manuellement via l'UI (Settings → API Keys) — instructions
affichées par le script si le fichier manque.

**Testé pour de vrai** : `docker compose down` + `make docling-stop` (tout coupé), puis `make twin-up`
→ stack complète + agent validé en ~2 min, zéro clic navigateur.

### Détail de l'agent à routage (livré)
- **2 outils exposés à l'Agent** : `search_documents` (RAG hybride OpenSearch, déjà présent) et
  `get_ticket_status` (**nouveau**, custom component, code dans `scripts/twin/ticket_status_component.py`,
  embarqué dans `flows/openrag_agent.json`). Mock ITSM : tickets 101/102/103 + fallback "not found".
- **Prompt de routage** (champ `system_prompt` de l'Agent) : règles de décision RAG vs ticket +
  table filename→URL pour la citation.
- **Chemin d'appel de démo** : `POST /v1/chat` sur le backend (`:3000`) avec la clé API backend
  (header `X-API-Key`). ⚠️ **PAS** l'API Langflow directe : la recherche OpenSearch utilise l'auth **JWT**
  injectée par le backend à chaque requête ; en appelant Langflow en direct on obtient un `401`.
- **Config runtime Langflow à réappliquer si `langflow-data/` est réinitialisé** (ce sont des variables
  globales Langflow, pas dans les fichiers de flow) :
  - `SELECTED_EMBEDDING_MODEL=nomic-embed-text:latest`, `SELECTED_EMBEDDING_MODEL_PROVIDER=Ollama`,
    `OLLAMA_BASE_URL=http://host.docker.internal:11434`
  - `OPENRAG-QUERY-FILTER=` (vide) — sinon le parseur de filtre du composant OpenSearch lève
    "Invalid filter_expression JSON type: expected a JSON object".

## Config .env (valeurs non commitées, à réappliquer si `.env` recréé)

- `LANGFLOW_SECRET_KEY` = clé Fernet valide (voir bug #2)
- `OPENSEARCH_PASSWORD` = conforme policy (maj/min/chiffre/spécial, ≥8)
- `LANGFLOW_SUPERUSER` / `_PASSWORD` = générés via `make generate-langflow-password`
- `ANTHROPIC_API_KEY` = renseignée
- `LANGFLOW_ALLOW_CUSTOM_COMPONENTS=true` (défaut `false` — voir bug #3)
- `INGEST_SAMPLE_DATA=false` (défaut `true` — évite d'ingérer les docs d'exemple d'OpenRAG dans notre corpus)

## Registre des bugs rencontrés & corrigés (matériel entretien)

### Bug #1 — Healthcheck OpenSearch cassé (cosmétique, upstream)
- **Symptôme** : conteneur `openrag-opensearch` reste éternellement `unhealthy` côté Docker, alors que le cluster répond `GREEN`.
- **Cause racine** : le `healthcheck` dans `docker-compose.yml` fait `curl -ku admin:$OPENSEARCH_PASSWORD ...`, mais ce conteneur ne reçoit que `OPENSEARCH_INITIAL_ADMIN_PASSWORD` dans son bloc `environment:` — `OPENSEARCH_PASSWORD` n'y est jamais injecté, donc l'auth du healthcheck échoue toujours.
- **Fix** : aucun nécessaire. Aucun service n'attend `condition: service_healthy`, donc ça ne bloque rien. On vérifie la vraie santé via `curl -sk -u admin:$PW https://localhost:9200/_cluster/health`. Bug amont réel, pas un souci local.

### Bug #2 — `LANGFLOW_SECRET_KEY` doit être une clé Fernet valide
- **Symptôme** : au démarrage, Langflow logue en boucle `Error processing <VAR> variable: Fernet key must be 32 url-safe base64-encoded bytes`, puis le backend échoue à générer sa clé API Langflow (`400 Bad Request` sur `/api/v1/api_key/`), ce qui bloque la création des flows.
- **Cause racine** : Langflow chiffre ses variables globales avec Fernet, qui exige une clé = 32 octets aléatoires encodés base64-urlsafe. Une chaîne alphanumérique quelconque n'est pas une clé Fernet valide → le chiffrement plante en cascade.
- **Fix** : générer la clé correctement :
  `python3 -c "import os,base64; print(base64.urlsafe_b64encode(os.urandom(32)).decode())"`
  et réinitialiser `langflow-data/` (qui contenait un `secret_key` dérivé de l'ancienne clé invalide).

### Bug #3 — `LANGFLOW_ALLOW_CUSTOM_COMPONENTS=false` bloque l'onboarding
- **Symptôme** : l'onboarding UI (choix du provider d'embedding) échoue avec `Error` ; logs backend : `Failed to call custom_component/update: HTTP 403 - Custom component creation is disabled`.
- **Cause racine** : le durcissement sécu par défaut (`LANGFLOW_ALLOW_CUSTOM_COMPONENTS=false`) interdit l'endpoint `custom_component/update`, dont l'onboarding se sert pour enregistrer le modèle sélectionné dans les flows.
- **Fix** : `LANGFLOW_ALLOW_CUSTOM_COMPONENTS=true` dans `.env` + recreate des conteneurs langflow/backend. (On en a de toute façon besoin pour l'outil de routage custom à venir.)

### Bug #4 — Version-skew des composants Docling/Embedding dans les flows JSON (le gros morceau)
- **Symptôme** : à l'exécution d'un flow, `500 Error creating class. ModuleNotFoundError(No module named 'lfx.components.models_and_agents.model_selection')` (composant EmbeddingModel), puis après ce premier fix, `ImportError(Cannot import name 'coerce_docling_document' from 'lfx.base.data.docling_utils')` (composant ExportDoclingDocument).
- **Cause racine** : les fichiers `flows/*.json` fournis par le repo **embarquent le code source Python de chaque composant** (champ `template.code.value`). Ce code a été exporté depuis une version de Langflow **plus récente** que celle réellement installée dans l'image Docker `langflowai/openrag-*:latest`. Les modules/fonctions qu'il importe (`model_selection.apply_model_overrides`, `docling_utils.coerce_docling_document`) n'existent pas dans le package `lfx` installé → la classe du composant ne peut pas être construite.
- **Fix** : remplacer le `code` embarqué de chaque composant cassé par la version **réellement installée** dans le conteneur
  (`docker exec openrag-langflow cat /opt/app-root/.../lfx/components/.../<composant>.py`), puis re-patcher :
  - `EmbeddingModel` (dans les 3 flows : ingestion, url_ingest, agent) → code installé, hardcodé sur Ollama `nomic-embed-text:latest` + endpoint `host.docker.internal:11434`.
  - `ExportDoclingDocument` (flow ingestion) → code installé.
  Application : édition des `flows/*.json` (versionné) + push live via l'API Langflow (`PATCH /api/v1/flows/{id}`).
- **Note** : `DoclingRemote` (docling_remote.py) était suspecté du même problème mais l'ingestion passe end-to-end sans le patcher — pas nécessaire.
- **Leçon entretien** : quand un produit sérialise du code applicatif dans ses artefacts de config (ici les flows), il crée un couplage de version implicite entre l'artefact et le runtime. C'est une vraie fragilité d'archi à savoir expliquer.

### Bug #5 — Version-skew des composants Agent & LanguageModel (suite du #4, à l'exécution)
- **Symptôme** : au premier *run* du flow agent (jamais exécuté jusque-là), erreurs 500 en chaîne :
  `ModuleNotFoundError: lfx.components.models_and_agents.agent_helpers` (composant Agent), puis
  `ModuleNotFoundError: ...model_selection` (composant LanguageModel séparé).
- **Cause racine** : exactement le Bug #4 (code de composant embarqué exporté d'une version plus récente
  que celle installée), mais sur des composants qui ne se déclenchent qu'à **l'exécution** du flow —
  donc invisibles tant qu'on n'avait pas lancé l'agent. Le composant Agent embarqué utilisait une
  architecture LangChain récente (`create_agent` + middlewares + `agent_helpers`) absente du package installé.
- **Fix** :
  - Agent → remplacé par le code `agent.py` de la version installée (architecture `LCToolsAgentComponent`).
  - LanguageModel (nœud externe) → il **écrasait** le modèle inline de l'Agent (Anthropic `claude-opus-5`,
    `api_key=ANTHROPIC_API_KEY`) par un défaut **OpenAI** (dont on n'a pas la clé → `401`). Comme l'Agent a
    déjà une config Anthropic valide en interne, on a **supprimé** ce nœud externe et son arête. L'Agent
    utilise désormais sa propre config Anthropic.
- **Leçon entretien** : renforce le #4 — le couplage config↔runtime est d'autant plus vicieux qu'il est
  **latent** : un composant peut sembler OK au chargement du flow et ne casser qu'à l'exécution. D'où
  l'importance de tester le *run* réel, pas juste le démarrage.

### Point d'attention — citation des sources
`source_url` s'indexe **vide** dans OpenSearch pour les fichiers uploadés (il n'est
peuplé que par le chemin d'ingestion-par-URL, pas par l'upload de fichier). Le
`filename` est fiable. → La citation source de l'agent mappe `filename` → URL via
une table dans le prompt système (les fichiers `.md` gardent l'URL en frontmatter).

## Commandes utiles

```bash
make dev-cpu          # démarre la stack CPU-only (Docker)
make docling          # démarre docling-serve (natif, :5001)
make docling-stop     # arrête docling-serve
docker compose ps     # statut des conteneurs
docker logs openrag-backend --tail 50
docker logs openrag-langflow --tail 50
ollama list           # modèles Ollama dispo (embedding)
```

Corpus : regénérer avec
`uv run --with beautifulsoup4 --with httpx --with markitdown python3 scripts/twin/fetch_opensearch_docs.py opensearch-docs-md`

## Nettoyage GitHub (repo présentable pour l'entretien)

- **Historique squashé** : les 4079 commits upstream + nos commits ont été réduits à
  **un seul commit initial**, signé par l'utilisateur. Contributors passe de 61 à 1.
  L'historique complet reste récupérable sur la branche distante
  `archive/full-history-pre-squash` si besoin un jour.
- **5 PRs Dependabot fermées** (mises à jour d'Actions GitHub héritées d'IBM, toutes en
  échec CI, visibles publiquement) + `.github/dependabot.yml` supprimé pour ne pas en
  regénérer.
- **Workflows CI réduits de 24 à 5** (puis 6 avec l'ajout ultérieur de `pages.yml`, voir plus
  bas) : gardés uniquement ceux qui donnent un vrai signal technique/sécurité et qui passent
  réellement (`codeql.yml`, `test-ci.yml`, `lint-backend.yml`, `lint-frontend.yml`,
  `react-doctor.yml`). Supprimés : tout ce qui publie des packages/images Docker, déploie une
  doc/Pages, gère des labels de PR, ou tourne sur un cron — inapplicable à un fork perso et
  risque de red-X silencieux.
- **Correctif important** : le squash initial gardait un trailer `Co-Authored-By: Claude`
  dans le message de commit — GitHub le traite comme un **contributeur distinct**
  (`?author=claude` a sa propre page), ce qui repassait le compteur à 2. Retiré, re-squashé.
  Vérifié à la source (`/graphs/contributors`, pas juste l'API REST qui peut être en
  avance sur le cache du graphe) : 1 seul contributeur.
- **Nettoyage racine du repo** (moins de scroll avant d'arriver au README) : supprimé
  `kubernetes/` (opérateur K8s, jamais utilisé par notre stack Docker Compose),
  `sdks/` (SDKs client Python/TS, idem) et `.coderabbit.yaml` (bot tiers non installé
  sur ce repo). Vérifié avant suppression : aucun n'est référencé par un Dockerfile,
  `docker-compose.yml`, ou un des 5 workflows CI gardés sur le chemin `push` (un seul
  job de `test-ci.yml`, gated `pull_request`-only, référence `sdks/typescript` — ne
  tourne jamais sur nos push directs à `main`). Tout le reste du contenu à la racine
  (Dockerfiles, docker-compose*.yml, `src/`, `frontend/`, `flows/`, `securityconfig/` +
  `cloud_securityconfig/` — les deux copiés dans l'image OpenSearch, `custom_components/`,
  `enhancements/` — vrai code importé par `src/connectors/registry.py`, `plugins/` —
  les skills Claude Code y symlinkent) est activement référencé par le build ou le
  runtime : **pas touché**, casser un de ces chemins casse `make dev-cpu`.
- **Split public/privé de la doc** : le registre de bugs (ci-dessus) a été extrait vers
  [ENGINEERING_LOG.md](ENGINEERING_LOG.md), en anglais — le README pointait dessus comme
  "the full engineering log" mais CLAUDE.md est en français, illisible pour un lecteur
  anglophone. Le README pointe maintenant vers ENGINEERING_LOG.md ; CLAUDE.md reste mes
  notes de travail (pas besoin d'être parfait pour un public externe, juste pour moi entre
  sessions). Idem pour `CONTRIBUTING.md`/`SECURITY.md` (toujours le contenu IBM d'origine,
  non modifié) : ajouté une bannière en tête de chacun clarifiant que ce n'est pas
  spécifique à ce fork. Et `make help` n'annonce plus `make test-sdk` (référençait
  `sdks/`, supprimé) — la cible existe toujours dans le Makefile, juste plus mise en avant.
