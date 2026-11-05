"""Stage 3: no quote, no record. Normalised substring match against the source text."""

import re

from .types import Bundle, Claim

_QUOTES = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"', "–": "-", "—": "-",
                         " ": " ", "•": "-", "*": "", "`": "", "\\": ""})


def norm(s: str) -> str:
    s = s.translate(_QUOTES).lower()
    return re.sub(r"\s+", " ", s).strip()


def repair(quote: str, text: str) -> str:
    """The reader sometimes copies our compact view (`[ref] k=v | k=v`) instead of the source span: keep the span that exists."""
    if norm(quote) in text:
        return quote
    q = re.sub(r"^\w+: ", "", quote.strip())
    q = re.sub(r"^\[[^\]]*\]\s*", "", q)
    best = ""
    for part in q.split(" | "):
        part = re.sub(r"^\w+=", "", part.strip())
        if len(part) > len(best) and norm(part) in text:
            best = part
    return best or quote


def verify_claims(bundle: Bundle, claims: list[Claim]) -> tuple[list[Claim], int]:
    """Set quote_verified. Returns (verified claims, dropped count)."""
    texts = {s.source_id: norm(s.text) for s in bundle.sources}
    kept, dropped = [], 0
    for c in claims:
        c.quote = repair(c.quote, texts.get(c.source_id, ""))
        q = norm(c.quote)
        c.quote_verified = len(q) >= 2 and q in texts.get(c.source_id, "")
        if c.quote_verified:
            kept.append(c)
        else:
            dropped += 1
    return kept, dropped
