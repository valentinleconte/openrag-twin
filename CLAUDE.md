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

Repo upstream cloné : https://github.com/langflow-ai/openrag.git
Remote `origin` actuel : encore celui d'upstream (voir note en bas de fichier).

## Stack

- **Langflow** — orchestration des flows agentiques (chat, ingestion, ingestion URL, nudges), UI sur `:7860`
- **Docling** — parsing/extraction de documents pour l'ingestion (via `docling-serve`, appelé par les flows Langflow)
- **OpenSearch** — moteur de recherche vectoriel + lexical (BM25 + kNN), API sur `:9200`, Dashboards sur `:5601`
- **Backend OpenRAG** (FastAPI, `openrag-backend`) — orchestre Langflow ↔ OpenSearch, expose l'API applicative, génère sa clé API Langflow au démarrage, crée/synchronise les flows depuis `flows/*.json`
- **Frontend OpenRAG** — UI applicative (chat + ingestion), `:3000`
- **Docker Compose** — orchestration locale (`make dev-cpu` = stack CPU-only, pas de build GPU)
- Modèle LLM configuré : **Anthropic** (`ANTHROPIC_API_KEY` dans `.env`, non commité)

## Scénario fonctionnel

**Pas encore défini — à faire à la prochaine session.** Le choix du cas d'usage
(quel type de documents ingérer, quel scénario de requête agentique démontrer)
revient à l'utilisateur et ne doit pas être décidé par Claude à sa place.

## Phase actuelle : Phase 3 terminée (installation vérifiée)

- [x] **Phase 0** — Prérequis : Docker Desktop 29.7.2, Python 3.13.14 (via `uv python install`), uv 0.12.2
- [x] **Phase 1** — Clone du repo upstream dans `~/dev/openrag-twin`
- [x] **Phase 2** — `.env` configuré : credentials Langflow générées (`make generate-langflow-password`),
      `OPENSEARCH_PASSWORD` conforme à la policy (maj/min/chiffre/spécial, ≥8 car.),
      `LANGFLOW_SECRET_KEY` (clé Fernet valide — voir incident ci-dessous), `ANTHROPIC_API_KEY` renseignée
- [x] **Phase 3** — `make dev-cpu` : 5 conteneurs up (opensearch, langflow, backend, frontend, dashboards),
      tous les endpoints vérifiés répondre (200/302), flows créés côté backend sans erreur

**Prochaine étape** : définir le scénario fonctionnel (Phase suivante), puis ingérer des documents.

## Incident résolu (bon à savoir pour l'entretien)

Deux bugs rencontrés pendant le setup, utiles à connaître pour parler de la stack en profondeur :

1. **Healthcheck OpenSearch cassé dans `docker-compose.yml` upstream** : le test
   (`curl -ku admin:$OPENSEARCH_PASSWORD ...`) référence une variable d'env qui n'est
   *jamais* injectée dans le conteneur `opensearch` (seul `OPENSEARCH_INITIAL_ADMIN_PASSWORD`
   l'est). Le conteneur reste donc éternellement en `starting`/`unhealthy` côté Docker
   alors que le cluster est réellement `GREEN`. Aucun autre service n'attend
   `condition: service_healthy`, donc ça ne bloque rien en pratique — mais c'est un vrai
   bug amont, pas un problème d'environnement local.
2. **`LANGFLOW_SECRET_KEY` doit être une clé Fernet valide** (32 octets aléatoires,
   base64 urlsafe — pas une string alphanumérique quelconque). Une clé mal formée fait
   échouer silencieusement le chiffrement des variables internes de Langflow, ce qui
   fait ensuite échouer la génération de clé API du backend (`400 Bad Request` sur
   `/api/v1/api_key/`), qui elle-même bloque la création des flows. Génération correcte :
   `python3 -c "import os,base64; print(base64.urlsafe_b64encode(os.urandom(32)).decode())"`

## Commandes utiles

```bash
make dev-cpu          # démarre la stack CPU-only
docker compose ps     # statut des conteneurs
docker compose down   # arrête tout
docker logs openrag-backend --tail 50    # logs backend
docker logs openrag-langflow --tail 50   # logs langflow
```

## Note remote Git

Le remote `origin` pointe encore vers `langflow-ai/openrag` (upstream, hérité du clone).
À reconfigurer vers le repo GitHub personnel `openrag-twin` avant tout `push`
(ne jamais pousser vers upstream).
