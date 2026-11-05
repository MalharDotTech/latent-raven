Built the app and launch scripts.

- Routes: `/`, `/play`, private `/play/{id}` rounds, `/leaderboard`, and passcode-gated `/scoreboard`.
- Run: `scripts/serve.sh`; open `http://127.0.0.1:8000`.
- Public tunnel: run `scripts/tunnel.sh` separately.
- Default passcode: `raven`; override with `LATENT_PASSCODE`.
- Force demo mode: `LATENT_FAKE_PANEL=1 scripts/serve.sh`.

Real engine integration runs automatically when available. Failures fall back to clearly labelled synthetic skills and quotes. Missing benchmark files show empty states. Demo rounds are excluded from live metrics and rankings.

Validation: **81 in-process HTTP checks passed**, plus template, JavaScript, shell, and dependency checks. The sandbox denied localhost binding, so live curl/browser verification remains unverified. No server is running.