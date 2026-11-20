# OPS-001 — The Publish Gate

**A standard for verify-before-commit: check the exact artefacts you are about to commit, against the complete record, after resolution and before the irreversible step — and forbid the commit until the check passes.**

By **Jha'asryel-Akquil Bishop**, Georgetown, Guyana — [jhaasryelakquil.com](https://jhaasryelakquil.com)
Part of the *Open Operations Standards* series: separate publications, one per issue, each with its evidence.

## The issue

Automated pipelines routinely check the *plan* and then commit a *different set of artefacts* than the one that was checked. Where the commit cannot be undone — a published artefact with no removal path, a sent message, a filed submission — every artefact that slipped past the check is permanent.

This standard was written after a documented production failure (2026-09-30): a pipeline cleared planned titles against a ledger, then committed recordings whose resolved titles carried suffixes the plan never showed. Four were already in the ledger. The platform offered no removal. They are still there.

## What the standard requires

1. The gate receives the **resolved** artefacts — never the planned form.
2. Comparison keys come from **one shared key-builder** (Unicode-folded, exact separator), used by the check, the gate, and the ledger write alike.
3. Comparison is against the **complete** ledger, never a recent window.
4. Duplicates **within the batch** are rejected too.
5. A rejected artefact leaves a gap — **no refill, no substitution**.
6. After commit, the ledger is appended with the **gate's own emitted keys**, only for artefacts actually committed.
7. An unreadable ledger **fails the gate**. Never treat a failed read as an empty record.

Full text: [SPEC.md](SPEC.md)

## Reference implementation

`src/publish_gate.py` — dependency-free Python. `build_key()` is the single key-builder; `check_batch()` returns repeats (against the ledger and within the batch) and, for a passing batch, the exact ledger keys to append. Runnable as a CLI over JSON files. Tests in `tests/` (7 tests, all passing).

## Licence

Code: MIT. Specification: CC BY 4.0. See [LICENSE](LICENSE).

## Discussion

Issues on this repository are the discussion venue. Implementations in other languages are welcome and will be linked from here.
