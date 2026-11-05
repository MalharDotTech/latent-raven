"""Regression checks: python3 -I scripts/test_persona_structure.py"""

import contextlib
import hashlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fix_structure as repair
import validate_personas as validator
from persona_structure import ledgerly_violations, monthly_floors


def pr(number=101, created="2025-01-12", merged="2025-01-16", title="QA-1 fix parser"):
    return {"repo": "kestrel-cloud/billing-core", "number": number, "title": title,
            "created": created, "merged": merged, "state": "merged", "files_ext": {".py": 2}}


def issue(key="QA-1", created="2025-01-20"):
    return {"key": key, "created": created, "resolved": "2025-01-24",
            "resolved_by_self": True, "reporter_is_self": True,
            "assignee_history": [{"assignee": "self", "from": "2025-01-01"}]}


class ValidatorTests(unittest.TestCase):
    def errors(self, github=None, jira=None, **extra):
        sources = {"github": github or {}, "jira": jira or {}, **extra}
        return validator.coherence_checks("P001", sources, {"P001": sources})

    def test_ticket_links_in_both_directions_and_merge_order(self):
        errors = self.errors({"pull_requests": [pr(merged="2025-01-01")]}, {"issues": [issue()]})
        self.assertTrue(any("before referenced ticket" in e for e in errors))
        self.assertTrue(any("merged" in e and "before created" in e for e in errors))
        i = issue()
        i["linked_prs"] = ["billing-core#101"]
        errors = self.errors({"pull_requests": [pr(title="fix parser")]}, {"issues": [i]})
        self.assertTrue(any("before referenced ticket" in e for e in errors))

    def test_day_concentration_and_disallowed_projects(self):
        errors = self.errors({"pull_requests": [pr(title="FOO-42 fix parser")]}, {"issues": [issue("LEDGER-9")]})
        self.assertTrue(any("day-of-month" in e for e in errors))
        self.assertEqual(sum("disallowed project" in e for e in errors), 2)

    def test_cross_persona_errors_and_twin_exemption(self):
        world = {"P001": {"github": {"pull_requests": [pr(number=900, created="2025-01-01")]}, "jira": {"issues": [issue()]}},
                 "P002": {"github": {"pull_requests": [pr(number=100, created="2025-02-01"), pr(number=900, created="2025-03-01")]},
                          "jira": {"issues": [issue()]}},
                 "P001-T1": {"github": {"pull_requests": [pr(number=900)]}, "jira": {"issues": [issue()]}}}
        errors = validator.cross_persona_checks(world)
        self.assertTrue(any("duplicate PR" in e for e in errors["P001"]))
        self.assertTrue(any("duplicate jira key" in e for e in errors["P001"]))
        self.assertTrue(any("not monotonic" in e for e in errors["P002"]))
        self.assertNotIn("P001-T1", errors)

    def test_monthly_counts_use_event_dates_and_attribution(self):
        gh = {"pull_requests": [pr(created="2025-01-31", merged="2025-02-03")],
              "reviews_given": [{"date": "2025-03-01"}]}
        floors = monthly_floors("github", gh)
        self.assertEqual(floors["2025-02"]["merged_prs"], 1)
        self.assertEqual(floors["2025-02"]["by_ext:.py"], 2)
        self.assertEqual(floors["2025-03"]["reviews"], 1)
        self.assertNotIn("2025-01", floors)
        errors = self.errors(gh)
        self.assertTrue(any("below listed items" in e for e in errors))
        sf = {"opportunities": [{"created": "2025-01-01", "close_date": "2025-02-02", "stage": "Closed Won"}],
              "activities": [{"date": "2025-03-01", "created_by": "Assistant"}]}
        floors = monthly_floors("salesforce", sf, {"Owner"})
        self.assertEqual(floors["2025-01"]["opps_created"], 1)
        self.assertEqual(floors["2025-02"]["opps_closed"], 1)
        self.assertEqual(floors["2025-03"]["activities_total"], 1)
        self.assertEqual(floors["2025-03"]["activities_created_by_user"], 0)

    def test_ledgerly_date_belongs_to_record_or_revision(self):
        self.assertTrue(ledgerly_violations({"issues": [{"summary": "Ledgerly import", "created": "2023-10-01"}]}))
        self.assertFalse(ledgerly_violations({"original_hire_date": "2021-09-06", "job_history": [{"grade": "Ledgerly-TL", "from": "2024-03"}]}))
        self.assertTrue(ledgerly_violations("---\ncreated: 2023-05-22\nlast_edited: 2024-02-26\n---\nLedgerly hypercare"))
        self.assertFalse(ledgerly_violations("---\ncreated: 2023-05-22\nlast_edited: 2024-04-01\n---\nLedgerly import update"))


class RepairTests(unittest.TestCase):
    def fixture(self, root):
        def write(pid, path, obj):
            target = root / "data/bundles" / pid / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(obj) if path.endswith(".json") else obj)

        for pid in repair.PIDS:
            write(pid, "manifest.json", {"sources": [{"source_type": "hcm", "path": "hcm.json"}]})
            write(pid, "hcm.json", {"legal_name": pid})
        for pid in ("P001", "P002"):
            prs = [pr(101 + m, f"2025-{m:02}-12", f"2025-{m:02}-16", "fix parser") for m in range(1, 11)]
            prs[0]["title"] = "QA-1 fix parser"
            write(pid, "github.json", {"pull_requests": prs, "monthly_activity": []})
            write(pid, "jira.json", {"issues": [issue()], "monthly_activity": []})
        write("P004", "docs/ARCH-adr-014-invoice-numbering.md", "The Ledgerly acquisition adds another numbering scheme.\nLedgerly numbering migrated later, not part of this ADR")
        write("P026", "docs/DOC-PEOPLE-0733.md", "manager hierarchy for Ledgerly staff")
        write("P009", "docs/DATA-0912.md", "---\ndoc_id: DATA-0912\ncreated: 2025-01-01\n---\nSQL style")
        write("P009", "manifest.json", {"sources": [{"source_type": "authored_doc", "path": "docs/DATA-0912.md", "source_id": "P009_DATA-0912"}]})
        for pid in ("P022", "P027"):
            write(pid, "salesforce.json", {"opportunities": [{"opp_id": "006brokenIAU", "created": "2025-01-01", "close_date": "2025-03-01", "stage": "Closed Won"}], "monthly_activity": []})
        write("P033", "sentinel.md", "new batch must remain untouched")
        write("P001-T1", "sentinel.md", "twin must remain untouched")
        truth = root / "data/truth/P001.json"
        truth.parent.mkdir(parents=True)
        truth.write_text('{"keep": true}')

    def run_repair(self, root):
        notes = root / "data/notes"
        with patch.multiple(repair, ROOT=root, NOTES=notes, STATE=notes / "structure_fix_state.json", REMAP=notes / "id_remap.json"):
            with contextlib.redirect_stdout(io.StringIO()):
                repair.main()

    def snapshot(self, root):
        return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob("*") if p.is_file()}

    def test_seeded_deterministic_idempotent_and_scoped(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            roots = [Path(a), Path(b)]
            for root in roots:
                self.fixture(root)
                protected = {p: (root / p).read_bytes() for p in ("data/bundles/P033/sentinel.md", "data/bundles/P001-T1/sentinel.md", "data/truth/P001.json")}
                self.run_repair(root)
                before = self.snapshot(root)
                self.run_repair(root)
                self.assertEqual(before, self.snapshot(root))
                for p, raw in protected.items():
                    self.assertEqual((root / p).read_bytes(), raw)
                manifest = json.loads((root / "data/bundles/P009/manifest.json").read_text())
                source = manifest["sources"][0]
                self.assertTrue((root / "data/bundles/P009" / source["path"]).exists())
                self.assertNotEqual(source["source_id"], "P009_DATA-0912")
                for pid in ("P022", "P027"):
                    sf = json.loads((root / "data/bundles" / pid / "salesforce.json").read_text())
                    identifier = sf["opportunities"][0]["opp_id"]
                    self.assertRegex(identifier, r"^006\d{12}[A-Z0-5]{3}$")
            self.assertEqual(self.snapshot(roots[0]), self.snapshot(roots[1]))

    def test_checkpoint_refuses_to_cascade_after_later_edits(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.fixture(root)
            self.run_repair(root)
            (root / "data/bundles/P001/hcm.json").write_text('{"legal_name": "Changed"}')
            with self.assertRaisesRegex(SystemExit, "refusing to cascade"):
                self.run_repair(root)


if __name__ == "__main__":
    unittest.main()
