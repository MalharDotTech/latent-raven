"""Validate generated persona bundles against data/spec/PERSONA_SPEC.md.

Usage: python3 -I scripts/validate_personas.py [PID ...]
Exit code 1 if any ERROR. WARNs are printed but do not fail.
"""

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# Isolated Python (-I) omits the script directory from sys.path.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from persona_structure import (JIRA_PROJECTS, STRAY_PROJECTS, iso_day, ledgerly_violations,
                               linked_tickets, monthly_floors, records)
DATA = ROOT / "data"
AS_OF = "2026-10-31"
SOURCE_TYPES = {"hcm", "cv", "github", "jira", "servicenow", "salesforce", "certs", "lms", "assessments", "authored_doc"}
SLOP_WORDS = ["spearheaded", "leveraged", "synergy", "passionate", "dynamic", "results-driven", "cutting-edge"]
LEAK_PATTERNS = [r"true_level", r"would_accept", r"has_skill", r"expected_engine_behavior", r"fault_id", r"\bF\d{2}\b",
                 r"(?i)\bsynthetic\b", r"(?i)\bplanted\b", r"(?i)\bfictional\b"]
DATE_RE = re.compile(r"\b(20\d{2})-(\d{2})(?:-(\d{2}))?\b")


def load_json(path, errors):
    try:
        return json.loads(path.read_text())
    except Exception as e:
        errors.append(f"{path.relative_to(ROOT)}: invalid JSON ({e})")
        return None


def taxonomy_index():
    path = DATA / "taxonomy" / "customer_taxonomy.json"
    if not path.exists():
        return None, None
    tax = json.loads(path.read_text())
    scales = {s["scale_id"]: max(l["value"] for l in s["levels"]) for s in tax["scales"]}
    family_scale = {f["family_id"]: f["scale_id"] for f in tax["skill_families"]}
    skills = {s["skill_id"]: scales[family_scale[s["family_id"]]] for s in tax["skills"]}
    return skills, tax


def grounding_names(file, key_candidates):
    path = DATA / "grounding" / file
    if not path.exists():
        return None
    data = json.loads(path.read_text())
    items = data if isinstance(data, list) else next((v for v in data.values() if isinstance(v, list)), [])
    names = set()
    for item in items:
        for k in key_candidates:
            if isinstance(item, dict) and item.get(k):
                names.add(item[k].strip().lower())
    return names


def ngrams(text, n=8):
    words = re.findall(r"[a-z0-9']+", text.lower())
    return {" ".join(words[i:i + n]) for i in range(len(words) - n + 1)}


def coherence_checks(pid, sources, world):
    errors = []
    local_issues = sources.get("jira", {}).get("issues", [])
    # Local ownership disambiguates old duplicated ticket IDs during migration.
    ticket_index = {i["key"]: i for other in world.values() for i in other.get("jira", {}).get("issues", [])}
    ticket_index.update({i["key"]: i for i in local_issues})
    all_issues = [i for other in world.values() for i in other.get("jira", {}).get("issues", [])]
    gh = sources.get("github", {})
    prs = gh.get("pull_requests", [])
    for pr in prs:
        label = f"{pid}: {pr.get('repo')}#{pr.get('number')}"
        created, merged = iso_day(pr.get("created")), iso_day(pr.get("merged"))
        if created and merged and merged < created:
            errors.append(f"{label}: merged {merged} before created {created}")
        for key in linked_tickets(pr, all_issues):
            ticket = ticket_index.get(key)
            opened = iso_day(ticket.get("created")) if ticket else None
            if created and opened and created < opened:
                errors.append(f"{label}: created {created} before referenced ticket {key} ({opened})")
        for field in ("title", "body", "body_excerpt", "issue_key", "ticket"):
            for key in re.findall(r"\b([A-Z][A-Z0-9]*(?:-[A-Z]+)?-\d+)\b", str(pr.get(field, ""))):
                if key.rsplit("-", 1)[0] not in JIRA_PROJECTS | {"KC", "KCC", "LGR", "ADR", "ENG", "ARCH", "ISO", "ORA", "RB"}:
                    errors.append(f"{label}: Jira reference {key} has disallowed project")
    if prs:
        days = Counter(pr.get("created", "")[8:10] for pr in prs if iso_day(pr.get("created")))
        for day, count in days.items():
            if count > .4 * len(prs):
                errors.append(f"{pid}: PR day-of-month {day} holds {count}/{len(prs)} (>40%)")
    for issue in local_issues:
        key = issue.get("key", "")
        if not re.fullmatch(r"(?:" + "|".join(JIRA_PROJECTS) + r")-\d+", key):
            errors.append(f"{pid}: Jira key {key} has disallowed project")
        created, resolved = iso_day(issue.get("created")), iso_day(issue.get("resolved"))
        if created and resolved and resolved < created:
            errors.append(f"{pid}: {key}: resolved before created")
        for assignment in issue.get("assignee_history", []):
            assigned = iso_day(assignment.get("from"))
            if assigned and created and assigned < created:
                errors.append(f"{pid}: {key}: assignee starts before ticket created")
            if assigned and resolved and assigned > resolved:
                errors.append(f"{pid}: {key}: assignee starts after ticket resolved")
    hcm = sources.get("hcm", {})
    own_names = {hcm.get("legal_name"), hcm.get("preferred_name")}
    for source in ("github", "jira", "servicenow", "salesforce"):
        if source not in sources:
            continue
        data = sources[source]
        months = {row["month"]: row for row in data.get("monthly_activity", [])}
        for month, floors in monthly_floors(source, data, own_names).items():
            row = months.get(month, {})
            for metric, floor in floors.items():
                if metric == "authored_merged_prs" and not any("authored_merged_prs" in r for r in months.values()):
                    continue
                if metric.startswith("by_ext:"):
                    actual = row.get("by_ext", {}).get(metric.split(":", 1)[1], 0)
                else:
                    actual = row.get(metric, 0)
                if actual < floor:
                    errors.append(f"{pid}: {source} monthly_activity {month}.{metric}={actual} below listed items ({floor})")
    for source, data in sources.items():
        for context, stamp in ledgerly_violations(data, source):
            errors.append(f"{pid}: Ledgerly mention in {context} dated {stamp} before 2024-03")
    return errors


def cross_persona_checks(world):
    """Compare the selected originals; counterfactual twins are intentional copies."""
    errors = defaultdict(list)
    prs, keys, projects = defaultdict(list), defaultdict(list), defaultdict(list)
    for pid, sources in world.items():
        if not re.fullmatch(r"P\d{3}", pid):
            continue
        for pr in sources.get("github", {}).get("pull_requests", []):
            prs[pr["repo"]].append((pr["created"], pr["number"], pid))
        for issue in sources.get("jira", {}).get("issues", []):
            keys[("jira", issue["key"])].append(pid)
            if iso_day(issue.get("created")) and re.fullmatch(r"[A-Z]+-\d+", issue["key"]):
                prefix, number = issue["key"].rsplit("-", 1)
                projects[prefix].append((issue["created"], int(number), pid))
        for source, field in (("servicenow", "number"), ("salesforce", "opp_id"), ("salesforce", "activity_id")):
            for item in records(sources.get(source, {}), source):
                if field in item:
                    keys[(source, item[field])].append(pid)
    for (source, key), owners in keys.items():
        if len(owners) > 1:
            for pid in set(owners):
                errors[pid].append(f"{pid}: duplicate {source} key {key} in {', '.join(owners)}")
    for repo, rows in prs.items():
        seen = defaultdict(list)
        for stamp, number, pid in rows:
            seen[number].append(pid)
        for number, owners in seen.items():
            if len(owners) > 1:
                for pid in set(owners):
                    errors[pid].append(f"{pid}: duplicate PR {repo}#{number} in {', '.join(owners)}")
    for kind, groups in (("PR", prs), ("Jira", projects)):
        for namespace, rows in groups.items():
            # Equal creation dates have no ordering within the exported day.
            maximum, max_date = -1, None
            by_day = defaultdict(list)
            for stamp, number, pid in rows:
                by_day[stamp].append((number, pid))
            for stamp, entries in sorted(by_day.items()):
                for number, pid in entries:
                    if number <= maximum:
                        errors[pid].append(f"{pid}: {kind} {namespace}#{number} ({stamp}) is not monotonic after #{maximum} ({max_date})")
                if max(n for n, _ in entries) > maximum:
                    maximum, max_date = max(n for n, _ in entries), stamp
    return errors


def validate(pid, skills, cert_names, course_names, world=None):
    errors, warns = [], []
    bdir, tpath = DATA / "bundles" / pid, DATA / "truth" / f"{pid}.json"
    if not bdir.exists():
        return [f"{pid}: missing bundle dir"], []
    if not tpath.exists():
        errors.append(f"{pid}: missing truth file")

    manifest = load_json(bdir / "manifest.json", errors) if (bdir / "manifest.json").exists() else None
    if manifest is None:
        errors.append(f"{pid}: missing manifest.json")
    else:
        for src in manifest.get("sources", []):
            if src.get("source_type") not in SOURCE_TYPES:
                errors.append(f"{pid}: bad source_type {src.get('source_type')}")
            if not (bdir / src.get("path", "")).exists():
                errors.append(f"{pid}: manifest path missing {src.get('path')}")

    bundle_text = ""
    sources = {}
    for f in sorted(bdir.rglob("*")):
        if f.is_dir():
            continue
        text = f.read_text(errors="replace")
        bundle_text += "\n" + text
        if f.suffix == ".json":
            obj = load_json(f, errors)
            if isinstance(obj, dict):
                sources[f.stem] = obj
        elif f.suffix == ".md":
            sources[str(f.relative_to(bdir))] = text
        for pat in LEAK_PATTERNS:
            if re.search(pat, text):
                errors.append(f"{pid}: leak pattern '{pat}' in {f.name}")
        for y, m, d in DATE_RE.findall(text):
            stamp = f"{y}-{m}-{d or '01'}"
            if stamp > AS_OF and f.name not in ("certs.json",):
                warns.append(f"{pid}: future date {stamp} in {f.name}")
        if f.name.startswith("cv"):
            hits = [w for w in SLOP_WORDS if w in text.lower()]
            if len(hits) >= 2:
                warns.append(f"{pid}: slop words in {f.name}: {hits}")

    certs_path = bdir / "certs.json"
    if certs_path.exists() and cert_names is not None:
        certs = load_json(certs_path, errors) or {}
        for c in certs.get("certificates", []):
            if c.get("name", "").strip().lower() not in cert_names:
                warns.append(f"{pid}: cert not in grounding: {c.get('name')}")
    lms_path = bdir / "lms.json"
    if lms_path.exists() and course_names is not None:
        lms = load_json(lms_path, errors) or {}
        rows = lms if isinstance(lms, list) else next((v for v in lms.values() if isinstance(v, list)), [])
        for c in rows:
            title = c.get("course_title", "")
            if not title.lower().startswith("internal:") and title.strip().lower() not in course_names:
                warns.append(f"{pid}: course not in grounding: {title}")

    if tpath.exists():
        truth = load_json(tpath, errors) or {}
        for s in truth.get("skills", []):
            sid = s.get("skill_id")
            if skills is not None and sid not in skills:
                errors.append(f"{pid}: truth skill_id not in taxonomy: {sid}")
                continue
            top = skills.get(sid, 4) if skills else 4
            for k in ("true_level", "self_perceived_level", "assessed_level"):
                v = s.get(k)
                if v is not None and not (0 <= v <= top):
                    errors.append(f"{pid}: {sid}.{k}={v} outside scale 0..{top}")
        if not truth.get("traps"):
            warns.append(f"{pid}: no traps listed")
        truth_text = " ".join([truth.get("summary", "")] + [s.get("why", "") for s in truth.get("skills", [])]
                              + [t.get("plant", "") for t in truth.get("traps", [])])
        overlap = ngrams(truth_text) & ngrams(bundle_text)
        if overlap:
            errors.append(f"{pid}: truth text leaks into bundle (8-gram): {sorted(overlap)[:2]}")
    errors.extend(coherence_checks(pid, sources, world or {pid: sources}))
    return errors, warns


def main():
    skills, _ = taxonomy_index()
    cert_names = grounding_names("certifications.json", ["name", "official_name"])
    course_names = grounding_names("courses.json", ["title", "course_title"])
    pids = sys.argv[1:] or sorted(p.name for p in (DATA / "bundles").glob("P*"))
    world = {}
    for pid in pids:
        world[pid] = {}
        for name in ("github", "jira", "servicenow", "salesforce", "hcm"):
            path = DATA / "bundles" / pid / (name + ".json")
            if path.exists():
                try:
                    obj = json.loads(path.read_text())
                    if isinstance(obj, dict):
                        world[pid][name] = obj
                except (ValueError, OSError):
                    pass  # validate() reports the original load error.
    cross_errors = cross_persona_checks(world)
    total_err = 0
    for pid in pids:
        errors, warns = validate(pid, skills, cert_names, course_names, world)
        errors.extend(cross_errors[pid])
        total_err += len(errors)
        status = "OK " if not errors else "ERR"
        print(f"[{status}] {pid}  errors={len(errors)} warns={len(warns)}")
        for e in errors:
            print(f"   ERROR {e}")
        for w in warns:
            print(f"   WARN  {w}")
    sys.exit(1 if total_err else 0)


if __name__ == "__main__":
    main()
