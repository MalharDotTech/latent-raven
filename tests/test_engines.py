import json

from imocha_raven import load
from imocha_raven.engines.raven2 import Raven2
from imocha_raven.engines.raven3 import Raven3, accepted
from imocha_raven.eval.score import expected_catch, wilson

from tests.fixtures.claims import bundle, claims

TAX = load.load_taxonomy()


def acts(res):
    return {d.skill_id: (d.action, d.level) for d in res.decisions}


def test_raven2_rules():
    a = acts(Raven2().infer(bundle(), TAX, claims()))
    assert a["python"] == ("send", 3)  # work in 3 months, floor 3
    assert a["kafka"][0] == "hold"  # listed only
    assert a["java"][0] == "hold"  # stale beyond 2y window


def test_raven3_threshold_and_determinism():
    lo, hi = Raven3(0.0), Raven3(0.99)
    a = acts(lo.infer(bundle(), TAX, claims()))
    assert a["python"][0] == "send" and a["kafka"][0] == "send"  # tau 0 sends everything
    assert all(v[0] == "hold" for v in acts(hi.infer(bundle(), TAX, claims())).values())
    r1, r2 = Raven3(0.5).infer(bundle(), TAX, claims()), Raven3(0.5).infer(bundle(), TAX, claims())
    assert r1.model_dump_json() == r2.model_dump_json()
    p = {d.skill_id: d.p_yes for d in lo.infer(bundle(), TAX, claims()).decisions}
    assert p["python"] > p["kafka"] > p["java"] - 1e-9 or p["python"] > p["java"]


def test_duplicate_cv_versions_add_nothing():
    cl = claims()
    dup = cl[3].model_copy(update={"source_id": "cv_1"})
    base = {d.skill_id: d.p_yes for d in Raven3(0).infer(bundle(), TAX, cl).decisions}
    more = {d.skill_id: d.p_yes for d in Raven3(0).infer(bundle(), TAX, cl + [dup]).decisions}
    assert base["python"] == more["python"]


def test_consent_blocks_messages():
    eu = json.dumps({"country": "DE", "messaging_consent": {"notice_given": True, "opted_out": False, "eu_opt_in": False}})
    r = Raven2().infer(bundle(eu), TAX, claims())
    assert {d.action for d in r.decisions} == {"do_not_message"}


def test_helpers():
    assert accepted(3, 4) == [2, 3, 4] and accepted(2, 3) == [2]
    lo, hi = wilson(19, 20)
    assert 0.7 < lo < 0.95 < hi <= 1
    assert expected_catch("send_at_level_3", "send", 4, TAX, "python")
    assert not expected_catch("hold", "send", 3, TAX, "python")


if __name__ == "__main__":  # no pytest dependency: uv run python -m tests.test_engines
    for n, f in sorted(globals().items()):
        if n.startswith("test_"):
            f()
            print("ok", n)
