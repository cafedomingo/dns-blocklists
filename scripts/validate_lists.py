#!/usr/bin/env python3
"""Validate list files the way pihole-updatelists and Pi-hole will read them.

Regexes are compiled by Pi-hole's own FTL from the pihole/pihole image, so
this needs Docker.
"""

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
FTL = ["docker", "run", "--rm", "--entrypoint", "pihole-FTL", "pihole/pihole:latest"]

# pihole-updatelists' textToArray() inline comment pattern (PHP /U = lazy)
INLINE_COMMENT = re.compile(r"^(.*?)\s+#\s*\S.*$")
HOSTNAME = re.compile(r"^(?!-)[a-z0-9_-]{1,63}(?<!-)(\.(?!-)[a-z0-9_-]{1,63}(?<!-))*$")


def check_url(value):
    parts = urlsplit(value)
    if parts.scheme != "https" or not parts.hostname:
        return "must be an https:// URL"


def check_domain(value):
    if len(value) > 253 or not HOSTNAME.match(value):
        return "must be a valid lowercase hostname"


def check_regex(value):
    # pihole-FTL regex-test exits 0 on match, 2 on no match, 1 on error
    result = subprocess.run(
        [*FTL, "-q", "regex-test", "example.com", value],
        capture_output=True,
        text=True,
    )
    if result.returncode == 1:
        return (result.stdout + result.stderr).strip() or "FTL rejected regex"
    if result.returncode not in (0, 2):
        sys.exit(f"pihole-FTL failed ({result.returncode}): {result.stderr.strip()}")


LISTS = [
    ("allowlists.txt", "blocklists.txt", check_url),
    ("allowlist.txt", "blocklist.txt", check_domain),
    ("regex-allowlist.txt", "regex-blocklist.txt", check_regex),
]


RESULTS = []


def record(label, problem=None):
    """Print one check result, like a test runner."""
    RESULTS.append(problem is None)
    status = "PASS" if problem is None else "FAIL"
    print(f"  {status}  {label}" + (f": {problem}" if problem else ""))


def validate(name, check):
    """Check one file and return the set of values it contains."""
    print(name)
    seen = {}
    formatting = []
    text = (ROOT / name).read_bytes().decode("utf-8")  # read_text hides CRs
    if text and not text.endswith("\n"):
        formatting.append("missing trailing newline")
    for lineno, line in enumerate(text.split("\n"), start=1):
        if line != line.rstrip():
            formatting.append(f"line {lineno} has trailing whitespace or CRLF")
        if not line or line.strip().startswith(("#", "=")):
            continue
        value = INLINE_COMMENT.sub(r"\1", line).strip()
        label = f"line {lineno}: {value}"
        if value in seen:
            record(label, f"duplicates line {seen[value]}")
        else:
            record(label, check(value))
        seen.setdefault(value, lineno)
    record("formatting", "; ".join(formatting) or None)
    return set(seen)


def main():
    print("pihole-FTL")
    canary = check_regex("(")
    record("rejects an invalid regex", None if canary else "accepted '('")
    for allow, block, check in LISTS:
        overlap = validate(allow, check) & validate(block, check)
        print(f"{allow} vs {block}")
        record("no entry in both", ", ".join(sorted(overlap)) or None)
    failed = RESULTS.count(False)
    print(f"\n{len(RESULTS) - failed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
