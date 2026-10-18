# Repository instructions

- Explain progress and key decisions to the user in Bulgarian. Keep code, identifiers, and
  commit messages in English. The application supports English and Bulgarian UI text.
- Maintain project documentation in both English and Bulgarian. `README.md` pairs with
  `README.bg.md`; every English Markdown document directly under `docs/` pairs with the same
  filename under `docs/bg/`. Update both versions in the same change when behavior, setup,
  architecture, requirements, examples, or validation claims change.
- Keep reciprocal language links in each pair. Preserve executable commands, environment
  variable names, paths, identifiers, numeric limits, and actual validation results across
  translations. Do not translate recorded English model output as if it were observed Bulgarian output.
- Fictional source procedures in `data/procedures/` are the English RAG corpus, not engineering
  documentation. Do not duplicate or translate them merely to satisfy documentation pairing;
  doing so changes retrieval evidence and requires a separate indexing/evaluation change.
- Preserve existing work. Never include secrets, `.env`, local databases, indexes, caches, or
  evaluation artifacts in commits. Do not push without an explicit user request covering the change.
