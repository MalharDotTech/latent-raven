"""Feedback loop guardrails: min labels, step limits, misses-only shift, human-only params untouched."""

from imocha_raven import feedback
from imocha_raven.feedback import Item, propose_shift, propose_tau, run


def item(p, level=3, implied=3, has=True, top=4, lev=True):
    return Item(skill_id="python", scale_max=top, p_yes=p, level=level, level_evidence=lev, has_skill=has,
                implied_level=implied, source="test")


def test_too_few_labels_never_moves():
    assert propose_tau([item(0.9)] * 5, 0.5) == (0.5, "hold: 5 labelled Raven 3 candidates < 30 needed")
    assert propose_shift([item(0.9)] * 5, 1)[0] == 1


def test_tau_moves_at_most_one_step():
    good = [item(0.2 + i / 100) for i in range(60)]  # all correct: lowest qualifying tau is low
    new, _ = propose_tau(good, 0.8)
    assert new == 0.75


def test_tau_tightens_when_precision_is_bad():
    bad = [item(0.5 + i / 200, has=i % 2 == 0) for i in range(60)]  # half wrong at every tau
    new, why = propose_tau(bad, 0.5)
    assert new == 0.55 and "tighten" in why


def test_shift_ignores_in_band_offsets_and_reacts_to_misses():
    in_band = [item(0.9, level=3, implied=2)] * 30  # off-centre but accepted under +-1
    assert propose_shift(in_band, 1)[0] == 1
    misses = [item(0.9, level=4, implied=2)] * 10 + [item(0.9)] * 20  # engine too high, outside the band
    assert propose_shift(misses, 1)[0] == 0


def test_dry_run_writes_nothing_and_lists_human_only(tmp_path, monkeypatch=None):
    before = feedback.FEEDBACK_FILE.exists()
    r = run([item(0.9)] * 3, apply=False, start={"tau": 0.4, "shift": 1, "history": []})
    assert feedback.FEEDBACK_FILE.exists() == before
    assert set(r["human_only_untouched"]) == set(feedback.HUMAN_ONLY)


if __name__ == "__main__":
    import tempfile
    from pathlib import Path
    for name, f in list(globals().items()):
        if name.startswith("test_"):
            f(Path(tempfile.mkdtemp())) if "tmp_path" in f.__code__.co_varnames else f()
            print("ok", name)
