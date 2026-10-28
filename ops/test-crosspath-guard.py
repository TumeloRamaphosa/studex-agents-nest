#!/usr/bin/env python3
"""Prove the two publish paths now block a CROSS-PATH duplicate.

THE BUG THIS GUARDS AGAINST
---------------------------
Two independent publishers target the same platforms for the same date:

  A. scripts/daily-post.py   - the PILLAR caption from
      memory/post-queue/<date>-<day>-<pillar>.md. Records what it posted in
      memory/published-<date>-<pillar>.json
  B. studex-content-automation/scripts/blotato-fallback.js - the PENDING
      caption from posts/pending/<date>.json. Records what it posted in the
      pending file's own `fallback.posted` list

Each guard could ONLY see its own record, so on 2026-10-22 Instagram received
TWO DIFFERENT captions the same day:

    8383092  biltong  20:39Z   (via the fallback path)
    8384191  coffee   21:16Z   (via daily-post.py)

They were DIFFERENT posts, not a re-post, so no per-path idempotency guard
could ever have caught them. The fix makes each path read the other's record.

The 09:00 SAST cron payload says "Generate ONE branded social media post",
so one post per platform per date is the intent.

A checker that cannot fail is worthless, so every case is paired with a
NEGATIVE CONTROL: the pre-fix behaviour must FAIL the same assertion.
"""
import importlib.util
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path("/workspace")
DP = ROOT / "scripts" / "daily-post.py"
FB = ROOT / "studex-content-automation" / "scripts" / "blotato-fallback.js"

results = []


def check(name, cond, detail=""):
    results.append((name, bool(cond), detail))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}"
          + (f" -> {detail}" if detail else ""))


# ---------------------------------------------------------------- fixtures
# Mirror the real layout so the ROOT substitutions are meaningful:
#   TMP/memory/                                 (workspace/memory)
#   TMP/studex-content-automation/posts/pending/ (workspace/studex-content-automation/...)
TMP = pathlib.Path(tempfile.mkdtemp(prefix="crosspath-"))
MEM = TMP / "memory"
SA = TMP / "studex-content-automation"
PEND = SA / "posts" / "pending"
MEM.mkdir(parents=True)
PEND.mkdir(parents=True)

DATE = "2026-10-23"
PILLAR = "agents"

# The PILLAR publisher used THREADS only.
(MEM / f"published-{DATE}-{PILLAR}.json").write_text(json.dumps({
    "date": DATE, "pillar": PILLAR,
    "results": {"posted": ["threads"], "failed": []},
    "posted": ["threads"]}))

# The FALLBACK publisher used INSTAGRAM only.
(PEND / f"{DATE}.json").write_text(json.dumps({
    "caption": "test caption",
    "media": {"image": "https://example.invalid/x.jpg"},
    "fallback": {"posted": ["instagram"], "failed": []}}))

print("=== A. daily-post.py sees the FALLBACK's record ===")


def load_dp(path, modname):
    spec = importlib.util.spec_from_file_location(modname, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.ROOT = str(TMP)
    return mod


mod = load_dp(DP, "dp_new")
got = mod.already_published(DATE, PILLAR)
check("daily-post.py sees fallback-published 'instagram'", "instagram" in got,
      f"got={sorted(got)}")
check("daily-post.py still sees its own marker 'threads'", "threads" in got,
      f"got={sorted(got)}")

print()
print("=== B. NEGATIVE CONTROL: the OLD daily-post.py would NOT see it ===")
old_src = DP.read_text()
region = old_src[old_src.index("def pending_published("):old_src.index("def write_marker(")]
old_src = old_src.replace(
    region, region.replace("return published | pending_published(date_str)",
                            "return published"))
tmp_old = TMP / "daily-post-old.py"
tmp_old.write_text(old_src)
mod_old = load_dp(tmp_old, "dp_old")
old_got = mod_old.already_published(DATE, PILLAR)
check("OLD impl does NOT see fallback's 'instagram' (control is real)",
      "instagram" not in old_got, f"old got={sorted(old_got)}")
check("NEW impl is strictly larger than OLD", old_got < got,
      f"old={sorted(old_got)} new={sorted(got)}")

print()
print("=== C. blotato-fallback.js sees the PILLAR's record ===")
shutil.copy(FB, TMP / "fallback.js")
(TMP / "fallback.js").write_text(FB.read_text().replace(
    "const ROOT = path.join(__dirname, '..');",
    f"const ROOT = {json.dumps(str(SA))};"))

STUB = """
const realFetch = global.fetch;
global.fetch = async (url, opts) => {
  if (String(url).includes('/v2/posts')) {
    console.log('WOULD_POST ' + JSON.stringify(JSON.parse(opts.body)));
    return { ok: true, status: 200, text: async () => JSON.stringify({id: 'x'}) };
  }
  return realFetch(url, opts);
};
"""
(TMP / "stub.js").write_text(STUB)


def run_fb(script):
    r = subprocess.run(["node", "-r", str(TMP / "stub.js"), str(script), DATE],
                       capture_output=True, text=True, timeout=60)
    return r.stdout + r.stderr


def posted_pairs(out):
    pairs = []
    for line in out.splitlines():
        if line.startswith("WOULD_POST "):
            payload = json.loads(line[len("WOULD_POST "):])
            p = payload["post"]
            pairs.append((p["content"]["platform"], p["accountId"]))
    return pairs


out = run_fb(TMP / "fallback.js")
print("  fallback output:")
for line in out.strip().splitlines()[:12]:
    print("    " + line)
would = posted_pairs(out)
check("fallback SKIPS threads (pillar publisher already used it)",
      not any(pl == "threads" for pl, _ in would), f"would_post={would}")
check("fallback still attempts linkedin (nobody used it)",
      any(pl == "linkedin" for pl, _ in would), f"would_post={would}")

print()
print("=== D. NEGATIVE CONTROL: the OLD fallback WOULD double-post threads ===")
# Pre-fix behaviour == the cross-path guard call is absent. Remove exactly
# that one line so the control differs from the fixed version by ONE line.
old_fb = FB.read_text()
CALL = "  for (const p of pillarPublished(date)) already.add(p);"
assert CALL in old_fb, "cross-path call site not found"
old_fb = old_fb.replace(CALL, "  // (pre-fix: no cross-path guard)")
(TMP / "fallback-old.js").write_text(old_fb.replace(
    "const ROOT = path.join(__dirname, '..');",
    f"const ROOT = {json.dumps(str(SA))};"))
# The fallback MUTATES the pending file (it records what it posted), so the
# fixture must be restored before the control runs or the control inherits
# the first run's record and skips everything.
(PEND / f"{DATE}.json").write_text(json.dumps({
    "caption": "test caption",
    "media": {"image": "https://example.invalid/x.jpg"},
    "fallback": {"posted": ["instagram"], "failed": []}}))
out2 = run_fb(TMP / "fallback-old.js")
if "WOULD_POST" not in out2:
    print("  !! control script failed to run:")
    for line in out2.strip().splitlines()[:12]:
        print("     " + line)
old_would = posted_pairs(out2)
check("OLD fallback WOULD double-post threads (control is real)",
      any(pl == "threads" for pl, _ in old_would), f"old would_post={old_would}")
check("NEW fallback posts strictly fewer platforms than OLD",
      len(would) < len(old_would), f"new={would} old={old_would}")

print()
print("=== E. the real 2026-10-22 pending file is not disturbed ===")
p22 = ROOT / "studex-content-automation" / "posts" / "pending" / "2026-10-22.json"
d22 = json.loads(p22.read_text())
check("2026-10-22 pending still lists threads+instagram in fallback.posted",
      set(d22.get("fallback", {}).get("posted") or []) == {"threads", "instagram"},
      str(d22.get("fallback")))

shutil.rmtree(TMP, ignore_errors=True)

print()
passed = sum(1 for _, ok, _ in results if ok)
failed = len(results) - passed
print("=" * 62)
print(f"{passed} passed, {failed} failed")
print("=" * 62)
sys.exit(1 if failed else 0)
