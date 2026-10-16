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


def validate(name, check, errors):
    """Check one file and return the set of values it contains."""
    seen = {}
    text = (ROOT / name).read_bytes().decode("utf-8")  # read_text hides CRs
    if text and not text.endswith("\n"):
        errors.append(f"{name}: missing trailing newline")
    for lineno, line in enumerate(text.split("\n"), start=1):
        where = f"{name}:{lineno}"
        if line != line.rstrip():
            errors.append(f"{where}: trailing whitespace or CRLF")
        if not line or line.strip().startswith(("#", "=")):
            continue
        value = INLINE_COMMENT.sub(r"\1", line).strip()
        if value in seen:
            errors.append(f"{where}: {value!r} duplicates line {seen[value]}")
        elif problem := check(value):
            errors.append(f"{where}: {value!r} {problem}")
        seen.setdefault(value, lineno)
    return set(seen)


def main():
    errors = []
    if check_regex("(") is None:
        errors.append("pihole-FTL did not reject an invalid regex")
    for allow, block, check in LISTS:
        overlap = validate(allow, check, errors) & validate(block, check, errors)
        errors += [f"{v!r} is in both {allow} and {block}" for v in sorted(overlap)]
    for error in errors:
        print(f"error: {error}")
    print(f"{len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
