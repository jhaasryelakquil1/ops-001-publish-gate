"""OPS-001 reference implementation — the Publish Gate.

Verify the exact artefacts to be committed against the full ledger of
previously committed artefacts, after resolution and before commit.
The commit is forbidden until the gate passes.

Key rules implemented (see specs/OPS-001-publish-gate.md):
  * one shared key-builder (NFKD fold, case fold, whitespace collapse,
    one exact separator) used by the check, the gate and the ledger write;
  * comparison against the COMPLETE ledger, never a recent window;
  * duplicates within the batch are also rejected;
  * a rejected artefact leaves a gap — no refill, no substitution;
  * on success the gate emits the exact ledger keys to append, and only
    for artefacts actually committed;
  * an unreadable ledger fails the gate (fail closed).

Usage (CLI):
    python3 publish_gate.py LEDGER.json CANDIDATES.json
  LEDGER.json     — a JSON list of existing ledger keys (gate-built form)
  CANDIDATES.json — a JSON list of {"title": ..., "creator": ...} objects
                    (the RESOLVED artefacts, exactly as they will be committed)
Exit code 0 = gate passed; the ledger keys to append are printed, one per
line, after a line containing only "LEDGER_KEYS". Exit code 1 = gate
failed; every repeat is printed. Exit code 2 = ledger unreadable.
"""

from __future__ import annotations

import json
import sys
import unicodedata

SEPARATOR = " \u2014 "  # space, EM DASH, space — the one exact separator


def _fold(text: str) -> str:
    folded = unicodedata.normalize("NFKD", str(text))
    folded = folded.encode("ascii", "ignore").decode("ascii")
    return " ".join(folded.lower().split())


def build_key(*parts: str) -> str:
    """The single key-builder. Every comparison in the system uses this."""
    return SEPARATOR.join(_fold(part) for part in parts)


def check_batch(candidates, ledger_keys):
    """Check resolved candidates against the full ledger.

    candidates: list of tuples of key parts, e.g. [("Title", "Creator"), ...]
    ledger_keys: iterable of existing ledger keys (built by build_key)

    Returns (ok, repeats, new_keys):
      ok       — True when the batch may be committed
      repeats  — list of (index, key, reason) for every rejected artefact;
                 reason is "REPEAT-IN-LEDGER" or "DUPLICATE-IN-BATCH"
      new_keys — the gate-built ledger keys to append after a successful
                 commit (empty when the gate fails)
    """
    ledger = set(ledger_keys)
    seen_in_batch = {}
    repeats = []
    new_keys = []
    for index, parts in enumerate(candidates):
        key = build_key(*parts)
        if key in ledger:
            repeats.append((index, key, "REPEAT-IN-LEDGER"))
        elif key in seen_in_batch:
            repeats.append((index, key, "DUPLICATE-IN-BATCH"))
        else:
            seen_in_batch[key] = index
            new_keys.append(key)
    if repeats:
        return False, repeats, []
    return True, [], new_keys


def main(argv) -> int:
    if len(argv) != 3:
        print("usage: publish_gate.py LEDGER.json CANDIDATES.json", file=sys.stderr)
        return 2
    try:
        with open(argv[1], encoding="utf-8") as fh:
            ledger_keys = json.load(fh)
        if not isinstance(ledger_keys, list):
            raise ValueError("ledger is not a list")
    except Exception as exc:  # fail closed: unreadable ledger = no commit
        print(f"GATE FAILED: ledger unreadable ({exc})", file=sys.stderr)
        return 2
    with open(argv[2], encoding="utf-8") as fh:
        raw = json.load(fh)
    candidates = [(item["title"], item["creator"]) for item in raw]
    ok, repeats, new_keys = check_batch(candidates, ledger_keys)
    if not ok:
        for index, key, reason in repeats:
            print(f"{reason}: candidate {index}: {key}")
        return 1
    print("GATE PASSED")
    print("LEDGER_KEYS")
    for key in new_keys:
        print(key)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
