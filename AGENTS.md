# AGENTS.md

Guide for anyone (human or coding agent) working in this repo: where things live, how to run them, and the rules that keep the eval honest.

## What this is

Raven infers employee skills and proficiency levels from work evidence and decides, per skill, whether to **send** (ask the person to confirm) or **hold**. Three engines ("Ravens") run on one shared extraction and are scored by one eval harness. **Latent** is the web app: the person rates themselves first, the three Ravens judge, and their Yes/No answers are the real precision metric.

Architecture: [docs/architecture.svg](docs/architecture.svg) (editable source: `docs/architecture.tldraw`).

## Hard rules

1. **Engines never read `data/truth/`.** Only `src/imocha_raven/eval/` may load truth. Any engine import of `eval` or any truth path is a bug.
2. **The model reads, code decides.** LLM calls extract claims with verbatim quotes. Levels and send/hold decisions are plain Python. Unverified quotes are dropped.
3. **Real people's data never enters Git.** `sample real employee data /`, `data/real/`, `pilot.db`, `data/cache/` and `runs/` are gitignored, because they hold real CV text. Before committing, grep the staged files for names, phones and emails.
4. **Third-party internal docs stay local.** The two transcribed plan docs in `docs/` and the raw Codex transcripts `.logs/*.jsonl` are gitignored.
5. **Tune only on the calibration half.** `eval/score.py:split_of()` fixes the cal/test split. Raven 3's threshold and level shift come from the cal half (`engines/raven3_tau.json`). Report the test half.
6. **The feedback loop tunes two scalars, nothing else.** `feedback.py` may move Raven 3's `tau` and `shift` within its guardrails. Evidence weights, decay, discounts, the no-level rule, Raven 2 rules and the taxonomy are human-only (`feedback.HUMAN_ONLY`). Do not widen the loop's authority without audit labels and a shadow run.
7. **Keep it light.** Python + stdlib + pydantic, FastAPI/Jinja2, HTMX + Alpine from a CDN. No frontend build, no ORM, no extra services.

## Where things are

| Path | What |
|---|---|
| `src/imocha_raven/types.py` | Core contract: `Source`, `Bundle`, `Claim`, `Decision`, `EngineResult`, `Engine` protocol |
| `src/imocha_raven/panel.py` | App contract: `PanelResult`, `JudgeScore`, `verdict()` (Latent rule), `fake_panel()`, `EngineScore` |
| `src/imocha_raven/llm.py` | LLM backend: headless `claude -p` (Haiku by default), disk cache by prompt hash, call log `data/cache/llm_calls.jsonl` |
| `src/imocha_raven/load.py` | Bundle and taxonomy loaders, `list_bundles(kind)` |
| `src/imocha_raven/extract.py` | Stage 2: claim extraction per source, cached in `data/cache/claims/` |
| `verify.py`, `map.py`, `group.py` | Stages 3-5: quote verification, taxonomy mapping, independent evidence groups |
| `src/imocha_raven/intake.py` | Live upload to bundle (PDF via `pdftotext`, public GitHub, portfolio URL) |
| `src/imocha_raven/engines/` | `raven1.py` (one-prompt LLM), `raven2.py` (reference rules), `raven3.py` (ours), `common.py` (send policy, consent) |
| `src/imocha_raven/pipeline.py` | `run_panel(bundle, taxonomy)`: runs all three Ravens and builds the Latent panel |
| `src/imocha_raven/eval/` | `score.py` (the only truth reader), `run.py` (full eval), `by_generator.py` (self-agreement check), `simulate_feedback.py` (feedback loop on simulated answers) |
| `src/imocha_raven/feedback.py` | RLHF-borrowed feedback loop: Latent answers auto-tune Raven 3 `tau` and `shift` only, inside guardrails; everything in `HUMAN_ONLY` stays with people |
| `src/imocha_raven/engines/raven3_tau.json`, `raven3_feedback.json` | Offline baseline (eval) and live overlay (feedback loop). Delete the overlay to roll back |
| `src/imocha_raven/app/` | FastAPI server, Jinja2 templates, `static/` (CSS, JS, logo) |
| `data/taxonomy/customer_taxonomy.json` | 55 skills, K4/K3 scales, level lines, aliases, exclude list |
| `data/bundles/P001..P042`, `P0xx-T1..T3` | Synthetic personas and fairness twins (engine input) |
| `data/truth/` | Hidden truth-v2 per persona (eval only). `data/truth_v1/` is the old format |
| `data/spec/PERSONA_SPEC.md` | Dataset contract. Section 8 records the design decisions D-U1..D-U6 |
| `data/grounding/` | Real anchors: cert and course names, PR and issue title styles |
| `data/notes/` | Dataset status, batch notes, truth-v2 change log, ID remaps |
| `docs/sprint/` | Problem framing: 5-question sprint, eval contract vs engine |
| `docs/research/` | Market, methods, fault catalog, audits, real CV observations |
| `docs/engine/raven3-interiors.md` | Raven 3 interiors: input/output, parameter DAG, every parameter with owner and research source, worked example (generated from `engines/raven3_params.py`) |
| `src/imocha_raven/engines/raven3_params.py` | Parameter registry (P1..P13), single source for the doc and the `/scoreboard/raven3` page |
| `docs/playbook/productionizing-raven.md` | Production playbook: parameters, tuning cadence, feedback loop, human in the loop, rollout |
| `scripts/` | `validate_personas.py`, `fix_structure.py`, `make_twins.py`, `run_extraction.py`, `ingest_real.py`, `serve.sh`, `tunnel.sh` |
| `tests/` | Engine tests and claim fixtures |

## Run locally

Prerequisites:
- macOS or Linux, Python 3.13 and [uv](https://docs.astral.sh/uv/).
- `pdftotext` (poppler, `brew install poppler`).
- The Claude Code CLI (`claude`), logged in. Extraction and Raven 1 call it headless.
- Optional: `cloudflared` for a public link.

```bash
uv sync

# 1. Check the dataset (schema, leakage, cross-source coherence)
uv run python -I scripts/validate_personas.py

# 2. Extraction, stages 1-5 (cached; a rerun costs nothing)
uv run python scripts/run_extraction.py

# 3. Eval: all three Ravens, scored on the test half -> runs/latest/
uv run python -m imocha_raven.eval.run
uv run python -m imocha_raven.eval.by_generator

# 4. Tests
uv run python -m tests.test_engines
uv run python -m tests.test_feedback

# 4b. Feedback loop (dry run; add --apply to write the overlay)
uv run python -m imocha_raven.feedback --source live
uv run python -m imocha_raven.eval.simulate_feedback --labels said

# 5. App on http://127.0.0.1:8000
scripts/serve.sh
LATENT_FAKE_PANEL=1 scripts/serve.sh   # UI with demo data, no LLM calls

# 6. Optional public link (second terminal; keeps the Mac awake)
scripts/tunnel.sh
```

App environment variables:
- `LATENT_PASSCODE` (default `raven`): gates play and the engine room.
- `LATENT_FAKE_PANEL=1`: demo data only.
- `LATENT_SESSION_SECRET`: keeps browser sessions valid across restarts.

Routes:
- `/` landing
- `/play` intake
- `/play/{id}` private round
- `/leaderboard`
- `/scoreboard` engine room
- `/scoreboard/raven3` Raven 3 interiors: parameter DAG, slow decision replay, feedback-loop replay

## Common changes

- **New engine:** add `engines/ravenN.py` implementing `Engine.infer(bundle, taxonomy, claims) -> EngineResult`, register it in `pipeline.py` and `eval/run.py`, and add it to `panel.JUDGES`.
- **Extractor prompt change:** bump the extractor version in `extract.py` so the claim cache invalidates, rerun `run_extraction.py`, then rerun the eval.
- **New personas:** follow `data/spec/PERSONA_SPEC.md` (truth-v2), run `validate_personas.py`, then `fix_structure.py` and `make_twins.py`.
- **After a demo with real people:** delete `pilot.db*`, `data/real/uploads/` and the real-person outputs in `runs/`, as the consent notice promises.
