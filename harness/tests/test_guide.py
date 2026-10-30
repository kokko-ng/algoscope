"""Every Python sample in docs/dsa-guide.md runs, and its assertions hold."""

import re
from pathlib import Path

import pytest

GUIDE = Path(__file__).resolve().parents[2] / "docs" / "dsa-guide.md"
BLOCK = re.compile(r"^```python\n(.*?)^```$", re.DOTALL | re.MULTILINE)
SAMPLES = BLOCK.findall(GUIDE.read_text(encoding="utf-8"))


def test_guide_has_samples():
    assert len(SAMPLES) >= 30


@pytest.mark.parametrize("source", SAMPLES, ids=[f"sample-{i + 1}" for i in range(len(SAMPLES))])
def test_sample_runs(source):
    # each sample is self-contained: it defines what it needs and asserts its own results
    exec(compile(source, str(GUIDE), "exec"), {"__name__": "guide_sample"})  # noqa: S102
