"""Tests for the OPS-001 reference implementation."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from publish_gate import build_key, check_batch  # noqa: E402


class KeyBuilderTests(unittest.TestCase):
    def test_separator_is_exact(self):
        self.assertEqual(build_key("Song", "Artist"), "song \u2014 artist")

    def test_unicode_and_case_fold(self):
        self.assertEqual(build_key("Café del Mar", "José"), "cafe del mar \u2014 jose")

    def test_whitespace_collapses(self):
        self.assertEqual(build_key("  A   B ", " C"), "a b \u2014 c")


class GateTests(unittest.TestCase):
    def test_clean_batch_passes_and_emits_keys(self):
        ok, repeats, keys = check_batch(
            [("New Song", "New Artist")], ["old song \u2014 old artist"]
        )
        self.assertTrue(ok)
        self.assertEqual(repeats, [])
        self.assertEqual(keys, ["new song \u2014 new artist"])

    def test_ledger_repeat_is_rejected(self):
        # The documented failure mode: the resolved artefact carries a
        # suffix the plan did not, but its folded key is already ledgered.
        ledger = [build_key("In the Air Tonight - 2015 Remaster", "Phil Collins")]
        ok, repeats, keys = check_batch(
            [("In the Air Tonight - 2015 Remaster", "Phil Collins")], ledger
        )
        self.assertFalse(ok)
        self.assertEqual(repeats[0][2], "REPEAT-IN-LEDGER")
        self.assertEqual(keys, [])

    def test_batch_self_duplicate_is_rejected(self):
        ok, repeats, _ = check_batch([("A", "B"), ("a", "b")], [])
        self.assertFalse(ok)
        self.assertEqual(repeats[0][2], "DUPLICATE-IN-BATCH")

    def test_folded_variants_match(self):
        ledger = [build_key("Beyoncé Live", "Beyoncé")]
        ok, _, _ = check_batch([("Beyonce Live", "BEYONCÉ")], ledger)
        self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main()
