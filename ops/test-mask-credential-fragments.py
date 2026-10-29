#!/usr/bin/env python3
"""The fragment masker must mask the WHOLE contiguous leak.

2026-10-28. The first version of `ops/mask-credential-fragments.py` grew
a match to the LEFT with the right index and to the RIGHT with the wrong
one (`vi + (b - j)` instead of `vi + (b - a)`). The right-hand extension
therefore stopped as soon as the match had been extended leftwards.

The damage was silent and partial: a 74-character Pinecone key in
`memory/2026-08-22.md` was masked as 22 characters, and the re-scan still
reported CLEAN for that file, because the remaining 52 characters were
shorter than the 12-character minimum? No - they were longer, but the
re-scan's own candidate test used the same broken growth, so it agreed
with the broken masker. 🔑 *Two functions that share a bug agree with each
other, and neither is a control.*

So the tests below check the masker against GROUND TRUTH - the length of
the contiguous run that is actually in the file - not against the
masker's own opinion of it.

Negative controls included:
  * a file with NO fragment is not touched
  * a fragment shorter than the minimum is not masked (the masker is not a
    word-finder)
  * a leak that starts at the very beginning of a file
  * a leak that runs to the very end of a file
  * two different credentials in one file are both masked
"""
import importlib.util
import pathlib
import shutil
import sys
import tempfile

REPO = pathlib.Path("/workspace")
MASKER = REPO / "ops/mask-credential-fragments.py"

spec = importlib.util.spec_from_file_location("mk", MASKER)
mk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mk)

fails = []


def check(name, cond, detail=""):
    if cond:
        print("PASS  %s" % name)
    else:
        print("FAIL  %s %s" % (name, detail))
        fails.append(name)


def tmpfile(name, data):
    d = pathlib.Path(tempfile.mkdtemp(prefix="mask-test-"))
    p = d / name
    p.write_bytes(data)
    return p


print("=== the ground truth: the longest contiguous run in the file ===")
# The ground truth is a credential of the RIGHT SHAPE that is NOT LIVE.
#
# These two used to be pasted in whole, and they were the real values -
# a "synthetic" credential that happens to be the actual one is the worst
# kind of fixture, because it leaks while looking safe. The pre-commit
# guard blocked the commit and was RIGHT to.
#
# A fake credential is only fake if it shares NO 12-character slice with
# a live one, so the characters below are chosen to differ from every
# live key in .env. The shape (prefix + length) is what is under test.
FAKE_PINE = "pcsk_" + "Zz8Qv4Nb7Xc2Lm9Rt5Yu3Io1Pa6Sd4Fg0Hj2Kl8Qw9Er1Ty5Uv3Bz6"
FAKE_MAIL = "am_us_" + "Mx2Qw7Er9Ty4Ui6Op1As3Df5Gh7Jk9Lz1Xc3Vb5Nm8Qw2Er6Rt4Y"
SECRET = FAKE_PINE.encode()
OTHER = FAKE_MAIL.encode()
MID = len(SECRET) // 2
RUN = SECRET[MID:]                      # a 25-character contiguous tail

print()
print("=== 1. a leak in the MIDDLE of a file is masked WHOLE ===")
p = tmpfile("mid.txt", b"before text here\n" + RUN + b"\nafter text\n")
per = mk.mask_file(p, [("PINECONE", SECRET.decode())])
after = p.read_bytes()
check("the file was masked", per.get("PINECONE") == 1, str(per))
check("NO 12+ slice of the secret survives",
      not any(SECRET[i:i + 12] in after for i in range(len(SECRET) - 11)))
check("the surrounding text is intact",
      b"before text here" in after and b"after text" in after)
check("the secret is entirely gone", RUN not in after)
check("the mask is the same length as the run", after.count(b"*") >= len(RUN) - 12)

print()
print("=== 2. the leak at the START of a file ===")
p = tmpfile("start.txt", RUN + b"\nrest of file\n")
mk.mask_file(p, [("PINECONE", SECRET.decode())])
after = p.read_bytes()
check("no 12+ slice survives at the start",
      not any(SECRET[i:i + 12] in after for i in range(len(SECRET) - 11)))
check("the rest of the file is intact", b"rest of file" in after)

print()
print("=== 3. the leak at the END of a file ===")
p = tmpfile("end.txt", b"header\n" + RUN)
mk.mask_file(p, [("PINECONE", SECRET.decode())])
after = p.read_bytes()
check("no 12+ slice survives at the end",
      not any(SECRET[i:i + 12] in after for i in range(len(SECRET) - 11)))
check("the header is intact", b"header" in after)

print()
print("=== 4. the WHOLE secret present ===")
p = tmpfile("full.txt", b"key: " + SECRET + b"\n")
mk.mask_file(p, [("PINECONE", SECRET.decode())])
after = p.read_bytes()
check("the whole secret is gone", SECRET not in after)
check("nothing 12+ survives",
      not any(SECRET[i:i + 12] in after for i in range(len(SECRET) - 11)))

print()
print("=== NEGATIVE CONTROL 1: a file with NO fragment is untouched ===")
clean = b"this file mentions a pinecone index but holds no key material at all\n"
p = tmpfile("clean.txt", clean)
before_ino = p.stat().st_ino
per = mk.mask_file(p, [("PINECONE", SECRET.decode())])
check("nothing was masked", per == {}, str(per))
check("the bytes are unchanged", p.read_bytes() == clean)
check("the inode is unchanged", p.stat().st_ino == before_ino)

print()
print("=== NEGATIVE CONTROL 2: a fragment SHORTER than the minimum is left alone ===")
short = SECRET[:8]
p = tmpfile("short.txt", b"x " + short + b" y\n")
per = mk.mask_file(p, [("PINECONE", SECRET.decode())])
check("an 8-character run is NOT masked", per == {}, str(per))
check("and the bytes are unchanged", short in p.read_bytes())

print()
print("=== NEGATIVE CONTROL 3: a DIFFERENT credential is not masked ===")
p = tmpfile("other.txt", b"value " + OTHER + b"\n")
per = mk.mask_file(p, [("PINECONE", SECRET.decode())])
check("another key is untouched", per == {}, str(per))
check("and its bytes survive", OTHER in p.read_bytes())

print()
print("=== 5. two credentials in ONE file are both masked ===")
p = tmpfile("two.txt", b"a " + SECRET[MID:] + b" b " + OTHER[6:] + b"\n")
per = mk.mask_file(p, [("PINECONE", SECRET.decode()), ("AGENTMAIL", OTHER.decode())])
after = p.read_bytes()
check("both credentials were reported", len(per) == 2, str(per))
check("neither 12+ slice survives",
      not any(SECRET[i:i + 12] in after for i in range(len(SECRET) - 11))
      and not any(OTHER[i:i + 12] in after for i in range(len(OTHER) - 11)))

print()
print("=== 6. the masker's own candidate filter is not vacuous ===")
check("a file holding the secret is a candidate",
      mk.candidate_credentials(SECRET, [("P", SECRET.decode())]) != [])
check("a file NOT holding the secret is not a candidate",
      mk.candidate_credentials(b"nothing here", [("P", SECRET.decode())]) == [])

print()
print("=== 7. the growth is measured against GROUND TRUTH, not the masker ===")
# The longest contiguous run of SECRET that appears in the data:
data = b"zz" + SECRET[MID:] + b"zz"
best = 0
for L in range(len(SECRET), 11, -1):
    if any(SECRET[i:i + L] in data for i in range(len(SECRET) - L + 1)):
        best = L
        break
check("ground truth finds a run of %d characters" % best, best >= len(SECRET) - MID,
      "best=%d" % best)
p = tmpfile("ground.txt", data)
mk.mask_file(p, [("PINECONE", SECRET.decode())])
after = p.read_bytes()
masked = best  # every character of the run must be masked
check("the WHOLE %d-character run is masked, not part of it" % masked,
      not any(SECRET[i:i + 12] in after for i in range(len(SECRET) - 11)))

print()
if fails:
    print("FAILURES: %d -> %s" % (len(fails), fails))
    sys.exit(1)
print("ALL CHECKS PASS")
