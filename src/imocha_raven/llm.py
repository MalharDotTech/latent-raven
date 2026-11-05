"""LLM backend: headless Claude Code CLI. Disk-cached, logged, thread-safe."""

import hashlib
import json
import re
import subprocess
import tempfile
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel

CACHE = Path(__file__).resolve().parents[2] / "data" / "cache"
SCRATCH = tempfile.mkdtemp(prefix="raven-llm-")
_lock = threading.Lock()
SYSTEM = "You are a precise extraction engine. Reply with exactly what is asked, no preamble."


class LLMResponse(BaseModel):
    text: str
    cost_usd: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    latency_s: float = 0.0
    model: str = ""
    cached: bool = False


def _run(prompt: str, model: str, system: str | None) -> LLMResponse:
    cmd = ["claude", "-p", "--model", model, "--output-format", "json", "--tools", "",
           "--setting-sources", "", "--disable-slash-commands", "--no-session-persistence",
           "--strict-mcp-config", "--system-prompt", system or SYSTEM]
    delay = 5
    for attempt in range(6):
        t0 = time.time()
        p = subprocess.run(cmd, input=prompt, capture_output=True, text=True, cwd=SCRATCH, timeout=300)
        dt = time.time() - t0
        out = p.stdout.strip()
        try:
            d = json.loads(out)
        except json.JSONDecodeError:
            d = {}
        err = (d.get("result") if d.get("is_error") else "") or (p.stderr if p.returncode else "") or ""
        if d and not d.get("is_error") and p.returncode == 0:
            u = d.get("usage") or {}
            tin = u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0) + u.get("cache_creation_input_tokens", 0)
            return LLMResponse(text=d.get("result", ""), cost_usd=d.get("total_cost_usd", 0.0), input_tokens=tin,
                               output_tokens=u.get("output_tokens", 0), latency_s=dt, model=model)
        low = (err + out).lower()
        if "usage limit" in low or "limit reached" in low:
            raise RuntimeError(f"usage limit: {err[:200]}")
        if attempt == 5:
            raise RuntimeError(f"claude call failed: {err[:300]} {out[:200]}")
        time.sleep(delay)
        delay *= 2
    raise RuntimeError("unreachable")


def call(prompt: str, model: str = "haiku", system: str | None = None, purpose: str = "") -> LLMResponse:
    key = hashlib.sha256(f"{model}\0{system or ''}\0{prompt}".encode()).hexdigest()
    f = CACHE / "llm" / f"{key}.json"
    if f.exists():
        r = LLMResponse(**json.loads(f.read_text()))
        r.cached = True
        return r
    r = _run(prompt, model, system)
    with _lock:
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(r.model_dump_json())
        with open(CACHE / "llm_calls.jsonl", "a") as fh:
            fh.write(json.dumps({"ts": datetime.now(timezone.utc).isoformat(), "model": model, "cost": r.cost_usd,
                                 "input_tokens": r.input_tokens, "output_tokens": r.output_tokens,
                                 "latency_s": round(r.latency_s, 2), "purpose": purpose}) + "\n")
    return r


def parse_json(text: str):
    t = text.strip()
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", t)
    try:
        return json.loads(t)
    except json.JSONDecodeError:
        pass
    for o, c in (("{", "}"), ("[", "]")):
        i, j = t.find(o), t.rfind(c)
        if i != -1 and j > i:
            try:
                return json.loads(t[i:j + 1])
            except json.JSONDecodeError:
                continue
    raise ValueError("no JSON in reply")


def call_json(prompt: str, model: str = "haiku", system: str | None = None, purpose: str = ""):
    r = call(prompt, model, system, purpose)
    try:
        return parse_json(r.text), r
    except ValueError:
        r2 = call(prompt + "\n\nReturn ONLY valid JSON, nothing else. No markdown fences.", model, system, purpose + ":retry")
        r2.cost_usd += r.cost_usd
        r2.input_tokens += r.input_tokens
        r2.output_tokens += r.output_tokens
        return parse_json(r2.text), r2
