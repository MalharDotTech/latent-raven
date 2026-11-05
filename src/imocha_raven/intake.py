"""Live intake: CV upload / text, GitHub username, portfolio URL -> a real bundle on disk."""

import json
import os
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


def _gh_token() -> str | None:
    tok = os.environ.get("GITHUB_TOKEN")
    if tok:
        return tok
    try:  # organiser's local gh login; only public endpoints are read
        return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, timeout=5).stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def _gh(path: str, raw: bool = False):
    h = dict(UA)
    if raw:
        h["Accept"] = "application/vnd.github.raw"
    if tok := _gh_token():
        h["Authorization"] = f"Bearer {tok}"
    body = _get(f"https://api.github.com{path}", h)
    return body.decode("utf-8", errors="replace") if raw else json.loads(body)


def github_snapshot(user: str, top: int = 8) -> str:
    """Public GitHub as plain lines: profile, top own repos (languages, own commits, README), merged PRs elsewhere."""
    user = re.sub(r"[^A-Za-z0-9-]", "", user)[:39]
    prof = _gh(f"/users/{user}")
    out = [f"# GitHub {prof['login']}", f"profile: name={prof.get('name')} | bio={prof.get('bio')} | public_repos="
           f"{prof.get('public_repos')} | joined={(prof.get('created_at') or '')[:10]}", ""]
    repos = [r for r in _gh(f"/users/{user}/repos?per_page=100&sort=pushed&type=owner") if not r.get("fork")]
    for r in repos[:top]:
        full = r["full_name"]
        langs = _gh(f"/repos/{full}/languages")
        commits = []
        try:
            commits = _gh(f"/repos/{full}/commits?author={user}&per_page=100")
        except Exception:
            pass
        dates = sorted((c["commit"]["author"]["date"] or "")[:10] for c in commits if c.get("commit"))
        months = sorted({d[:7] for d in dates})
        msgs = [c["commit"]["message"].split("\n")[0][:100] for c in commits[:4]]
        try:
            readme = re.sub(r"\s+", " ", _gh(f"/repos/{full}/readme", raw=True))[:900]
        except Exception:
            readme = ""
        out += [f"repo: {full} | description={r.get('description')} | stars={r.get('stargazers_count', 0)} | "
                f"created={(r.get('created_at') or '')[:10]} | pushed={(r.get('pushed_at') or '')[:10]} | topics={r.get('topics', [])}",
                f"  languages_bytes: {langs}",
                f"  own_commits: {len(commits)}{'+' if len(commits) == 100 else ''} | first={dates[0] if dates else None} | "
                f"last={dates[-1] if dates else None} | active_months={len(months)}",
                f"  recent_commit_messages: {msgs}",
                f"  readme: {readme}", ""]
    if len(repos) > top:
        out.append("other_repos: " + ", ".join(f"{r['name']} ({r.get('language')})" for r in repos[top:40]))
    try:
        prs = _gh(f"/search/issues?q=author:{user}+type:pr+is:merged+-user:{user}&per_page=20&sort=updated")
        for it in prs.get("items", []):
            repo = it["repository_url"].split("/repos/")[-1]
            out.append(f"merged_pr: {repo}#{it['number']} | {it['title'][:120]} | merged={(it.get('closed_at') or '')[:10]}")
    except Exception:
        pass
    return "\n".join(out)


def portfolio_pages(url: str, max_pages: int = 8) -> str:
    """Homepage plus same-site pages it links to (case studies first)."""
    from urllib.parse import urljoin, urlparse
    host = urlparse(url).netloc
    first = _get(url).decode("utf-8", errors="replace")
    links = []
    for href in re.findall(r'href=["\']([^"\'#]+)', first):
        u = urljoin(url, href)
        if urlparse(u).netloc == host and u.rstrip("/") != url.rstrip("/") and not re.search(r"\.(png|jpe?g|svg|css|js|pdf|ico)$", u, re.I):
            links.append(u)
    rank = lambda u: (0 if re.search(r"work|case|project|portfolio|source", u, re.I) else 1, len(u))
    pages, seen = [(url, first)], {url.rstrip("/")}
    for u in sorted(dict.fromkeys(links), key=rank):
        if len(pages) >= max_pages:
            break
        if u.rstrip("/") in seen:
            continue
        seen.add(u.rstrip("/"))
        try:
            html = _get(u).decode("utf-8", errors="replace")
        except Exception:
            continue
        pages.append((u, html))
        for href in re.findall(r'href=["\']([^"\'#]*source[^"\'#]*)', html):  # "full case study" sub-pages
            v = urljoin(u, href)
            if urlparse(v).netloc == host and v.rstrip("/") not in seen and len(pages) < max_pages:
                seen.add(v.rstrip("/"))
                try:
                    pages.append((v, _get(v).decode("utf-8", errors="replace")))
                except Exception:
                    pass
    return "\n\n".join(f"## Page {u}\n\n{html_to_text(h)[:12000]}" for u, h in pages)


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
            login = re.sub(r"[^A-Za-z0-9-]", "", github_user.strip().lstrip("@").rstrip("/").split("/")[-1])
            (d / "github.md").write_text(github_snapshot(login)[:MAX_TEXT])
            sources.append({"source_id": f"gh_{login}", "source_type": "github_public", "path": "github.md", "received": today})
        except Exception as e:
            (d / "intake_errors.txt").write_text(f"github: {e}\n")
    if portfolio_url:
        try:
            url = portfolio_url if portfolio_url.startswith("http") else "https://" + portfolio_url
            page = portfolio_pages(url)[:MAX_TEXT]
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
