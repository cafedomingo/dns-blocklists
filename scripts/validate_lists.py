#!/usr/bin/env python3
"""Validate list files before pihole-updatelists imports them.

Parsing mirrors pihole-updatelists' textToArray(): blank lines and lines
starting with '#' or '=' are skipped, and "value  # comment" is split on the
first whitespace-preceded '#'.

Regexes are compiled by Pi-hole's own FTL (TRE, POSIX ERE plus Pi-hole
extensions) via `pihole-FTL regex-test`. Pass the command with --ftl, e.g.
--ftl "docker run --rm --entrypoint pihole-FTL pihole/pihole:latest".
Without --ftl the regex compile check is skipped.
"""

from __future__ import annotations

import argparse
import re
import shlex
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit

URL_LISTS = ["blocklists.txt", "allowlists.txt"]
DOMAIN_LISTS = ["allowlist.txt", "blocklist.txt"]
REGEX_LISTS = ["regex-allowlist.txt", "regex-blocklist.txt"]

# Same pattern pihole-updatelists uses (PHP /U makes .* lazy)
INLINE_COMMENT = re.compile(r"^(.*?)\s+#\s*(\S.*)$")
LABEL = re.compile(r"^(?!-)[a-z0-9_-]{1,63}(?<!-)$")

# pihole-FTL regex-test exit codes: 0 = match, 1 = error, 2 = no match
FTL_COMPILE_ERROR = 1


def parse(text: str) -> list[tuple[int, str]]:
    """Return (line number, value) pairs the way pihole-updatelists sees them."""
    entries = []
    for lineno, line in enumerate(text.split("\n"), start=1):
        stripped = line.strip()
        if not line or stripped.startswith("#") or stripped.startswith("="):
            continue
        match = INLINE_COMMENT.match(line)
        value = match.group(1) if match else line
        entries.append((lineno, value.strip()))
    return entries


def check_hygiene(text: str) -> list[str]:
    errors = []
    if "\r" in text:
        errors.append("contains CR characters (use LF line endings)")
    if text and not text.endswith("\n"):
        errors.append("missing trailing newline")
    for lineno, line in enumerate(text.split("\n"), start=1):
        if line.rstrip("\r") != line.rstrip():
            errors.append(f"line {lineno}: trailing whitespace")
    return errors


def check_url(value: str) -> str | None:
    parts = urlsplit(value)
    if parts.scheme != "https":
        return "must be an https:// URL"
    if not parts.hostname:
        return "URL has no host"
    if any(c.isspace() for c in value):
        return "URL contains whitespace"
    return None


def check_domain(value: str) -> str | None:
    if value != value.lower():
        return "must be lowercase"
    if len(value) > 253:
        return "longer than 253 characters"
    if not all(LABEL.match(label) for label in value.split(".")):
        return "not a valid hostname"
    return None


def check_regex(value: str) -> str | None:
    if any(c.isspace() for c in value):
        return "regex contains whitespace"
    return None


def ftl_compile_error(ftl: list[str], pattern: str) -> str | None:
    result = subprocess.run(
        [*ftl, "-q", "regex-test", "example.com", pattern],
        capture_output=True,
        text=True,
    )
    if result.returncode == FTL_COMPILE_ERROR:
        output = (result.stdout + result.stderr).strip()
        return output or "FTL failed to compile regex"
    if result.returncode not in (0, 2):
        raise RuntimeError(
            f"pihole-FTL exited {result.returncode}: {result.stderr.strip()}"
        )
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--ftl", help="command that runs pihole-FTL")
    args = parser.parse_args()
    ftl = shlex.split(args.ftl) if args.ftl else None

    errors: list[str] = []
    values: dict[str, set[str]] = {}

    # Make sure FTL actually reports compile errors before trusting it
    if ftl and ftl_compile_error(ftl, "(") is None:
        errors.append("pihole-FTL did not reject an invalid regex, check --ftl")

    checks = (
        [(name, check_url) for name in URL_LISTS]
        + [(name, check_domain) for name in DOMAIN_LISTS]
        + [(name, check_regex) for name in REGEX_LISTS]
    )
    for name, check in checks:
        path = args.root / name
        if not path.exists():
            errors.append(f"{name}: file is missing")
            continue
        text = path.read_bytes().decode("utf-8")  # keep CRs visible
        errors += [f"{name}: {e}" for e in check_hygiene(text)]

        seen: dict[str, int] = {}
        for lineno, value in parse(text):
            where = f"{name}:{lineno}: {value!r}"
            if value in seen:
                errors.append(f"{where}: duplicate of line {seen[value]}")
                continue
            seen[value] = lineno
            problem = check(value)
            if problem is None and ftl and check is check_regex:
                problem = ftl_compile_error(ftl, value)
            if problem:
                errors.append(f"{where}: {problem}")
        values[name] = set(seen)

    for allow, block in [
        ("allowlists.txt", "blocklists.txt"),
        ("allowlist.txt", "blocklist.txt"),
        ("regex-allowlist.txt", "regex-blocklist.txt"),
    ]:
        for value in sorted(values.get(allow, set()) & values.get(block, set())):
            errors.append(f"{value!r} is in both {allow} and {block}")

    for error in errors:
        print(f"error: {error}")
    if ftl is None:
        print("note: --ftl not given, regexes were not compiled")
    print(f"{len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
