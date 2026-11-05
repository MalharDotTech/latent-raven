"""Raven's local, consent-first pilot UI. Engine modules remain optional."""
from __future__ import annotations

import asyncio
import hashlib
import hmac
import inspect
import ipaddress
import json
import logging
import os
import re
import secrets
import sqlite3
import threading
import time
import traceback
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from imocha_raven.panel import (PanelResult, PanelSkill, JudgeScore, EngineScore,
                               JUDGES, JUDGE_BLURB, fake_panel, verdict, panel_average)

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
DB = ROOT / "pilot.db"
UPLOADS = ROOT / "data/real/uploads"
LATEST = ROOT / "runs/latest"
MAX_FILE = 5 * 1024 * 1024
ERROR_LOG = Path(__file__).resolve().parents[3] / "data" / "real" / "app_errors.log"
FAKE_MODE = os.environ.get("LATENT_FAKE_PANEL", "").lower() in {"1", "true", "yes"}
CONSENT = "Your documents are processed by Claude (Anthropic) and pass through Cloudflare. Stored only on the organiser's laptop, deleted after the demo. Your first name and score appear on the Latent leaderboard."
SECRET = os.environ.get("LATENT_SESSION_SECRET", secrets.token_hex(32)).encode()
POOL = ThreadPoolExecutor(max_workers=2, thread_name_prefix="raven")
RATE: dict[str, deque] = defaultdict(deque)
RATE_LOCK = threading.Lock()
LOG = logging.getLogger(__name__)


def connect():
    conn = sqlite3.connect(DB, timeout=15)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    with connect() as c:
        c.executescript("""
        PRAGMA journal_mode=WAL;
        CREATE TABLE IF NOT EXISTS submissions (
          id TEXT PRIMARY KEY, first_name TEXT NOT NULL, created REAL NOT NULL,
          consent_at REAL NOT NULL, status TEXT NOT NULL, result TEXT,
          demo INTEGER NOT NULL DEFAULT 0, notice TEXT NOT NULL DEFAULT '');
        CREATE TABLE IF NOT EXISTS self_ratings (
          submission_id TEXT NOT NULL REFERENCES submissions(id), skill_id TEXT NOT NULL,
          level INTEGER NOT NULL, locked_at REAL NOT NULL,
          PRIMARY KEY(submission_id, skill_id));
        CREATE TABLE IF NOT EXISTS reveals (
          submission_id TEXT NOT NULL, skill_id TEXT NOT NULL, revealed_at REAL NOT NULL,
          verdict TEXT NOT NULL, panel REAL, PRIMARY KEY(submission_id, skill_id));
        CREATE TABLE IF NOT EXISTS answers (
          submission_id TEXT NOT NULL, skill_id TEXT NOT NULL, has_skill TEXT NOT NULL,
          level_feedback TEXT NOT NULL, answered_at REAL NOT NULL,
          PRIMARY KEY(submission_id, skill_id));
        CREATE TABLE IF NOT EXISTS missed (
          submission_id TEXT PRIMARY KEY, text TEXT NOT NULL, saved_at REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS leaderboard (
          submission_id TEXT PRIMARY KEY, first_name TEXT NOT NULL, opted_at REAL NOT NULL);
        """)
        # A restart must never leave a participant polling a dead worker.
        c.execute("UPDATE submissions SET status='interrupted', notice='The local server restarted. Please submit again.' WHERE status='running'")
    os.chmod(DB, 0o600)


@asynccontextmanager
async def lifespan(app):
    init_db()
    if FAKE_MODE:
        print("\n*** LATENT_FAKE_PANEL=1: DEMO MODE. Every round gets synthetic skills, not the real engine. ***\n", flush=True)
    yield


app = FastAPI(title="Raven · Latent", docs_url=None, redoc_url=None, lifespan=lifespan)
app.mount("/static", StaticFiles(directory=HERE / "static"), name="static")
templates = Jinja2Templates(directory=HERE / "templates")
templates.env.globals.update(judges=JUDGES, blurbs=JUDGE_BLURB, consent_text=CONSENT, fake_mode=FAKE_MODE)


def page(request, name, status_code=200, **ctx):
    return templates.TemplateResponse(request=request, name=name, context=ctx, status_code=status_code)


def signature(value):
    return hmac.new(SECRET, value.encode(), hashlib.sha256).hexdigest()


def cookie_value(value):
    return value + "." + signature(value)


def signed_cookie(request, name, value):
    return hmac.compare_digest(request.cookies.get(name, ""), cookie_value(value))


def set_cookie(response, request, name, value):
    response.set_cookie(name, cookie_value(value), httponly=True, samesite="strict",
                        secure=request.url.scheme == "https" or request.headers.get("x-forwarded-proto") == "https",
                        max_age=12 * 3600)


@app.middleware("http")
async def safeguards(request, call_next):
    if request.method == "POST":
        if "content-length" not in request.headers:
            return HTMLResponse("A Content-Length header is required for uploads.", status_code=411)
        try:
            if int(request.headers.get("content-length", 0)) > MAX_FILE + 200_000:
                return page(request, "error.html", message="That upload is too big. Choose a PDF under 5 MB.", status_code=413)
        except ValueError:
            return HTMLResponse("Invalid request length", status_code=400)
        origin = request.headers.get("origin")
        if origin and urlparse(origin).netloc != request.headers.get("host"):
            return HTMLResponse("Please submit this form from the Raven page.", status_code=403)
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "same-origin"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Cache-Control"] = "no-store"
    return response


@app.exception_handler(HTTPException)
async def http_error(request, exc):
    response = page(request, "error.html", message=exc.detail)
    response.status_code = exc.status_code
    return response


def limit(request, bucket, maximum, window):
    ip = request.client.host if request.client else "local"
    if ip in {"127.0.0.1", "::1"}:
        ip = request.headers.get("cf-connecting-ip", ip)
    now = time.time()
    with RATE_LOCK:
        q = RATE[bucket + ":" + ip]
        while q and now - q[0] > window:
            q.popleft()
        if len(q) >= maximum:
            raise HTTPException(429, "The Ravens need a breather. Please try again later.")
        q.append(now)


def submission(request, sid):
    if not signed_cookie(request, "latent_" + sid, sid):
        raise HTTPException(403, "This private round belongs to another browser. Start your own round.")
    with connect() as c:
        row = c.execute("SELECT * FROM submissions WHERE id=?", (sid,)).fetchone()
    if not row:
        raise HTTPException(404, "This round could not be found.")
    return dict(row)


def result_of(row):
    if row["status"] != "ready":
        raise HTTPException(409, "The Ravens are still reading. Wait for your round to finish.")
    return PanelResult.model_validate_json(row["result"])


def find_skill(result, skill_id):
    for skill in result.skills:
        if skill.skill_id == skill_id:
            return skill
    raise HTTPException(404, "Skill not found in this round.")


def demo_panel(sid):
    panel = fake_panel(sid)
    # The contract fixture has two skills; provide a third visibly synthetic stage card.
    panel.skills.append(PanelSkill(skill_id="sql", name="SQL", family="data", scale_max=3,
        level_lines={"1": "Writes a query with filtering and joins in a guided exercise.",
                     "2": "Independently writes and maintains SQL queries for a working service.",
                     "3": "Reviews query designs and teaches performance practices adopted by the team."},
        judges=[JudgeScore(judge=j, action="send", level=2, quote="Maintained reporting queries for the weekly product dashboard.",
                           source_id="demo_cv", reason="Synthetic example for the demo.") for j in JUDGES]))
    kafka = panel.skills[1]
    kafka.level_lines = {"1": "Explains topics, partitions and consumer groups in an exercise.",
                         "2": "Adds a Kafka producer or consumer with reviewer guidance.",
                         "3": "Independently operates Kafka integrations and resolves delivery faults.",
                         "4": "Reviews event-stream designs and teaches reliability patterns adopted by others."}
    return panel


def resolve(value):
    return asyncio.run(value) if inspect.isawaitable(value) else value


def run_submission(sid, cv_bytes, cv_text, github_user, portfolio_url):
    demo, notice = False, ""
    if os.environ.get("LATENT_FAKE_PANEL", "").lower() in {"1", "true", "yes"}:
        panel, demo = demo_panel(sid), True
        notice = "Demo mode is on (LATENT_FAKE_PANEL=1) · These skills are synthetic, not an assessment of your documents."
    else:
        try:
            from imocha_raven.intake import bundle_from_upload
            from imocha_raven.pipeline import run_panel
            from imocha_raven.load import load_taxonomy
            bundle = resolve(bundle_from_upload(person_ref=sid, cv_bytes=cv_bytes or None,
                             cv_text=cv_text or None, github_user=github_user or None, portfolio_url=portfolio_url or None))
            panel = PanelResult.model_validate(resolve(run_panel(bundle, load_taxonomy())))
            panel.skills = panel.skills[:5]
        except Exception:
            # A real person never gets fake skills. Traceback goes to a gitignored local file only.
            ERROR_LOG.parent.mkdir(parents=True, exist_ok=True)
            with ERROR_LOG.open("a") as f:
                f.write(f"\n--- {sid} {time.strftime('%Y-%m-%d %H:%M:%S')}\n{traceback.format_exc()}")
            LOG.warning("Panel failed for %s; see %s", sid, ERROR_LOG)
            with connect() as c:
                c.execute("UPDATE submissions SET status='interrupted', notice=? WHERE id=?",
                          ("The Ravens hit an error reading your evidence. Nothing was scored. Please try again.", sid))
            return
        if not panel.skills:
            notice = "The Ravens found no skills from the customer skill list in your evidence. Add a GitHub username or portfolio link and try again."
    with connect() as c:
        c.execute("UPDATE submissions SET status='ready', result=?, demo=?, notice=? WHERE id=?",
                  (panel.model_dump_json(), int(demo), notice, sid))


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return page(request, "home.html")


@app.get("/play", response_class=HTMLResponse)
def play(request: Request):
    return page(request, "play.html", error=None)


@app.post("/play")
async def start(request: Request):
    limit(request, "attempt", 30, 600)
    form = await request.form(max_files=1, max_fields=12, max_part_size=MAX_FILE)
    def invalid(message):
        response = page(request, "play.html", error=message)
        response.status_code = 400
        return response
    if not hmac.compare_digest(str(form.get("passcode", "")), os.environ.get("LATENT_PASSCODE", "raven")):
        return invalid("That passcode didn’t match. Ask your organiser for the code.")
    name = str(form.get("first_name", "")).strip()
    if not name or len(name) > 40 or any(ord(ch) < 32 for ch in name):
        return invalid("Please enter a first name, up to 40 characters.")
    if form.get("consent") != "yes":
        return invalid("Please tick the consent box before sending your evidence.")
    cv_text = str(form.get("cv_text", "")).strip()
    if len(cv_text) > 100_000:
        return invalid("Please keep pasted text under 100,000 characters.")
    upload, cv_bytes = form.get("cv"), b""
    if upload and getattr(upload, "filename", ""):
        cv_bytes = await upload.read(MAX_FILE + 1)
        await upload.close()
        if len(cv_bytes) > MAX_FILE:
            return invalid("The PDF must be 5 MB or smaller.")
        if not upload.filename.lower().endswith(".pdf") or not cv_bytes.startswith(b"%PDF-"):
            return invalid("Please upload a PDF, or paste your CV as plain text.")
    if not cv_bytes and not cv_text:
        return invalid("Upload a CV PDF or paste some evidence to start.")
    github = str(form.get("github_user", "")).strip()
    portfolio = str(form.get("portfolio_url", "")).strip()
    if github and not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?", github):
        return invalid("Use a GitHub username, without the github.com URL.")
    if portfolio:
        parsed = urlparse(portfolio)
        host = parsed.hostname or ""
        try:
            is_private = not ipaddress.ip_address(host).is_global
        except ValueError:
            is_private = "." not in host or host.endswith((".local", ".localhost", ".internal"))
        if len(portfolio) > 1000 or parsed.scheme != "https" or parsed.username or parsed.password or is_private:
            return invalid("Use a public https:// portfolio URL.")
    limit(request, "submission", 6, 3600)
    sid, now = secrets.token_hex(16), time.time()
    UPLOADS.mkdir(parents=True, exist_ok=True)
    os.chmod(UPLOADS, 0o700)
    if cv_bytes:
        path = UPLOADS / (sid + ".pdf")
        path.write_bytes(cv_bytes)
        path.chmod(0o600)
    if cv_text:
        path = UPLOADS / (sid + ".txt")
        path.write_text(cv_text)
        path.chmod(0o600)
    with connect() as c:
        c.execute("INSERT INTO submissions(id,first_name,created,consent_at,status) VALUES (?,?,?,?,?)",
                  (sid, name, now, now, "running"))
        c.execute("INSERT OR REPLACE INTO leaderboard VALUES (?,?,?)", (sid, name, now))  # everyone plays on the leaderboard
    POOL.submit(run_submission, sid, cv_bytes, cv_text, github, portfolio)
    response = RedirectResponse(f"/play/{sid}", status_code=303)
    set_cookie(response, request, "latent_" + sid, sid)
    return response


@app.get("/play/{sid}", response_class=HTMLResponse)
def round_page(request: Request, sid: str):
    row = submission(request, sid)
    result = result_of(row) if row["status"] == "ready" else None
    with connect() as c:
        ratings = {r["skill_id"]: dict(r) for r in c.execute("SELECT * FROM self_ratings WHERE submission_id=?", (sid,))}
    # The template receives public skill data only. Judge data never enters this response.
    public_skills = [{"skill_id": s.skill_id, "name": s.name, "level_lines": s.level_lines,
                      "scale_max": s.scale_max} for s in result.skills] if result else []
    return page(request, "round.html", row=row, skills=public_skills, ratings=ratings)


@app.get("/play/{sid}/status", response_class=HTMLResponse)
def status(request: Request, sid: str):
    row = submission(request, sid)
    response = page(request, "status.html", row=row)
    if row["status"] == "ready":
        response.headers["HX-Redirect"] = f"/play/{sid}"
    return response


@app.post("/play/{sid}/skills/{skill_id}/lock", response_class=HTMLResponse)
async def lock_rating(request: Request, sid: str, skill_id: str):
    row = submission(request, sid)
    skill = find_skill(result_of(row), skill_id)
    form = await request.form()
    try:
        level = int(str(form.get("level", "")))
    except ValueError:
        raise HTTPException(400, "Choose a level before locking your rating.")
    if level < 1 or level > skill.scale_max or str(level) not in skill.level_lines:
        raise HTTPException(400, "Choose one of the listed levels.")
    with connect() as c:
        c.execute("INSERT OR IGNORE INTO self_ratings VALUES (?,?,?,?)", (sid, skill_id, level, time.time()))
        rating = c.execute("SELECT * FROM self_ratings WHERE submission_id=? AND skill_id=?", (sid, skill_id)).fetchone()
    # No judge information in the lock response, either: a separate authenticated GET reveals it.
    return page(request, "locked.html", sid=sid, skill=skill, rating=rating)


@app.get("/play/{sid}/skills/{skill_id}/reveal", response_class=HTMLResponse)
def reveal(request: Request, sid: str, skill_id: str):
    row = submission(request, sid)
    panel = result_of(row)
    skill = find_skill(panel, skill_id)
    with connect() as c:
        rating = c.execute("SELECT * FROM self_ratings WHERE submission_id=? AND skill_id=?", (sid, skill_id)).fetchone()
        if not rating:
            raise HTTPException(403, "Lock your self-rating before meeting the panel.")
        avg, spread = panel_average(skill)
        outcome = verdict(rating["level"], skill)
        c.execute("INSERT OR IGNORE INTO reveals VALUES (?,?,?,?,?)", (sid, skill_id, time.time(), outcome, avg))
        answer = c.execute("SELECT * FROM answers WHERE submission_id=? AND skill_id=?", (sid, skill_id)).fetchone()
    missing = next((x.get("missing_source") for x in panel.abstained if x.get("skill_id") == skill_id), None)
    return page(request, "reveal.html", sid=sid, skill=skill, rating=rating, avg=avg, spread=spread,
                outcome=outcome, missing=missing or "a work sample, a repository, or an assessment", answer=answer, demo=row["demo"])


@app.post("/play/{sid}/skills/{skill_id}/feedback", response_class=HTMLResponse)
async def feedback(request: Request, sid: str, skill_id: str):
    row = submission(request, sid)
    find_skill(result_of(row), skill_id)
    form = await request.form()
    has_skill, level_feedback = str(form.get("has_skill", "")), str(form.get("level_feedback", ""))
    if has_skill not in {"yes", "no"} or level_feedback not in {"too_low", "right", "too_high", "unscored"}:
        raise HTTPException(400, "Please answer both questions.")
    with connect() as c:
        if not c.execute("SELECT 1 FROM reveals WHERE submission_id=? AND skill_id=?", (sid, skill_id)).fetchone():
            raise HTTPException(403, "Meet the panel before giving feedback.")
        c.execute("INSERT OR REPLACE INTO answers VALUES (?,?,?,?,?)", (sid, skill_id, has_skill, level_feedback, time.time()))
    response = page(request, "thanks.html")
    response.headers["HX-Trigger"] = "feedbackSaved"
    return response


@app.get("/play/{sid}/finish", response_class=HTMLResponse)
def finish_partial(request: Request, sid: str):
    row = submission(request, sid)
    panel = result_of(row)
    with connect() as c:
        completed = c.execute("SELECT COUNT(*) FROM answers WHERE submission_id=?", (sid,)).fetchone()[0]
        missed = c.execute("SELECT text FROM missed WHERE submission_id=?", (sid,)).fetchone()
        opted = c.execute("SELECT 1 FROM leaderboard WHERE submission_id=?", (sid,)).fetchone()
    return page(request, "finish.html", sid=sid, panel=panel, completed=completed, missed=missed, opted=opted)


@app.post("/play/{sid}/finish", response_class=HTMLResponse)
async def finish(request: Request, sid: str):
    row = submission(request, sid)
    panel = result_of(row)
    form = await request.form()
    text = str(form.get("missed", "")).strip()
    if len(text) > 5000:
        raise HTTPException(400, "Keep your feedback under 5,000 characters.")
    with connect() as c:
        completed = c.execute("SELECT COUNT(*) FROM answers WHERE submission_id=?", (sid,)).fetchone()[0]
        if completed < len(panel.skills):
            raise HTTPException(409, "Please give quick feedback on every skill before finishing.")
        c.execute("INSERT OR REPLACE INTO missed VALUES (?,?,?)", (sid, text, time.time()))
        c.execute("INSERT OR REPLACE INTO leaderboard VALUES (?,?,?)", (sid, row["first_name"], time.time()))
    return page(request, "finished.html")


def read_json(path, default):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return default


def leaderboard_rows():
    with connect() as c:
        return [dict(r) for r in c.execute("""SELECT l.first_name, AVG(ABS(s.level-r.panel)) AS gap, COUNT(*) AS skills
            FROM leaderboard l JOIN self_ratings s ON s.submission_id=l.submission_id
            JOIN reveals r ON r.submission_id=s.submission_id AND r.skill_id=s.skill_id
            JOIN submissions u ON u.id=l.submission_id
            WHERE r.panel IS NOT NULL AND r.verdict!='panel_abstains' AND u.demo=0
            GROUP BY l.submission_id ORDER BY gap ASC, l.opted_at ASC LIMIT 20""")]


@app.get("/leaderboard", response_class=HTMLResponse)
def leaderboard(request: Request):
    return page(request, "leaderboard.html", leaders=leaderboard_rows())


def dashboard_auth(request):
    return signed_cookie(request, "latent_dashboard", "organiser")


@app.post("/scoreboard/login")
async def dashboard_login(request: Request):
    limit(request, "dashboard", 20, 600)
    form = await request.form()
    if not hmac.compare_digest(str(form.get("passcode", "")), os.environ.get("LATENT_PASSCODE", "raven")):
        response = page(request, "dashboard_gate.html", error="That passcode didn’t match.")
        response.status_code = 403
        return response
    response = RedirectResponse("/scoreboard", status_code=303)
    set_cookie(response, request, "latent_dashboard", "organiser")
    return response


def stats():
    with connect() as c:
        submissions = c.execute("SELECT COUNT(*) FROM submissions WHERE demo=0 AND status='ready'").fetchone()[0]
        demo_count = c.execute("SELECT COUNT(*) FROM submissions WHERE demo=1").fetchone()[0]
        answers = c.execute("SELECT COUNT(*), SUM(a.has_skill='yes') FROM answers a JOIN submissions s ON s.id=a.submission_id WHERE s.demo=0").fetchone()
        winners = c.execute("SELECT COUNT(*) FROM reveals r JOIN submissions s ON s.id=r.submission_id WHERE s.demo=0 AND r.verdict='latent_winner'").fetchone()[0]
    return dict(submissions=submissions, demo_count=demo_count, answers=answers[0],
                yes_rate=(round(100 * (answers[1] or 0) / answers[0]) if answers[0] else None), winners=winners)


def panel_files():
    """Projected picker: names only for synthetic people and consenting players.

    Keep the existing directory:id values, including real:<random submission id>.
    A submission's saved panel is authoritative even if no run file was written.
    """
    files, live = {}, {}
    with connect() as c:
        rows = c.execute("""SELECT s.*, l.submission_id AS opted_in FROM submissions s
            LEFT JOIN leaderboard l ON l.submission_id=s.id
            WHERE s.status='ready' AND s.result IS NOT NULL ORDER BY s.created, s.id""").fetchall()
    for number, row in enumerate(rows, 1):
        try:
            panel = PanelResult.model_validate_json(row["result"])
        except ValueError:
            continue
        name = row["first_name"] if row["opted_in"] else f"Player {number}"
        label = f"{name} · played {time.strftime('%H:%M', time.localtime(row['created']))}"
        live[row["id"]] = dict(panel=panel, label=label, group="Live players")
    # Match saved run references back to their submission, never display a raw id.
    refs = {entry["panel"].person_ref: sid for sid, entry in live.items()}
    matched = set()
    index = read_json(ROOT / "data/real/index.json", [])
    roles = {r.get("rid"): r.get("role_family", "") for r in index if isinstance(r, dict)} if isinstance(index, list) else {}
    role_names = {"design": "Product designer", "data_ai": "Data & AI",
                  "solutions_payments": "Solutions & payments", "mechanical": "Mechanical engineering",
                  "civil": "Civil engineering"}
    for directory in (LATEST / "per_person", LATEST / "real"):
        for path in sorted(directory.glob("*.json")):
            try:
                panel = PanelResult.model_validate_json(path.read_text())
            except (OSError, ValueError):
                continue
            key, pid = path.parent.name + ":" + path.stem, path.stem
            sid = pid if pid in live else refs.get(panel.person_ref)
            if sid:
                files[key] = live[sid]
                matched.add(sid)
            elif directory.name == "per_person" and re.fullmatch(r"P\d{3}", pid):
                hcm = read_json(ROOT / "data/bundles" / pid / "hcm.json", {})
                if not isinstance(hcm, dict):
                    hcm = {}
                name = hcm.get("preferred_name") or hcm.get("legal_name") or pid
                history = [job for job in hcm.get("job_history", []) if isinstance(job, dict)]
                history.sort(key=lambda job: (not job.get("to"), job.get("from") or ""))
                title = history[-1].get("title", "Synthetic employee") if history else "Synthetic employee"
                files[key] = dict(panel=panel, label=f"{name} · {title}", group="Synthetic employees")
            elif directory.name == "real" and re.fullmatch(r"R\d{3}", pid):
                role = roles.get(pid) or "Pilot employee"
                role = role_names.get(role, role.replace("_", " ").capitalize())
                files[key] = dict(panel=panel, label=f"{pid} · {role} (real pilot)", group="Real pilot")
    for sid, entry in live.items():
        if sid not in matched:
            files["real:" + sid] = entry
    return files


RULE_NAMES = {"not_high": "Not enough independent proof", "no_floor": "No level backed twice",
              "spread": "Evidence disagrees by 3+ levels", "measured_conflict": "Test result contradicted",
              "decay": "Evidence too old", "send": "Independent proof agrees"}
TRACE_CAPTIONS = {"raven1": "One LLM read of everything. No rules, no checks.",
                  "raven2": "Independent proof sets a floor; rules decide send or hold.",
                  "raven3": "Discount dependence, weigh levels, then clear a calibrated threshold."}


def trace_view(judge, scale_max=4):
    """Presentation only: expose recorded values, never re-run engine decisions."""
    trace = judge.trace or {}
    records = [r for r in trace.get("records", []) or [] if isinstance(r, dict)]
    evidence = [e for e in trace.get("evidence", []) or [] if isinstance(e, dict)]
    # A compact example should show the dependence discounts even when the
    # highest-weight evidence occupies the first few entries in the saved trace.
    compact_indices = [0] if evidence else []
    for discount in (0, 0.3):
        index = next((i for i, e in enumerate(evidence) if e.get("discount") == discount), None)
        if index is not None and index not in compact_indices:
            compact_indices.append(index)
    compact_indices += [i for i in range(len(evidence)) if i not in compact_indices]
    groups = ("measured", "work", "authored", "org", "third_party", "self", "training")
    lanes = [dict(name=g, records=[r for r in records if r.get("group") == g]) for g in groups]
    return dict(judge=judge, trace=trace, available=bool(trace),
                scale_max=trace.get("scale_max") or scale_max,
                lanes=lanes, evidence=evidence, compact_evidence=[evidence[i] for i in compact_indices[:3]],
                caption=TRACE_CAPTIONS.get(judge.judge, ""),
                rule=RULE_NAMES.get(trace.get("rule"), str(trace.get("rule") or "Rule not recorded").replace("_", " ").capitalize()))


def trace_examples(people):
    """Use synthetic run examples only; no live player's evidence on the intro."""
    candidates = {j: [] for j in JUDGES}
    for key, entry in people.items():
        if entry["group"] != "Synthetic employees":
            continue
        for skill in entry["panel"].skills:
            for judge in skill.judges:
                if judge.judge in candidates and judge.trace:
                    trace = judge.trace
                    interest = (int(trace.get("quote_in_source") is False) if judge.judge == "raven1" else
                                int(judge.action == "hold") + 2 * int(trace.get("floor") is not None and trace.get("ceiling") is not None) if judge.judge == "raven2" else
                                sum(e.get("discount") in (0, 0.3) for e in trace.get("evidence", []) if isinstance(e, dict)))
                    candidates[judge.judge].append((interest, key, skill, judge))
    # Explicitly labelled illustrative fallback when runs are missing or predate traces.
    illustrative = {
        "raven1": dict(confidence=.88, level=4, quote_in_source=False),
        "raven2": dict(rule="send", window_years=2, records=[dict(group="work", level=3, type="applied"), dict(group="authored", level=3, type="authored_doc")], groups=["work", "authored"], establishing=["work", "authored"], measured=0, work_months=8, floor=3, ceiling=4, scale_max=4),
        "raven3": dict(evidence=[dict(type="applied", group="work", q=.8, discount=1, weight=.8, level=3), dict(type="applied", group="work", q=.8, discount=0, weight=0, level=3), dict(type="authored_doc", group="authored", q=.7, discount=.3, weight=.21, level=3)], p_has=.84, level_dist=[.02, .1, .76, .12], best=3, accepted=[2, 3, 4], p_yes=.82, tau=.61, shift=1),
    }
    examples = []
    for name in JUDGES:
        if candidates[name]:
            _, key, skill, judge = max(candidates[name], key=lambda row: row[0])
            view = trace_view(judge, skill.scale_max)
            view["example"] = f"{key.split(':', 1)[1]} · {skill.name} · recorded trace"
        else:
            view = trace_view(JudgeScore(judge=name, action="send", level=3 if name != "raven1" else 4, trace=illustrative[name]))
            view["example"] = "Illustrative example · not a benchmark result"
        examples.append(view)
    return examples


def probability(value):
    return "—" if value is None else f"{float(value):.2%}"


templates.env.globals.update(trace_view=trace_view, probability=probability)


def build_log():
    try:
        text = (ROOT / "data/notes/00-dataset-status.md").read_text()
    except OSError:
        return []
    section = text.split("## Build log", 1)
    if len(section) < 2:
        return []
    rows = []
    for line in section[1].splitlines():
        if line.startswith("|"):
            cells = [s.strip() for s in line.strip("|").split("|")]
            if len(cells) >= 3 and not all(set(s) <= {"-", ":", " "} for s in cells):
                rows.append(cells[:3])
    return rows[1:]


def trap_rows():
    raw = read_json(LATEST / "traps.json", [])
    if isinstance(raw, list) and raw and isinstance(raw[0], dict) and "engine" in raw[0]:
        # eval writes one row per (trap, engine); pivot to one row per trap, test half only like summary.json
        pivot = {}
        for r in raw:
            if r.get("split", "test") != "test":
                continue
            key = (r.get("pid"), r.get("skill_id"), r.get("s11_row"))
            pivot.setdefault(key, {})[r.get("engine")] = r.get("caught")
        return [dict(name=f"{pid} · {skill or '-'} · {(row or '').replace('_', ' ')}",
                     cells=[cells.get(j) for j in JUDGES]) for (pid, skill, row), cells in sorted(pivot.items(), key=str)]
    if isinstance(raw, dict):
        raw = raw.get("traps", raw.get("rows", raw))
        if isinstance(raw, dict):
            raw = [dict(name=k, results=v) for k, v in raw.items()]
    rows = []
    for item in raw if isinstance(raw, list) else []:
        if not isinstance(item, dict):
            continue
        values = item.get("engines", item.get("results", item.get("caught", item)))
        if isinstance(values, list):
            values = {v.get("judge", ""): v.get("caught") for v in values if isinstance(v, dict)}
        if not isinstance(values, dict):
            values = item
        cells = []
        for judge in JUDGES:
            value = values.get(judge)
            if isinstance(value, dict):
                value = value.get("caught", value.get("passed"))
            cells.append(True if value is True or value in ("caught", "pass", "passed") else False if value is False or value in ("missed", "fail", "failed") else None)
        rows.append(dict(name=item.get("name", item.get("trap", item.get("trap_id", "Trap"))), cells=cells))
    return rows


@app.get("/scoreboard", response_class=HTMLResponse)
def scoreboard(request: Request):
    if not dashboard_auth(request):
        return page(request, "dashboard_gate.html", error=None)
    scores = []
    summary = read_json(LATEST / "summary.json", [])
    for row in summary if isinstance(summary, list) else []:
        try:
            scores.append(EngineScore.model_validate(row))
        except ValueError:
            continue
    curve = read_json(LATEST / "curve.json", [])
    if isinstance(curve, dict):
        curve = curve.get("curves", {}).get("raven3", {}).get("all") or curve.get("raven3", curve.get("points", []))
    points = []
    for p in curve if isinstance(curve, list) else []:
        try:
            points.append(dict(tau=float(p["tau"]), precision=max(0, min(1, float(p["precision"]))), coverage=max(0, min(1, float(p["coverage"])))))
        except (KeyError, ValueError, TypeError):
            continue
    points.sort(key=lambda p: p["coverage"])
    curve_path = " ".join(f"{55 + p['coverage'] * 600:.1f},{235 - p['precision'] * 200:.1f}" for p in points)
    people = panel_files()
    people_groups = [dict(label=group, options=[dict(value=key, label=entry["label"]) for key, entry in people.items() if entry["group"] == group])
                     for group in ("Live players", "Real pilot", "Synthetic employees")]
    return page(request, "scoreboard.html", scores=scores, curve=points, curve_path=curve_path,
                traps=trap_rows(), people=people, people_groups=people_groups, examples=trace_examples(people),
                stats=stats(), build_log=build_log())


@app.get("/scoreboard/stats", response_class=HTMLResponse)
def live_stats(request: Request):
    if not dashboard_auth(request):
        raise HTTPException(403, "Unlock the organiser dashboard first.")
    return page(request, "stats.html", stats=stats())


@app.get("/scoreboard/person", response_class=HTMLResponse)
def person(request: Request, person: str = ""):
    if not dashboard_auth(request):
        raise HTTPException(403, "Unlock the organiser dashboard first.")
    files = panel_files()
    if person not in files:
        return page(request, "person.html", panel=None, messages=[])
    panel = files[person]["panel"]
    messages = []
    for skill in panel.skills:
        decision = next((j for j in skill.judges if j.judge == "raven3"), None)
        if decision and decision.action == "send" and decision.level is not None:
            quotes = list(dict.fromkeys((j.quote, j.source_id) for j in skill.judges if j.quote and j.judge == "raven3"))[:3]
            messages.append(dict(name=skill.name, level=decision.level, level_name=skill.level_lines.get(str(decision.level), ""), quotes=quotes))
    return page(request, "person.html", panel=panel, person_label=files[person]["label"], messages=messages[:3])
