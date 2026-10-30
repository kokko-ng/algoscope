#!/usr/bin/env python3
"""Fail when a text file contains emoji. Box drawing and geometric shapes used by the UI are fine."""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Code point ranges, built from numbers so this file never contains the characters it rejects.
RANGES = [
    (0x1F000, 0x1FAFF),  # pictographs, emoticons, transport, symbols and supplemental symbols
    (0x2700, 0x27BF),  # dingbats
    (0x2600, 0x26FF),  # miscellaneous symbols
    (0xFE0F, 0xFE0F),  # emoji presentation selector
]
EMOJI = re.compile("[" + "".join(f"{chr(lo)}-{chr(hi)}" for lo, hi in RANGES) + "]")


def main(paths: list[str]) -> int:
    """Report every line containing emoji; return 1 if any were found."""
    found = 0
    for name in paths:
        try:
            text = Path(name).read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            if EMOJI.search(line):
                sys.stdout.write(f"{name}:{lineno}: emoji: {line.strip()[:100]}\n")
                found += 1
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
