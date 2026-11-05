"""Shared, read-only structure rules for persona repair and validation."""

import calendar
import re
from collections import Counter, defaultdict
from datetime import date

JIRA_PROJECTS = frozenset({"BILL", "RECON", "DATA", "WEB", "MOB", "PLAT", "QA", "SEC", "PM"})
# These are ticket namespaces mistakenly introduced by the original generators.
# Do not interpret employee IDs, ADRs, certifications or Oracle error codes as Jira.
STRAY_PROJECTS = {"LEDGER": "RECON", "SE": "PM", "HR-MIG": "PM"}
TICKET_RE = re.compile(r"(?<![\w-])(?:" + "|".join(sorted(JIRA_PROJECTS | STRAY_PROJECTS.keys(), key=len, reverse=True)) + r")-\d+\b")
PR_REF_RE = re.compile(r"(?:(?:kestrel-cloud)/)?([a-z][a-z0-9-]+)#(\d+)\b")
ACQUISITION = "2024-03-01"


def iso_day(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}(?:-\d{2})?", value):
        return None
    try:
        return date.fromisoformat(value if len(value) == 10 else value + "-01")
    except ValueError:
        return None


def month_end(value):
    d = iso_day(value)
    return d.replace(day=calendar.monthrange(d.year, d.month)[1])


def records(data, source):
    names = {"github": ("pull_requests", "reviews_given", "merge_events"),
             "jira": ("issues",), "servicenow": ("records", "incidents", "items", "requests"),
             "salesforce": ("opportunities", "activities")}
    return [row for key in names[source] for row in data.get(key, [])]


def linked_tickets(pr, issues):
    """Recognize both PR -> ticket text/fields and Jira -> PR links."""
    import json
    keys = set(TICKET_RE.findall(json.dumps(pr)))
    identity = (pr.get("repo", "").removeprefix("kestrel-cloud/"), str(pr.get("number")))
    for issue in issues:
        if any(tuple(m) == identity for ref in issue.get("linked_prs", []) for m in PR_REF_RE.findall(ref)):
            keys.add(issue["key"])
    return keys


def monthly_floors(source, data, own_names=()):
    """Count samples by event month and metric semantics, including sparse history."""
    floors = defaultdict(Counter)

    def add(stamp, metric, amount=1):
        if iso_day(stamp):
            floors[stamp[:7]][metric] += amount

    if source == "github":
        for pr in data.get("pull_requests", []):
            if pr.get("state") == "merged":
                stamp = pr.get("merged")
                add(stamp, "merged_prs")
                for ext, count in pr.get("files_ext", {}).items():
                    add(stamp, "by_ext:" + ext, count)
                if pr.get("author_type", "human") == "human":
                    add(stamp, "authored_merged_prs")
                elif pr.get("merged_by") == "self":
                    add(stamp, "bot_prs_merged_by_self")
        for review in data.get("reviews_given", []):
            add(review.get("date"), "reviews")
    elif source == "jira":
        for issue in data.get("issues", []):
            if issue.get("resolved_by_self"):
                add(issue.get("resolved"), "resolved_as_assignee")
            if issue.get("reporter_is_self"):
                add(issue.get("created"), "reported")
    elif source == "servicenow":
        assigned_key = "incidents_resolved_by_self" if "records" in data else "tickets_resolved_as_assignee"
        for item in records(data, source):
            if item.get("number", "").startswith("INC"):
                if "records" in data:
                    add(item.get("opened"), "incidents_assigned")
                if item.get("resolved_by_self"):
                    add(item.get("resolved"), assigned_key)
            elif item.get("requested_by_self", True):
                add(item.get("opened"), "ritm_raised")
    elif source == "salesforce":
        for opp in data.get("opportunities", []):
            add(opp.get("created"), "opps_created")
            if opp.get("stage", "").lower().startswith("closed"):
                add(opp.get("close_date"), "opps_closed")
            if "opps_touched" in next(iter(data.get("monthly_activity", [])), {}):
                for month in {s[:7] for s in (opp.get("created"), opp.get("close_date")) if iso_day(s)}:
                    add(month, "opps_touched")
        for activity in data.get("activities", []):
            add(activity.get("date"), "activities_total")
            if activity.get("created_by") in own_names:
                add(activity.get("date"), "activities_created_by_user")
    return floors


def ledgerly_violations(value, context=""):
    """Check the date of the containing evidence record, never unrelated ancestors.

    A historical original_hire_date does not date a 2026 CV or HCM export.
    Likewise a page can acquire a new paragraph in a later revision.
    """
    import json
    found = []
    if isinstance(value, dict):
        direct = " ".join(str(v) for v in value.values() if isinstance(v, str))
        if "ledgerly" in direct.lower():
            stamps = [value.get(k) for k in ("created", "opened", "date", "from", "close_date", "completed", "issued")]
            stamp = next((s for s in stamps if iso_day(s)), None)
            if stamp and stamp < ACQUISITION[:len(stamp)]:
                found.append((context, stamp))
        for key, child in value.items():
            if isinstance(child, (dict, list)):
                found.extend(ledgerly_violations(child, context + "/" + key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(ledgerly_violations(child, context + f"[{index}]"))
    elif isinstance(value, str) and "ledgerly" in value.lower():
        # Front matter is not a general YAML dependency; the schema uses ISO dates.
        front = re.match(r"\A---\n(.*?)\n---", value, re.S)
        if front:
            stamps = dict(re.findall(r"^(created|last_edited):\s*(\d{4}-\d{2}(?:-\d{2})?)\s*$", front[1], re.M))
            stamp = stamps.get("last_edited", stamps.get("created"))
            if stamp and stamp < ACQUISITION[:len(stamp)]:
                found.append((context, stamp))
    return found
