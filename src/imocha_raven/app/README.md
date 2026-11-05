# Raven / Just Latent

From the repository root, run `scripts/serve.sh`, then open http://127.0.0.1:8000.
Use a second terminal for `scripts/tunnel.sh`; cloudflared prints the temporary public URL.
The tunnel keeps the Mac awake until stopped. Stop both terminals after the demo.

- `LATENT_PASSCODE` defaults to `raven`. It protects submission and the organiser dashboard.
- `LATENT_FAKE_PANEL=1 scripts/serve.sh` forces clearly labelled synthetic skill/quote fixtures.
- `LATENT_SESSION_SECRET` optionally keeps signed browser sessions valid across restarts.
- Optional intake/pipeline imports and execution run in a two-worker background pool. Import or execution failures use the labelled demo fixture. The browser polls every two seconds.
- `/`: landing; `/play`: intake; `/play/{id}`: private round; `/leaderboard`: opt-in first names; `/scoreboard`: organiser dashboard.
- SQLite `pilot.db` holds consent timestamps, submissions/results, immutable self-rating timestamps, reveals, skill answers, missed feedback, and leaderboard consent. Uploads use random filenames in `data/real/uploads/`.
- Demo rounds do not count in live Yes rates, wins, or leaderboard rankings. Benchmark scores and explorer panels are read from `runs/latest/`; absent files show empty states.
- The Teams message is a preview. Its buttons do not send messages or affect pilot metrics.

The organiser must delete `pilot.db` (including any `-wal` / `-shm` sidecars), `data/real/uploads/`, and real-person engine outputs after the demo, as promised by the consent notice. Preserve no real-person data in Git.

The only web dependencies added to the project are FastAPI, uvicorn, Jinja2, and python-multipart. HTMX 2.0.4 and Alpine 3.14.9 load from their CDNs; Google Fonts supplies display typography. No asset build step.
