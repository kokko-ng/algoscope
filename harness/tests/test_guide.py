"""Every Python sample in the guides under docs/ runs, and its assertions hold."""

import re
from pathlib import Path

import pytest

DOCS = Path(__file__).resolve().parents[2] / "docs"
BLOCK = re.compile(r"^```python\n(.*?)^```$", re.DOTALL | re.MULTILINE)
GUIDES = sorted(DOCS.glob("*-guide.md"))
SAMPLES = [(guide, source) for guide in GUIDES for source in BLOCK.findall(guide.read_text(encoding="utf-8"))]


def test_every_guide_has_samples():
    assert GUIDES
    for guide in GUIDES:
        assert any(g == guide for g, _ in SAMPLES), f"{guide.name} has no Python samples"


@pytest.mark.parametrize(("guide", "source"), SAMPLES, ids=[f"{g.stem}-{i + 1}" for i, (g, _) in enumerate(SAMPLES)])
def test_sample_runs(guide, source):
    # each sample is self-contained: it defines what it needs and asserts its own results
    exec(compile(source, str(guide), "exec"), {"__name__": "guide_sample"})  # noqa: S102
