# 2026-10-27 — a failed HTTP probe printed the previous provider's answer; the content agent published an unregistered ribeye price

**Found:** 2026-10-27 ~21:15–21:50 UTC (heartbeat pass, probing my own tooling).
**Fixed:** commit `822b4655`.

Two real defects, both in the "a checker that lies about what it protects" family. Neither
was found by a checker — both were found by *probing the checkers*.

---

## 1. A FAILED PROBE PRINTED ANOTHER PROBE'S ANSWER

`ops/check-content-agent.py` probed several LLM providers **in sequence**, each writing its
response to the **same fixed path** and then reading that path back:

```python
cmd = ["curl", "-s", "-o", "/tmp/llm.out", "-w", "%{http_code}", ...]
out = open("/tmp/llm.out").read()[:200]
```

curl only writes its `-o` target when it actually **receives** a response. On a connection
failure it exits non-zero and **leaves the previous file exactly as it was**. Proven, not
assumed:

```
$ printf STALE > /tmp/probe-stale-test.out
$ curl -s --max-time 5 -o /tmp/probe-stale-test.out -w "%{http_code}" \
      -X POST http://127.0.0.1:1/unreachable
000
$ cat /tmp/probe-stale-test.out
STALE
```

So a **dead** provider printed the **previous provider's response body** under its own name:

```
moonshot    HTTP 000  {"id":"chatcmpl-...",...}   <- real
openai      HTTP 000  {"id":"chatcmpl-...",...}   <- MOONSHOT's body
```

A repair tool that shows a dead provider as alive **misdirects the repair**, and it erred in
the direction that **hides** a fault.

### 🔑 The root cause is the CHANNEL, not the path

A **file** carried the response from curl to Python, so a stale read was possible. **stdout is
the channel; the file was the accident.** New `ops/http_probe.py` uses stdout — so there is no
file to go stale, two concurrent probes cannot collide, and nothing is left in `/tmp` for the
credential-surface audit to trip over.

`ops/check-catalog.py` and `ops/check-content-agent.py` now use it.

**Test:** `ops/test-http-probe.py` — 10 assertions including a **negative control** that
reproduces the original stale read, so the test is not vacuous.

---

## 2. The content agent published an UNREGISTERED price

The content agent's `studex-content-automation/products/catalog.json` carried:

```json
"id": "wagyu-ribeye", "price": "From R1,950", "price_raw": 1950, "allowed_prices": [1950]
```

The live store (`studexmeat.com/products/ribeye-steak`) sells it as **two variants**:

| Variant | Price | Was |
|---|---|---|
| 500g | **R950** | R1,569 |
| 1kg | **R1,950** | R2,939 |

🔑 **"From" means the CHEAPEST variant, and the cheapest is R950.** "From R1,950" is the 1kg
price — so a Facebook post **overstated the entry price by R1,000 (105%)**. The convention
already set on 21 Oct (registry §2.1) is to quote **live Shopify sale pricing**.

Worse: the price was **UNOWNED**. `git log -S "Ribeye" -- studex-meat/PRICE-SOURCE-REGISTRY.md`
returns **nothing** — the registry had **no** row for a retail ribeye at all. So nothing owned
it, nothing checked it, and nothing would have seen it change. And the content agent's own
guard **cannot** catch it: its `allowed_prices` live in the same `catalog.json`, so it was
**self-certifying**.

### 🔑 The check that should have caught it could not

`check-catalog.py` compared `price in reg` — a literal **substring** test of the whole price
**string**. That produced **false negatives** too: `"R4,200 per 100g"` and `"R400/kg"` are
registry prices written with a unit suffix, so **two of six products** were wrongly reported as
unregistered.

**Fixed:**
- `check-catalog.py` now compares the **numeric** price — the format-independent unit — and
  flags any catalog product whose price is absent from the registry. It was proven to **FAIL**
  (`VERDICT: UNOWNED PRICE`) on the ribeye **before** the fix, then went **CLEAN** after it.
- **Registry §2.9** added: the two Wagyu Ribeye Steak variant rows, owner = the live Shopify
  product page, with the reasoning recorded in place.
- `catalog.json` corrected: `price` "From R950", `price_raw` 950, `variants` `["500g","1kg"]`,
  `allowed_prices` `[950, 1950]`.

**Verified after the change:** `check-catalog.py` CLEAN (0 unowned) · `drift-check` 18 pages /
18 clean / 0 drift / 0 unreachable · the content agent's own guard tests ALL PASS.

---

## ⚠️ Surfaced, NOT fixed — for Tumelo

**The canonical static retail site (`nudsduvyrc12`) carries NO steak range**, though the live
store sells a `Steaks` collection: ribeye, chuckeye, sirloin, t-bone, tri-tip, tomahawk, rump,
fillet, picanha and the Ankole cuts. The store's own registry §4 note already flagged the
"Steaks" collection as existing but unowned. Adding a category to the canonical sales surface
is a **build + redeploy + price-registry** decision, not a heartbeat fix. Recorded in registry
§2.9.

---

## 🔑 The transferable lessons

🔑 **A checker that reads a file it did not just write is reading a stale value.** This bit
today's pre-flight (which read a *clock* instead of the target date) and now two HTTP probes.
Both are the same shape: **the thing you read is not the thing you meant to read.**

🔑 **A checker that carries a value through a FILE can lie.** stdout has no stale state. If you
need a value to survive between two processes, make sure the failure path cannot leave the old
one behind — or don't use a file.

🔑 **A self-certifying guard is not a guard.** The content agent's `allowed_prices` sat in the
same file it was meant to police. A rule whose source and subject are the same artefact cannot
detect drift.

🔑 **Prove a check can FAIL before you trust it to PASS.** `check-catalog.py` was green (well —
it was green *and wrong*, reporting 2 of 6 products as unregistered for the wrong reason). It
was only after it was rewritten that it could be seen to fail on the real defect.

🔑 **Compare on the NORMALISED value, not the formatted string.** `"R4,200 per 100g"` and
`"R4,200"` are the same price. A substring test on a formatted string cannot tell a formatting
difference from a genuine absence.
