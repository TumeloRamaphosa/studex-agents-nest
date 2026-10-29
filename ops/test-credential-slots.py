#!/usr/bin/env python3
"""The credential-slot guard must FAIL when a slot does not hold a credential.

On 2026-10-28 05:30 a redaction wrote its own source line into the
BLOTATO_API_KEY slot of .env. Every scanner believed a credential was present
because the NAME was present. The API answered 401 and the publish path
would have silently done nothing the next morning.

ops/check-credential-slots.py is the guard that closes that. This test
proves the guard can FAIL - a guard that cannot fail is a comment - and that
it does not fire on healthy credentials.
"""
import importlib.util
import os
import pathlib
import subprocess
import sys
import tempfile

REPO = pathlib.Path("/workspace")
CHECKER = REPO / "ops" / "check-credential-slots.py"

fails = []


def check(name, cond, detail=""):
    if cond:
        print("PASS  %s" % name)
    else:
        print("FAIL  %s %s" % (name, detail))
        fails.append(name)


def load():
    spec = importlib.util.spec_from_file_location("slots", CHECKER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_on(envfile, repo=None):
    cmd = [sys.executable, str(CHECKER), envfile]
    if repo:
        cmd += ["--tracked", str(repo)]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def main():
    mod = load()

    print("--- the classifier ---")
    check("a long alphanumeric token is a CREDENTIAL",
          mod.classify("A" * 40) == "CREDENTIAL")
    check("an empty value is EMPTY", mod.classify("") == "EMPTY")
    check("a short value is TOO-SHORT", mod.classify("abc123") == "TOO-SHORT")
    check("a redaction artefact is a PLACEHOLDER",
          mod.classify('t = t.replace(secret, "***")') == "PLACEHOLDER")
    check("a masked value is a PLACEHOLDER",
          mod.classify("************") == "PLACEHOLDER")
    check("a source line is NOT-A-CREDENTIAL or PLACEHOLDER",
          mod.classify('value = os.environ.get("KEY", "")') != "CREDENTIAL")
    check("a value with spaces is not a CREDENTIAL",
          mod.classify("not a real credential at all") != "CREDENTIAL")

    print("--- the checker against real env files ---")
    work = pathlib.Path(tempfile.mkdtemp(prefix="cred-slots-"))
    try:
        good = work / "good.env"
        good.write_text("BLOTATO_API_KEY=%s\n" % ("B" * 40), encoding="utf-8")
        rc, out = run_on(good)
        check("a healthy slot is CLEAN (rc=0)", rc == 0, out[-300:])
        check("and it says CLEAN", "VERDICT: CLEAN" in out, out[-300:])

        broken = work / "broken.env"
        broken.write_text('BLOTATO_API_KEY=t = t.replace(secret, "***")\n',
                          encoding="utf-8")
        rc, out = run_on(broken)
        check("NEGATIVE CONTROL: a redaction artefact FAILS (rc!=0)", rc != 0,
              "rc=%d" % rc)
        check("and it says BROKEN", "VERDICT: BROKEN" in out, out[-300:])
        check("and it names the slot", "BLOTATO_API_KEY" in out, out[-300:])

        empty = work / "empty.env"
        empty.write_text("BLOTATO_API_KEY=\n", encoding="utf-8")
        rc, out = run_on(empty)
        check("NEGATIVE CONTROL: an empty slot FAILS (rc!=0)", rc != 0,
              "rc=%d" % rc)

        print("--- a credential value in TRACKED SOURCE is caught ---")
        repo = work / "repo"
        (repo / ".git").mkdir(parents=True)
        subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True,
                       capture_output=True)
        secret = "C" * 40
        tracked = repo / "leak.py"
        tracked.write_text('KEY = "%s"\n' % secret, encoding="utf-8")
        envf = work / "leak.env"
        envf.write_text("BLOTATO_API_KEY=%s\n" % secret, encoding="utf-8")
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True,
                       capture_output=True)
        subprocess.run(["git", "-C", str(repo), "-c", "user.email=t@e.invalid",
                        "-c", "user.name=t", "commit", "-q", "-m", "x"],
                       check=True, capture_output=True)
        rc, out = run_on(envf, repo)
        check("NEGATIVE CONTROL: a credential in tracked source FAILS (rc!=0)",
              rc != 0, "rc=%d" % rc)
        check("and it names the file", "leak.py" in out, out[-400:])

        print("--- the pre-flight refuses to publish without a credential ---")
        # The publisher reads the .env FILE, so stripping the variable from
        # the ENVIRONMENT proves nothing - the credential was still in the
        # file and the case passed without exercising the path it claimed
        # to. STUDEX_ENV_FILE points the publisher at a scratch file with
        # no credential in it, so "no credential" is now a REAL state.
        noenv = work / "no-credential.env"
        noenv.write_text("# deliberately empty\n", encoding="utf-8")
        env = {k: v for k, v in os.environ.items()
               if k not in ("BLOTATO_API_KEY", "STUDEX_ENV_FILE")}
        env["STUDEX_ENV_FILE"] = str(noenv)
        p = subprocess.run([sys.executable, str(REPO / "scripts" / "daily-post.py"),
                            "2026-10-27"], capture_output=True, text=True,
                           env=env, timeout=200, cwd=str(REPO))
        out = p.stdout or ""
        check("the publisher refuses without a credential (rc!=0)", p.returncode != 0,
              "rc=%d" % p.returncode)
        check("and it says it is refusing to publish",
              "refusing to publish" in out.lower(), out[-300:])

        env2 = dict(env)
        env2["BLOTATO_API_KEY"] = 't = t.replace(secret, "***")'
        p = subprocess.run([sys.executable, str(REPO / "scripts" / "daily-post.py"),
                            "2026-10-27"], capture_output=True, text=True,
                           env=env2, timeout=200, cwd=str(REPO))
        out = p.stdout or ""
        check("the publisher refuses a redaction artefact (rc!=0)",
              p.returncode != 0, "rc=%d" % p.returncode)
        check("and it says the credential is not shaped like one",
              "not shaped like a credential" in out, out[-300:])
        # The ORDER matters: the credential is a precondition, so it must be
        # checked before any content validation. It used to be checked after
        # the caption validation, which meant a broken credential was only
        # ever reported when the caption happened to be valid - the guard was
        # in the wrong place to protect anything.
        check("the credential is checked BEFORE the content (precondition first)",
              "not shaped like a credential" in out and "validate" not in out.lower(),
              "the credential error should come before any content validation")
    finally:
        import shutil
        shutil.rmtree(work, ignore_errors=True)

    print()
    if fails:
        print("FAILURES: %d -> %s" % (len(fails), fails))
        return 1
    print("ALL CHECKS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
