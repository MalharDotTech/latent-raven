# latent-raven

Raven infers an employee's skills and proficiency levels from work evidence (CV, GitHub, Jira, certs, LMS, assessments, docs) and decides, per skill, whether to send it to the person for confirmation or hold. **Just Latent** is the game mode: you rate yourself first, three Ravens judge, and you see if you match.

- **The model reads, code decides.** An LLM extracts claims with verbatim quotes, and every quote is checked against the source. A claim without a quote is dropped.
- **Three judges, one harness.** All three are run and scored by the same harness on the same data:
  - Raven 1: one-prompt LLM baseline.
  - Raven 2: rule-based reference engine (floor/ceiling, caps, decay).
  - Raven 3: evidence clusters, dependence-aware combination, calibrated threshold.
- **Honest eval.** Only `eval/` can read the hidden truth. Precision on sends comes with Wilson CIs, alongside coverage, traps caught, fairness-twin flips and cost.

## Run

```bash
uv sync
uv run python scripts/run_extraction.py      # stages 1-5, cached (needs the `claude` CLI)
uv run python -m imocha_raven.eval.run        # scoreboard -> runs/latest/
scripts/serve.sh                              # app on http://127.0.0.1:8000
scripts/tunnel.sh                             # optional public link via Cloudflare quick tunnel
```

## Layout

- `src/imocha_raven/`: pipeline (`load`, `extract`, `verify`, `map`, `group`), `engines/`, `eval/`, `app/`
- `data/`: synthetic company "Kestrel Cloud", with 42 personas and 18 fairness twins. Truth files are hidden from the engines. Also holds the taxonomy and the grounding corpus.
- `docs/`: sprint notes, research, architecture
- `scripts/`: validators, structure repair, twin generator

All people in `data/` are fictitious. Real pilot data is never committed.
