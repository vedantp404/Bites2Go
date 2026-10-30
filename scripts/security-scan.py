"""Bounded pattern scan: working tracked files, reachable Git blobs, optional exports.
Reports locations/types only. Not a substitute for a full secret detector or review.
Run from any directory: python scripts/security-scan.py --artifact <export-dir>
"""
import argparse
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = {
    "private key": rb"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----",
    "AWS access identifier": rb"(?:AKIA|ASIA)[A-Z0-9]{16}",
    "GitHub token": rb"(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{50,})",
    "Supabase secret": rb"sb_secret_[A-Za-z0-9_-]{20,}",
    "JWT-shaped credential": rb"eyJ[A-Za-z0-9_-]{15,}\.eyJ[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{20,}",
}

def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args])

def matches(data):
    return [kind for kind, pattern in PATTERNS.items() if re.search(pattern, data)]

def scan():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path)
    args = parser.parse_args()
    findings = []
    count = 0

    def inspect(label, data):
        nonlocal count
        count += 1
        findings.extend((label, kind) for kind in matches(data))

    for raw in git("ls-files", "-z", "--cached", "--others", "--exclude-standard").split(b"\0"):
        if not raw:
            continue
        name = raw.decode("utf-8")
        path = ROOT / name
        if path.is_file():
            inspect(name, path.read_bytes())
        if path.name.startswith(".env") and path.name != ".env.example":
            findings.append((name, "tracked/unignored environment file"))
        if path.suffix.lower() in {".db", ".sqlite", ".sqlite3", ".keystore", ".jks", ".apk", ".aab"}:
            findings.append((name, "database, signing material or generated build"))

    objects = git("rev-list", "--objects", "--all").splitlines()
    # One batch process; no values from objects are printed.
    ids = [line.split(b" ", 1)[0] for line in objects]
    proc = subprocess.run(["git", "-C", str(ROOT), "cat-file", "--batch"],
                          input=b"\n".join(ids)+b"\n", stdout=subprocess.PIPE, check=True)
    offset = 0
    blobs = 0
    for oid in ids:
        end = proc.stdout.index(b"\n", offset)
        header = proc.stdout[offset:end].split()
        size = int(header[2])
        data = proc.stdout[end+1:end+1+size]
        offset = end+size+2
        if header[1] == b"blob":
            blobs += 1
            inspect("git blob " + oid.decode(), data)
    artifacts = 0
    if args.artifact:
        if not args.artifact.is_dir():
            parser.error("artifact must be an existing export directory")
        for path in args.artifact.rglob("*"):
            if path.is_file():
                artifacts += 1
                inspect("export/" + str(path.relative_to(args.artifact)), path.read_bytes())
    for label, kind in findings:
        print(f"FINDING {kind}: {label}")
    print(f"Scanned {count} files/blobs ({blobs} historical blobs, {artifacts} export files); {len(findings)} pattern findings.")
    return bool(findings)

if __name__ == "__main__":
    raise SystemExit(scan())
