Implemented within `src/imocha_raven/app/`:

- Searchable, grouped picker with readable labels and anonymous names for players without leaderboard consent.
- Top explainer strip and per-judge trace visuals, with replay, scroll-triggered animation and reduced-motion support.
- Graceful fallbacks for old traces and missing runs.

TestClient checks passed, including all 50 saved person pages. Filtering and reduced-motion checks passed. Browser visual review was blocked by computer-use permissions.

Restart `scripts/serve.sh`, then open [the engine room](http://127.0.0.1:8000/scoreboard) and choose a person.