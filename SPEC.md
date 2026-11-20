# OPS-001 — The Publish Gate

**Version 0.1 · 2026-11-20 · Status: Published**
**Author: Jha'asryel-Akquil Bishop (Georgetown, Guyana)**

## 1. Problem

Automated pipelines routinely perform a correctness check on the *plan* and then commit a *different set of artefacts* than the one that was checked. Where the commit is irreversible — a published playlist that cannot be edited down, a sent message, a filed submission — every artefact that slipped past the check is permanent.

Documented case (VERIFIED, operator record, 2026-09-30): a publishing pipeline checked planned track titles against a ledger and reported them clear. The recordings actually committed carried remaster suffixes not present in the planned titles, and four of them were already in the ledger. The check had run on the wrong strings, and the platform offered no removal. The repeats are still there.

## 2. Rule

**The gate runs on the exact artefacts to be committed, after they are resolved and before the commit, and the commit is forbidden until the gate passes.**

## 3. Requirements

An implementation conforms to OPS-001 when all of the following hold:

1. **Resolved artefacts only.** The gate receives the final, resolved form of each artefact (the exact title, identifier, or payload that will be committed) — never the planned or requested form.
2. **One key-builder.** Comparison keys are built by a single shared function used by the check, the gate, and the ledger write. Keys are normalised by Unicode folding (NFKD), case folding, and whitespace collapse, joined with one exact separator. Ad-hoc key construction at any call site is a conformance failure. (Documented case, VERIFIED, 2026-09-30: a hand-built key missing the spaces around the separator character false-negatived three repeats in one run.)
3. **Full-record comparison.** The gate compares against the complete ledger of previously committed artefacts, not a recent window. (Documented case, VERIFIED, 2026-09-30: a fixed recent-window check missed repeats that a full-frequency check caught the same day.)
4. **Batch self-check.** The gate also detects duplicates *within* the batch being committed.
5. **No refill.** An artefact the gate rejects leaves a gap. The batch ships smaller; a rejected slot is never refilled with a substitute artefact in the same run.
6. **Ledger write from the gate.** On a successful commit, the ledger is appended with the gate's own emitted keys for the artefacts actually committed — never keys rebuilt by hand from the plan.
7. **Fail closed.** If the ledger cannot be read or parsed, the gate fails and the commit does not happen. An unreadable record is never treated as an empty record.

## 4. Reference implementation

`src/publish_gate.py` in this repository implements OPS-001 for a JSON ledger of string keys: `build_key()` is the single key-builder; `check_batch()` returns the repeats (against the ledger and within the batch) and, for a passing batch, the exact ledger keys to append after commit.

## 5. Applicability

Any pipeline with an irreversible or expensive-to-reverse commit: publishing, messaging sends, form submissions, financial postings, deployment pipelines, bulk data writes. The gate is deliberately small — it is a control-flow step, not a framework.
