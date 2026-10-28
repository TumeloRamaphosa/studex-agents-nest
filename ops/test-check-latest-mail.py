#!/usr/bin/env python3
"""Regression tests for ops/check-latest-mail.py.

The bug this pins: a mail probe that fetches nothing must never print
"no new mail". Three separate shape assumptions broke in one heartbeat
pass, and each produced a confident, wrong all-clear:

  * the inbox list key is "inboxes", not "items"
  * the inbox handle is "inbox_id", not "address"/"name"
  * the messages list key is "messages", not "items"

So the tests below use the API's REAL shapes, and assert the contract:
a sweep that proved nothing exits 2 and says so out loud.

NOTE ON FIXTURES: every address used below is either a LIVE address from
ops/live-inbox-allowlist.txt or a non-Studex example domain. A test may
not invent a mailbox on our own domain - ops/dead-inbox-check.py reads
those as a real address nobody can read, and it is right to.
"""
import importlib.util
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location(
    "check_latest_mail", ROOT / "ops" / "check-latest-mail.py")
clm = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(clm)

# Live, allowlisted inboxes.
A1 = "t.ramaphosa@agentmail.to"
A2 = "naledi-cmo@studex-group.com"
A3 = "sales@studex-group.com"
A4 = "meat@studex-group.com"
# A genuine external party.
EXT = "buyer@example.com"


class TestRealApiShapes(unittest.TestCase):
    """The parser must handle the shapes the API actually returns."""

    def test_inbox_list_uses_inboxes_key_not_items(self):
        payload = {"count": 2, "limit": 200, "inboxes": [
            {"inbox_id": A1, "email": A1, "display_name": "A"},
            {"inbox_id": A2, "email": A2, "display_name": "B"},
        ]}
        self.assertEqual(clm.parse_inboxes(payload), [A1, A2])

    def test_inbox_handle_is_inbox_id_not_address(self):
        payload = {"inboxes": [{"inbox_id": A1}]}
        self.assertEqual(clm.parse_inboxes(payload), [A1])

    def test_inbox_handle_falls_back_to_address_then_email(self):
        self.assertEqual(
            clm.parse_inboxes({"inboxes": [{"address": "alpha@example.org"}]}),
            ["alpha@example.org"])
        self.assertEqual(
            clm.parse_inboxes({"inboxes": [{"email": "beta@example.org"}]}),
            ["beta@example.org"])

    def test_messages_use_messages_key_not_items(self):
        payload = {"count": 1, "limit": 10, "messages": [
            {"sent_at": "2026-10-26T09:00:07.281Z", "from": A3,
             "subject": "Re: biltong bulk pricing"}]}
        msgs = clm.parse_messages(payload)
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0]["subject"], "Re: biltong bulk pricing")

    def test_empty_payloads_parse_to_empty_lists(self):
        self.assertEqual(clm.parse_inboxes({}), [])
        self.assertEqual(clm.parse_inboxes({"inboxes": []}), [])
        self.assertEqual(clm.parse_messages({}), [])
        self.assertEqual(clm.parse_messages({"messages": []}), [])


class TestAssessContract(unittest.TestCase):
    """The core contract: a broken sweep must NOT read as 'no mail'."""

    def test_zero_inboxes_is_could_not_prove_not_clean(self):
        r = clm.assess({}, [])
        self.assertEqual(r["rc"], 2)
        self.assertIn("COULD NOT PROVE", r["verdict"])
        self.assertIn("NOT an empty mailbox", r["verdict"])

    def test_zero_messages_across_visible_inboxes_is_could_not_prove(self):
        r = clm.assess({A1: "k"}, [])
        self.assertEqual(r["rc"], 2)
        self.assertIn("COULD NOT PROVE", r["verdict"])
        self.assertIn("response-shape change", r["verdict"])

    def test_a_real_sweep_is_clean(self):
        msgs = [{"sent_at": "2026-10-26T09:00:07.281Z", "from": A3,
                 "subject": "Re: biltong bulk pricing"}]
        r = clm.assess({A1: "k"}, msgs)
        self.assertEqual(r["rc"], 0)
        self.assertIn("VERDICT: OK", r["verdict"])
        self.assertEqual(r["messages"], 1)
        self.assertEqual(r["inboxes"], 1)

    def test_newest_is_the_max_timestamp_not_the_first(self):
        msgs = [
            {"sent_at": "2026-10-20T01:00:00.000Z", "from": A2},
            {"sent_at": "2026-10-26T09:00:07.281Z", "from": A3},
            {"sent_at": "2026-10-22T01:00:00.000Z", "from": A4},
        ]
        r = clm.assess({A1: "k"}, msgs)
        self.assertEqual(r["newest"][0], "2026-10-26T09:00:07.281Z")
        self.assertEqual(r["newest"][1], A3)

    def test_external_arrival_is_counted_after_since(self):
        msgs = [
            {"sent_at": "2026-10-26T10:00:00.000Z", "from": EXT,
             "subject": "Enquiry"},
            {"sent_at": "2026-10-26T11:00:00.000Z", "from": A2,
             "subject": "internal"},
        ]
        r = clm.assess({A1: "k"}, msgs,
                        since="2026-10-26T09:00:07.281Z")
        self.assertEqual(r["rc"], 0)
        self.assertEqual(len(r["external_since"]), 1)
        self.assertEqual(r["external_since"][0][1], EXT)
        self.assertIn("no external arrival", r["verdict"])

    def test_own_domain_senders_are_not_external(self):
        for s in (A1, A2, A3, "info@studexmeat.com"):
            self.assertFalse(clm.is_external(s), s)
        self.assertTrue(clm.is_external(EXT))

    def test_timestamp_and_sender_helpers_tolerate_odd_rows(self):
        self.assertEqual(clm.ts_of("not a dict"), "")
        self.assertEqual(clm.sender_of(None), "")
        self.assertEqual(clm.subject_of({}), None)


if __name__ == "__main__":
    unittest.main(verbosity=2)
