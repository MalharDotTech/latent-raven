"""Live intake: CV upload / text, GitHub username, portfolio URL -> a real bundle on disk."""

import json
import re
import subprocess
import tempfile
import urllib.request
from datetime import date
from html import unescape
from pathlib import Path

from .load import REAL, load_bundle
from .types import Bundle

MAX_TEXT = 60000
UA = {"User-Agent": "raven-intake/0.1", "Accept": "application/vnd.github+json"}


def _get(url: str, headers: dict | None = None, limit: int = 2_000_000) -> bytes:
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "Mozilla/5.0 raven-intake"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read(limit)


def pdf_to_text(data: bytes) -> str:
    with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
        f.write(data)
        f.flush()
        p = subprocess.run(["/opt/homebrew/bin/pdftotext", "-layout", f.name, "-"], capture_output=True, text=True, timeout=60)
    return p.stdout


def html_to_text(html: str) -> str:
    html = re.sub(r"(?is)<(script|style|noscript|svg)\b.*?</\1>", " ", html)
    html = re.sub(r"(?i)<(br|/p|/div|/li|/h\d|/tr)\s*/?>", "\n", html)
    t = unescape(re.sub(r"<[^>]+>", " ", html))
    t = re.sub(r"[ \t\f\r]+", " ", t)
    return re.sub(r"\n\s*\n+", "\n\n", t).strip()


def github_snapshot(user: str) -> dict:
    user = re.sub(r"[^A-Za-z0-9-]", "", user)[:39]
    base = "https://api.github.com"
    repos = json.loads(_get(f"{base}/users/{user}/repos?per_page=50&sort=pushed", UA))
    ev = json.loads(_get(f"{base}/users/{user}/events/public?per_page=60", UA))
    out = {"login": user, "account_type": "public", "public_profile": {"personal_repos": [
        {"name": r["name"], "description": r.get("description"), "language": r.get("language"), "topics": r.get("topics", []),
         "fork": r["fork"], "pushed": (r.get("pushed_at") or "")[:10], "stars": r.get("stargazers_count", 0)}
        for r in repos if isinstance(r, dict)][:40]}, "events": []}
    for e in ev if isinstance(ev, list) else []:
        p = e.get("payload", {})
        item = {"type": e.get("type"), "repo": e.get("repo", {}).get("name"), "date": (e.get("created_at") or "")[:10]}
        if e.get("type") == "PushEvent":
            item["commits"] = [c["message"].split("\n")[0][:120] for c in p.get("commits", [])[:3]]
        elif e.get("type") == "PullRequestEvent":
            pr = p.get("pull_request", {})
            item.update(action=p.get("action"), title=pr.get("title"), merged=pr.get("merged"))
        elif e.get("type") == "PullRequestReviewEvent":
            item["state"] = p.get("review", {}).get("state")
        out["events"].append(item)
    return out


def bundle_from_upload(person_ref: str, cv_bytes: bytes | None = None, cv_text: str | None = None,
                       github_user: str | None = None, portfolio_url: str | None = None,
                       filename: str | None = None) -> Bundle:
    ref = re.sub(r"[^A-Za-z0-9_-]", "", person_ref) or "R999"
    d = REAL / ref
    (d / "docs").mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    sources = []
    text = cv_text
    if cv_bytes:
        is_pdf = cv_bytes[:4] == b"%PDF" or (filename or "").lower().endswith(".pdf")
        text = pdf_to_text(cv_bytes) if is_pdf else cv_bytes.decode("utf-8", errors="replace")
    if text and text.strip():
        (d / "cv_v1.md").write_text(text[:MAX_TEXT])
        sources.append({"source_id": f"cv_{ref}_1", "source_type": "cv", "path": "cv_v1.md", "received": today,
                        "lineage_key": f"cv-{ref}"})
    if github_user:
        try:
            snap = github_snapshot(github_user.strip().lstrip("@").rstrip("/").split("/")[-1])
            (d / "github.json").write_text(json.dumps(snap, indent=1)[:MAX_TEXT])
            sources.append({"source_id": f"gh_{snap['login']}", "source_type": "github", "path": "github.json", "received": today})
        except Exception as e:
            (d / "intake_errors.txt").write_text(f"github: {e}\n")
    if portfolio_url:
        try:
            url = portfolio_url if portfolio_url.startswith("http") else "https://" + portfolio_url
            page = html_to_text(_get(url).decode("utf-8", errors="replace"))[:MAX_TEXT]
            if page:
                (d / "docs" / "portfolio.md").write_text(f"# Portfolio {url}\n\n{page}")
                sources.append({"source_id": f"authored_doc_{ref}_portfolio", "source_type": "authored_doc",
                                "path": "docs/portfolio.md", "received": today})
        except Exception as e:
            with open(d / "intake_errors.txt", "a") as f:
                f.write(f"portfolio: {e}\n")
    (d / "manifest.json").write_text(json.dumps({"person_ref": ref, "customer": "real-pilot", "as_of": today,
                                                 "sources": sources}, indent=1))
    return load_bundle(d)
