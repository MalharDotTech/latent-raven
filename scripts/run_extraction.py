"""Run stages 1-5 over bundles. Usage: run_extraction.py [P001 P037 R003 ...] (default: all)."""

import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from imocha_raven.extract import get_extraction
from imocha_raven.load import list_bundles, load_bundle, load_taxonomy


def main(argv: list[str]) -> None:
    tax = load_taxonomy()
    paths = [p for p in list_bundles("all") if not argv or p.name in argv]
    t0 = time.time()

    def one(p: Path):
        try:
            return p.name, get_extraction(load_bundle(p), tax), None
        except Exception as e:
            return p.name, None, str(e)

    results = []
    with ThreadPoolExecutor(6) as ex:
        for name, e, err in ex.map(one, paths):
            if err:
                print(f"{name}: ERROR {err[:150]}", flush=True)
                if "usage limit" in err:
                    sys.exit(1)
                continue
            results.append(e)
            mapped = sum(c.skill_id is not None for c in e.claims)
            print(f"{name}: raw={e.raw_claims} verified={len(e.claims)} dropped={e.dropped_unverified} "
                  f"mapped={mapped} unmatched={len(e.unmatched)} cost=${e.cost_usd:.3f}", flush=True)
    raw = sum(e.raw_claims for e in results)
    ver = sum(len(e.claims) for e in results)
    print(f"\npeople={len(results)} raw_claims={raw} verified={ver} ({100 * ver / max(raw, 1):.1f}%) "
          f"unverified={raw - ver} cost=${sum(e.cost_usd for e in results):.2f} wall={time.time() - t0:.0f}s")


if __name__ == "__main__":
    main(sys.argv[1:])
