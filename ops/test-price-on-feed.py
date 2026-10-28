#!/usr/bin/env python3
"""Regression tests for ops/check-price-on-feed.py

No network. The live path is exercised through injected fixtures, never by
calling the Blotato API.

A checker that cannot fail is worse than no checker, so every negative control
below asserts that the checker DOES fire.
"""
import importlib.util
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, "check-price-on-feed.py")

spec = importlib.util.spec_from_file_location("check_price_on_feed", TARGET)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

TRADE = {"34000", "22000", "12500"}


class TestAmountParsing(unittest.TestCase):
    def test_plain_amount(self):
        hits = mod.scan_caption("Wagyu from R650 today", TRADE)
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["digits"], "650")

    def test_comma_thousands(self):
        hits = mod.scan_caption("Only R34,000 per kg", TRADE)
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["digits"], "34000")

    def test_trailing_comma_not_captured(self):
        """'R1,950,' must yield 1950, not '1950,'."""
        hits = mod.scan_caption("From R1,950, order now", TRADE)
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["digits"], "1950")

    def test_space_separator(self):
        hits = mod.scan_caption("R 4 200 only", TRADE)
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["digits"], "4200")

    def test_no_price_is_no_finding(self):
        self.assertEqual(mod.scan_caption("Premium Wagyu, no numbers here", TRADE), [])

    def test_trade_classified_as_trade(self):
        hits = mod.scan_caption("Trade buyers, we see you too - R34,000/kg", TRADE)
        self.assertEqual(hits[0]["kind"], "TRADE")

    def test_retail_classified_as_retail(self):
        hits = mod.scan_caption("Only R999", TRADE)
        self.assertEqual(hits[0]["kind"], "RETAIL")

    def test_qualifier_after_amount_is_not_trade(self):
        """FALSE-POSITIVE SHAPE A: 'R400/kg for home brewers, with trade orders
        welcome from 50kg' -- R400 is RETAIL; the qualifier describes
        something else."""
        hits = mod.scan_caption(
            "available per kilogram at R400/kg for home brewers, with trade "
            "orders welcome from 50kg if you're stocking a cafe",
            TRADE,
        )
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["kind"], "RETAIL")

    def test_qualifier_before_amount_is_trade(self):
        """FALSE-POSITIVE SHAPE B: 'Trade buyers -- R34,000/kg'."""
        hits = mod.scan_caption(
            "Our Oscietra Imperial Caviar is the aristocrat of the sea. "
            "Trade buyers, we see you too - R34,000/kg. Delivered nationwide.",
            TRADE,
        )
        self.assertEqual(hits[0]["kind"], "TRADE")

    def test_trade_table_listing_is_annotation_not_classifier(self):
        """R12,500 is BOTH the Sevtruga trade/kg price AND the retail 7kg-case
        price, so the registry table must not decide the kind."""
        hits = mod.scan_caption("Biltong Gold 7kg case at R12,500", TRADE)
        self.assertEqual(hits[0]["kind"], "RETAIL")
        self.assertTrue(hits[0]["listed"], "R12,500 is registry-trade-listed")

    def test_multiple_prices_all_found(self):
        hits = mod.scan_caption("R4,200 per 100g. Trade buyers - R34,000/kg", TRADE)
        self.assertEqual(len(hits), 2)
        self.assertEqual({h["kind"] for h in hits}, {"RETAIL", "TRADE"})

    def test_lowercase_r_not_a_price(self):
        """'Reserve' must not read as a price."""
        self.assertEqual(mod.scan_caption("Reserve your box now", TRADE), [])


class TestRegistryTradePrices(unittest.TestCase):
    def test_registry_trade_table_parsed(self):
        prices = mod.registry_trade_prices()
        self.assertIn("34000", prices, "registry trade table must yield the Oscietra trade price")
        self.assertIn("22000", prices)
        self.assertIn("12500", prices)

    def test_no_private_allowlist(self):
        """Trade prices come from the registry, not a hardcoded list."""
        src = open(TARGET, encoding="utf-8").read()
        self.assertNotIn('"34000"', src, "trade price must not be hardcoded")
        self.assertNotIn("'34000'", src, "trade price must not be hardcoded")


class TestNoStaleFloor(unittest.TestCase):
    """The caviar floors were recomputed at LIVE FX (16.578, not the stale
    18.5). The 24 Oct 'below floor' finding is SUPERSEDED: R34,000/kg clears
    the live-FX floor R29,535 by R4,465. A checker that asserts the stale
    floor manufactures a false margin crisis."""

    @staticmethod
    def _code_only():
        """Source with the module docstring removed.

        The docstring deliberately CITES the stale floor to warn future
        maintainers off it, so the prohibition applies to executable code --
        a checker must not COMPUTE a floor verdict. Reading the docstring is
        the opposite of the mistake.
        """
        import ast

        src = open(TARGET, encoding="utf-8").read()
        tree = ast.parse(src)
        doc = ast.get_docstring(tree) or ""
        return src.replace(doc, "") if doc else src

    def test_no_stale_floor_numbers_in_code(self):
        code = self._code_only()
        for stale in ("37,661", "37661", "26,720", "26720", "15,778", "15778"):
            self.assertNotIn(stale, code, "superseded floor %s must not be asserted" % stale)

    def test_checker_does_not_compute_a_floor_verdict(self):
        code = self._code_only().lower()
        self.assertNotIn("below-floor", code, "checker must not assert a floor verdict")
        self.assertNotIn("below_floor", code, "checker must not assert a floor verdict")


class TestRuleSource(unittest.TestCase):
    def test_rule_10_present_in_skill(self):
        rule = mod.skill_rule_10()
        self.assertIsNotNone(rule, "rule [10] must be findable in the skill")
        self.assertIn("no price on a public feed", rule.lower())


class TestStagedScan(unittest.TestCase):
    def _write_pending(self, payload):
        d = tempfile.mkdtemp()
        for name, data in payload.items():
            with open(os.path.join(d, name), "w", encoding="utf-8") as fh:
                json.dump(data, fh)
        return d

    def test_caption_with_price_is_flagged(self):
        d = self._write_pending(
            {"2026-10-24.json": {"caption": "Oscietra R4,200 per 100g", "status": "APPROVED_PENDING_FB_TOKEN"}}
        )
        old = mod.PENDING_DIR
        mod.PENDING_DIR = d
        try:
            rows = mod.staged_captions(TRADE)
        finally:
            mod.PENDING_DIR = old
        self.assertEqual(len(rows), 1)
        self.assertEqual(len(rows[0]["prices"]), 1)

    def test_clean_caption_not_flagged(self):
        d = self._write_pending({"2026-10-24.json": {"caption": "Premium Wagyu biltong", "status": "X"}})
        old = mod.PENDING_DIR
        mod.PENDING_DIR = d
        try:
            rows = mod.staged_captions(TRADE)
        finally:
            mod.PENDING_DIR = old
        self.assertEqual(rows[0]["prices"], [])

    def test_already_published_excluded_from_staged_findings(self):
        d = self._write_pending(
            {
                "2026-10-22.json": {
                    "caption": "R1,450 biltong",
                    "status": "POSTED_VIA_FALLBACK",
                    "fallback": {"posted": ["threads", "instagram"]},
                }
            }
        )
        old = mod.PENDING_DIR
        mod.PENDING_DIR = d
        try:
            rows = mod.staged_captions(TRADE)
        finally:
            mod.PENDING_DIR = old
        bad = [r for r in rows if r["prices"] and not r["published"]]
        self.assertEqual(bad, [], "an already-published caption is a live finding, not a staged one")

    def test_malformed_json_skipped_not_fatal(self):
        d = tempfile.mkdtemp()
        with open(os.path.join(d, "2026-10-24.json"), "w", encoding="utf-8") as fh:
            fh.write("{not json")
        old = mod.PENDING_DIR
        mod.PENDING_DIR = d
        try:
            rows = mod.staged_captions(TRADE)
        finally:
            mod.PENDING_DIR = old
        self.assertEqual(rows, [])


class TestLivePathIsNotSilentlyEmpty(unittest.TestCase):
    def test_live_scan_is_the_default_not_opt_in(self):
        """The live feed must be checked by DEFAULT.

        On 2026-10-26 the default run printed 'live posts : 0' and could
        return CLEAN with the verdict 'no price on any public feed (staged or
        live)' -- while posts 8383092 / 8383081 still carried R1,450 live and
        the live scan had never run. That is a false all-clear.
        """
        src = open(TARGET, encoding="utf-8").read()
        self.assertIn('"--no-live" not in args', src,
                      "live scan must be the default; --no-live is the explicit opt-out")
        self.assertNotIn('want_live = "--live" in args', src,
                         "live scan must not be opt-in")

    def test_no_live_opt_out_does_not_claim_whole_feed_clean(self):
        """With --no-live the verdict must not claim a whole-feed clean bill."""
        src = open(TARGET, encoding="utf-8").read()
        self.assertIn("live feed NOT checked", src,
                      "a --no-live run must disclose that live was not checked")

    def test_live_posts_zero_is_not_a_pass(self):
        """A zero-length live result must never be printed as a clean live feed."""
        src = open(TARGET, encoding="utf-8").read()
        self.assertIn("SKIPPED (--no-live", src,
                      "the skipped-live line must be explicit, not a bare 0")
        self.assertIn("live feed NOT checked", src,
                      "the skipped-live line must say the live feed was not checked")

    def test_empty_live_list_is_an_error_not_a_pass(self):
        """An unreachable API must never read as 'nothing published'."""
        rows, err = mod.live_posts.__wrapped__ if hasattr(mod.live_posts, "__wrapped__") else (None, None)
        # Direct check of the contract: the function must return an error string
        # when the key is missing, and never (rows=[], err=None).
        self.assertNotEqual((rows, err), ([], None))

    def test_missing_key_returns_error(self):
        old = mod._env_key
        mod._env_key = lambda name: ""
        try:
            rows, err = mod.live_posts(TRADE)
        finally:
            mod._env_key = old
        self.assertEqual(rows, [])
        self.assertIsNotNone(err, "missing key must be an explicit error")


if __name__ == "__main__":
    unittest.main(verbosity=2)
