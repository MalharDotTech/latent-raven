"""Hand-made bundle and claims: python (strong), kafka (listed only), java (stale), excel_modeling (generic-like)."""

from imocha_raven.types import Bundle, Claim, Source

HCM = '{"country": "IN", "messaging_consent": {"notice_given": true, "opted_out": false, "eu_opt_in": false}}'


def bundle(hcm: str = HCM) -> Bundle:
    srcs = [Source(source_id="hcm_1", source_type="hcm", path="hcm.json", text=hcm),
            Source(source_id="cv_1", source_type="cv", path="cv.md", text="Built Python ETL. Skills: Kafka. Java 2015.",
                   received="2026-03-01", lineage_key="cv-X"),
            Source(source_id="gh_1", source_type="github", path="gh.json", text="fix python service a; fix python service b; fix python c",
                   received="2026-10-01")]
    return Bundle(person_ref="T001", as_of="2026-10-31", sources=srcs, messaging_allowed=None)


def claim(sid, src, quote, et, lv, date, ref=None, gk=None):
    return Claim(source_id=src, skill_phrase=sid, quote=quote, evidence_type=et, level_seen=lv, date=date,
                 quote_verified=True, skill_id=sid, group_key=gk or f"{src}", ref=ref)


def claims() -> list[Claim]:
    gh = lambda q, d, n: claim("python", "gh_1", q, "applied", 3, d, ref=f"org/repo#{n}", gk="github:gh_1")
    return [gh("fix python service a", "2026-08", 1), gh("fix python service b", "2026-09", 2),
            gh("fix python c", "2026-10", 3),
            claim("python", "cv_1", "Built Python ETL", "applied", 3, "2024-01", gk="self:T001"),
            claim("kafka", "cv_1", "Skills: Kafka", "listed", None, None, gk="self:T001"),
            claim("java", "cv_1", "Java 2015", "applied", 3, "2015-06", gk="self:T001")]
