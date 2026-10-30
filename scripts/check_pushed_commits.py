#!/usr/bin/env python3
"""Pre-push: every commit being pushed must follow Conventional Commits (checked by commitizen).

pre-commit passes the pushed range as PRE_COMMIT_FROM_REF and PRE_COMMIT_TO_REF. A new branch has
no remote ref to compare with, so every commit reachable from the pushed head is checked instead.
"""

from __future__ import annotations

import os
import subprocess
import sys

NO_REF = {"", "0" * 40}


def main() -> int:
    """Run `cz check` over the pushed commits and return its exit code."""
    to_ref = os.environ.get("PRE_COMMIT_TO_REF", "HEAD")
    from_ref = os.environ.get("PRE_COMMIT_FROM_REF", "")
    rev_range = to_ref if from_ref in NO_REF else f"{from_ref}..{to_ref}"
    return subprocess.run(["cz", "check", "--rev-range", rev_range], check=False).returncode  # noqa: S603, S607


if __name__ == "__main__":
    sys.exit(main())
