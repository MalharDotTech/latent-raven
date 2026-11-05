"""Renumber PRs/Jira across P001--P042 and substitute their IDs in truth.

Run: python3 -I scripts/fix_structure.py

This follow-up to the original structure repair changes only IDs/references.
The original id_remap.json and structure_fix_state.json remain historical audit
artifacts. This run maps the CURRENT input IDs to new IDs in id_remap_run2.json
and checkpoints bundle/truth hashes in structure_fix_state_run2.json. Repeating
it verifies the checkpoint and changes no bytes; changed inputs fail closed.
Twins are never loaded or modified. Allocation uses SHA-256-derived seeds.
"""

import hashlib
import json
import random
import re
import sys
from collections import Counter, defaultdict
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from persona_structure import (JIRA_PROJECTS, PR_REF_RE, STRAY_PROJECTS, TICKET_RE,
                               iso_day, records)

PIDS = tuple(f"P{i:03}" for i in range(1, 43))
NOTES = ROOT / "data/notes"
STATE = NOTES / "structure_fix_state_run2.json"
REMAP = NOTES / "id_remap_run2.json"
SEED = "kestrel-structure-v2-2026-11-05"


def rng(*parts):
    return random.Random(int(hashlib.sha256((SEED + "|" + "|".join(map(str, parts))).encode()).hexdigest(), 16))


def digest(raw):
    return hashlib.sha256(raw.encode()).hexdigest()


def dumped(value):
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def replace_literals(text, mapping):
    """One simultaneous, bounded substitution; replacement IDs never cascade."""
    if not mapping:
        return text
    pattern = r"(?<![A-Za-z0-9-])(?:" + "|".join(re.escape(k) for k in sorted(mapping, key=len, reverse=True)) + r")(?![A-Za-z0-9-])"
    return re.sub(pattern, lambda m: mapping[m[0]], text)


def map_strings(value, transform):
    if isinstance(value, dict):
        return {k: map_strings(v, transform) for k, v in value.items()}
    if isinstance(value, list):
        return [map_strings(v, transform) for v in value]
    return transform(value) if isinstance(value, str) else value


def main():
    # Explicit numeric whitelist: never include a twin or a later batch.
    raw = {}
    bundles = {}
    for pid in PIDS:
        bdir = ROOT / "data/bundles" / pid
        if not bdir.is_dir():
            raise SystemExit(f"Missing {bdir}; refusing a partial global renumber")
        bundles[pid] = {}
        for path in sorted(bdir.rglob("*")):
            if path.suffix not in (".json", ".md") or not path.is_file():
                continue
            rel = str(path.relative_to(ROOT))
            raw[rel] = path.read_text()
            bundles[pid][str(path.relative_to(bdir))] = json.loads(raw[rel]) if path.suffix == ".json" else raw[rel]
    # Truth is staged as raw text: only simultaneous ID substitutions are allowed.
    for pid in PIDS:
        rel = f"data/truth/{pid}.json"
        raw[rel] = (ROOT / rel).read_text()
        json.loads(raw[rel])
    if STATE.exists():
        state = json.loads(STATE.read_text())
        actual = {path: digest(text) for path, text in raw.items()}
        if (state.get("version") != 3 or state.get("scope") != list(PIDS)
                or state.get("seed") != SEED or actual != state["output_sha256"]):
            raise SystemExit("Bundle/truth inputs or repair scope changed since the checkpoint; refusing to cascade IDs. Restore the checkpointed outputs before rerunning.")
        if not REMAP.exists() or digest(REMAP.read_text()) != state["remap_sha256"]:
            raise SystemExit("The ID remap is missing or changed; restore it before rerunning.")
        print("Already repaired; all output hashes match. No files changed.")
        print(json.dumps(state["counts"], sort_keys=True))
        return

    counts = Counter()
    remaps = {pid: {} for pid in PIDS}
    sources = {pid: {name: files.get(name + ".json", {}) for name in ("github", "jira", "servicenow", "salesforce", "hcm")}
               for pid, files in bundles.items()}

    # Jira registry includes reference-only tickets. Explicit linked_prs and
    # copied summary keys are aliases of an existing Jira object where possible.
    jira_entries = []
    aliases = {pid: {} for pid in PIDS}
    for pid, data in sources.items():
        for issue in data["jira"].get("issues", []):
            jira_entries.append({"pid": pid, "old": issue["key"], "date": issue["created"], "row": issue})
            for key in TICKET_RE.findall(issue.get("summary", "")):
                if key != issue["key"] and key not in {i["key"] for i in data["jira"].get("issues", [])}:
                    aliases[pid][key] = issue["key"]
    for pid, files in bundles.items():
        known = {entry["old"] for entry in jira_entries if entry["pid"] == pid}
        for path, content in files.items():
            text = json.dumps(content) if isinstance(content, dict) else content
            for key in sorted(set(TICKET_RE.findall(text)) - known - aliases[pid].keys()):
                # Find the containing dated record; a plain-text backlog
                # reference uses page creation, not the current export date.
                stamps = []
                source = path.removesuffix(".json")
                if source in ("github", "jira", "servicenow", "salesforce"):
                    for item in records(sources[pid][source], source):
                        if key in json.dumps(item):
                            stamp = next((item.get(k) for k in ("created", "opened", "date", "close_date", "merged") if iso_day(item.get(k))), None)
                            if stamp:
                                stamps.append(stamp)
                elif isinstance(content, str):
                    stamps += re.findall(r"^created:\s*(\d{4}-\d{2}-\d{2})", content, re.M)
                if not stamps:
                    stamps = ["2024-09-01"] if key.startswith("HR-MIG-") else ["2026-10-31"]
                existing = next((e for e in jira_entries if e["pid"] == pid and e["old"] == key), None)
                if existing:
                    existing["date"] = min(existing["date"], *stamps)
                else:
                    jira_entries.append({"pid": pid, "old": key, "date": min(stamps), "row": None})

    def project(key):
        prefix = key.rsplit("-", 1)[0]
        return STRAY_PROJECTS.get(prefix, prefix)

    for prefix in sorted(JIRA_PROJECTS):
        entries = sorted((e for e in jira_entries if project(e["old"]) == prefix), key=lambda e: (e["date"], e["old"], e["pid"]))
        number = rng("jira", prefix, "base").randint(700, 3500)
        previous_date = None
        for entry in entries:
            gap_days = (iso_day(entry["date"]) - iso_day(previous_date)).days if previous_date else 0
            number += rng("jira", prefix, entry["date"], entry["old"]).randint(2, 13) + min(gap_days, 90)
            remaps[entry["pid"]][entry["old"]] = f"{prefix}-{number}"
            previous_date = entry["date"]
            counts["jira_records_renumbered" if entry["row"] is not None else "jira_reference_only_ids_renumbered"] += 1
    for pid, values in aliases.items():
        for old, canonical in values.items():
            remaps[pid][old] = remaps[pid][canonical]
            counts["jira_aliases_remapped"] += 1

    # Registry includes unseen PRs mentioned in review/merge samples. Known PRs
    # always take their actual creation date, including reviews by other people.
    registry = {}
    authored_index = defaultdict(list)
    for pid, data in sources.items():
        for pr in data["github"].get("pull_requests", []):
            key = (pid, pr["repo"], pr["number"])
            if key in registry:
                raise ValueError(f"Duplicate PR inside one bundle: {key}")
            registry[key] = {"created": pr["created"], "title": pr["title"], "listed": True}
            authored_index[(pr["repo"], pr["number"])].append(key)

    def resolve_pr(pid, repo, old, stamp=None):
        local = (pid, repo, old)
        if local in registry:
            return local
        matches = authored_index.get((repo, old), [])
        if len(matches) == 1:
            return matches[0]
        if matches:
            # An originally colliding number is disambiguated by the nearest
            # preceding creation, only for a review without a local author row.
            eligible = [k for k in matches if not stamp or registry[k]["created"] <= stamp]
            return max(eligible or matches, key=lambda k: registry[k]["created"])
        return ("unseen", repo, old)

    counts["original_pr_collisions_resolved"] = sum(len(v) - 1 for v in authored_index.values())
    for pid, data in sources.items():
        for item in data["github"].get("reviews_given", []) + data["github"].get("merge_events", []):
            stamp = item.get("date", item.get("merged"))
            key = resolve_pr(pid, item["repo"], item["pr_number"], stamp)
            if key not in registry:
                registry[key] = {"created": (iso_day(stamp) - timedelta(days=rng(*key).randint(1, 6))).isoformat(), "title": str(item.get("sample_comment", item.get("title", ""))), "listed": False}
            elif not registry[key]["listed"]:
                registry[key]["created"] = min(registry[key]["created"], (iso_day(stamp) - timedelta(days=1)).isoformat())
    # A squash-merge title can mention an unseen original PR from the same repo.
    for pid, data in sources.items():
        for pr in data["github"].get("pull_requests", []):
            for number in re.findall(r"#(\d+)\b", pr["title"]):
                key = resolve_pr(pid, pr["repo"], int(number), pr["created"])
                registry.setdefault(key, {"created": pr["created"], "title": "squashed original", "listed": False})
    allocated = {}
    for repo in sorted({repo for owner, repo, number in registry}):
        # Repo base uses no persona input. Gaps represent other unseen authors.
        number = rng("github", repo, "base").randint(2000, 9000)
        previous_date = None
        for key, entry in sorted(((key, entry) for key, entry in registry.items() if key[1] == repo), key=lambda pair: (pair[1]["created"], pair[1]["title"], pair[0][2], pair[0][0])):
            gap = (iso_day(entry["created"]) - iso_day(previous_date)).days if previous_date else 0
            number += rng("github", repo, entry["created"], entry["title"]).randint(2, 17) + min(gap, 120) * rng("rate", repo).randint(1, 3)
            allocated[key] = number
            previous_date = entry["created"]
            counts["prs_renumbered" if entry["listed"] else "review_or_reference_only_prs_renumbered"] += 1
    for pid, data in sources.items():
        references = set()
        for item in records(data["github"], "github"):
            old = item.get("number", item.get("pr_number"))
            if old is not None:
                references.add(resolve_pr(pid, item["repo"], old, item.get("date", item.get("created", item.get("merged")))))
        for content in bundles[pid].values():
            for repo, number in PR_REF_RE.findall(json.dumps(content) if isinstance(content, dict) else content):
                key = resolve_pr(pid, "kestrel-cloud/" + repo, int(number))
                if key in allocated:
                    references.add(key)
        for pr in data["github"].get("pull_requests", []):
            references.update(resolve_pr(pid, pr["repo"], int(n), pr["created"]) for n in re.findall(r"#(\d+)\b", pr["title"]))
        by_number = defaultdict(set)
        for key in sorted(references):
            owner, repo, old = key
            new = allocated[key]
            remaps[pid][f"{repo}#{old}"] = f"{repo}#{new}"
            short = repo.removeprefix("kestrel-cloud/")
            remaps[pid][f"{short}#{old}"] = f"{short}#{new}"
            remaps[pid][f"https://github.com/{repo}/pull/{old}"] = f"https://github.com/{repo}/pull/{new}"
            by_number[old].add(new)
        for old, values in by_number.items():
            if len(values) == 1:
                remaps[pid][f"#{old}"] = f"#{next(iter(values))}"
            else:
                counts["ambiguous_bare_pr_ids_repo_qualified"] += 1
        for item in records(data["github"], "github"):
            field = "number" if "number" in item else "pr_number"
            if field in item:
                old = item[field]
                key = resolve_pr(pid, item["repo"], old, item.get("date", item.get("created", item.get("merged"))))
                item[field] = allocated[key]
                counts["pr_numeric_fields_changed"] += old != item[field]

    # Rewrite *all* JSON string values and Markdown references simultaneously.
    # Numeric PR fields were handled with repo context; no arbitrary number
    # replacement may corrupt dates, diff sizes, employee IDs or quantities.
    for pid, files in bundles.items():
        transform = lambda text, pid=pid: replace_literals(text, remaps[pid])
        for path, content in files.items():
            files[path] = map_strings(content, transform)
        for name in sources[pid]:
            sources[pid][name] = files.get(name + ".json", {})

    output = {}
    renamed = {}
    for pid, files in bundles.items():
        for path, content in files.items():
            rel = f"data/bundles/{pid}/{path}"
            new_path = replace_literals(path, remaps[pid])
            new_rel = f"data/bundles/{pid}/{new_path}"
            if new_rel in output:
                raise ValueError(f"Remap would collide at {new_rel}")
            if new_rel != rel:
                renamed[rel] = new_rel
            text = dumped(content) if path.endswith(".json") else content
            # Keep unrelated JSON files byte-for-byte, including their original
            # indentation/newline style when no semantic field changed.
            if path.endswith(".json") and json.loads(raw[rel]) == content:
                text = raw[rel]
            output[new_rel] = text
    for pid in PIDS:
        rel = f"data/truth/{pid}.json"
        old = raw[rel]
        new = replace_literals(old, remaps[pid])
        json.loads(new)
        output[rel] = new
        counts["truth_files_changed"] += old != new
    counts["bundle_files_renamed"] = len(renamed)
    counts["bundle_files_changed"] = sum(output.get(p) != raw[p] for p in raw if p.startswith("data/bundles/"))
    counts["personas_changed"] = sum(any(output.get(p) != raw[p] for p in raw if p.startswith(f"data/bundles/{pid}/")) for pid in PIDS)
    remaps = {pid: {old: new for old, new in mapping.items() if old != new}
              for pid, mapping in remaps.items()}
    counts["id_mapping_entries"] = sum(map(len, remaps.values()))
    # Stage the complete result before writing. This also catches invalid JSON
    # and local/global coherence errors without leaving a partial repair.
    import validate_personas as validator
    validation_errors = []
    for pid, files in bundles.items():
        check_sources = {path.removesuffix(".json") if path.endswith(".json") else path: obj for path, obj in files.items()}
        validation_errors.extend(validator.coherence_checks(pid, check_sources, sources))
    validation_errors.extend(e for errors in validator.cross_persona_checks(sources).values() for e in errors)
    if validation_errors:
        print("Repair plan failed coherence checks; no files written:", file=sys.stderr)
        print("\n".join(validation_errors), file=sys.stderr)
        raise SystemExit(1)
    for pid, files in bundles.items():
        for entry in files["manifest.json"]["sources"]:
            if f"data/bundles/{pid}/{entry['path']}" not in output:
                raise ValueError(f"Manifest remap would leave a missing path: {pid}/{entry['path']}")
    remap_text = dumped(remaps)
    state = {"version": 3, "seed": SEED, "scope": list(PIDS), "counts": dict(sorted(counts.items())),
             "input_sha256": {p: digest(t) for p, t in raw.items()},
             "output_sha256": {p: digest(t) for p, t in output.items()},
             "remap_sha256": digest(remap_text), "renamed_files": renamed}
    for path, text in output.items():
        if raw.get(path) != text:
            (ROOT / path).write_text(text)
    for path in renamed:
        (ROOT / path).unlink()
    NOTES.mkdir(exist_ok=True)
    REMAP.write_text(remap_text)
    STATE.write_text(dumped(state))
    print(json.dumps(dict(sorted(counts.items())), indent=2))


if __name__ == "__main__":
    main()
