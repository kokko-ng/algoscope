"""Tests for the tracing harness: run it the way the Rust runner does, through a run directory."""

import json
import os
import subprocess
import sys
import textwrap

import pytest

HARNESS = os.path.join(os.path.dirname(__file__), "..", "harness.py")

CASES = """
def visual():
    return ([5, 1, 4, 2],)

def fixed():
    return [([],), ([1],)]

def cases(n, rng):
    return [([rng.randint(0, 99) for _ in range(n)],)]
"""

REFERENCE = """
def solve(nums):
    best = None
    for x in nums:
        if best is None or x > best:
            best = x
    return best
"""


def run(tmp_path, solution, mode, cases=CASES, reference=REFERENCE, **cfg):
    (tmp_path / "solution.py").write_text(textwrap.dedent(solution))
    (tmp_path / "reference.py").write_text(textwrap.dedent(reference))
    (tmp_path / "cases.py").write_text(textwrap.dedent(cases))
    config = {"kind": "function", "entry": "solve", "watch": ["nums", "i"], "sizes": [20, 40, 80], "max_frames": 500}
    config.update(cfg)
    (tmp_path / "config.json").write_text(json.dumps(config))
    subprocess.run([sys.executable, "-I", HARNESS, str(tmp_path), mode], check=True, timeout=60)
    return json.loads((tmp_path / "out.json").read_text())


def test_visual_records_frames_reads_and_writes(tmp_path):
    out = run(
        tmp_path,
        """
        def solve(nums):
            for i in range(len(nums) - 1):
                if nums[i] > nums[i + 1]:
                    nums[i], nums[i + 1] = nums[i + 1], nums[i]
            return nums[-1]
        """,
        "visual",
    )
    assert out["passed"] is True
    frames = out["frames"]
    assert frames, "no frames"
    assert all("line" in f and "vars" in f for f in frames)
    assert any(f["reads"] for f in frames)
    assert any(f["writes"] for f in frames)
    assert any(f["vars"].get("i") == 1 for f in frames)
    assert frames[-1]["ev"] == "return"


def test_step_counts_are_deterministic_and_grow(tmp_path):
    a = run(tmp_path, REFERENCE, "score")
    b = run(tmp_path, REFERENCE, "score")
    assert a["passed"] == a["total"] > 0
    assert a["steps"] == b["steps"]
    user = [s for _, s in a["steps"]["user"]]
    assert user[0] < user[1] < user[2]


def test_hidden_linear_work_is_charged(tmp_path):
    quadratic = """
    def solve(nums):
        best = None
        for x in nums:
            if x in nums and (best is None or x > best):
                best = x
        return best
    """
    out = run(tmp_path, quadratic, "score")
    ref = dict(map(tuple, out["steps"]["ref"]))
    user = dict(map(tuple, out["steps"]["user"]))
    assert user[80] > 10 * ref[80]


def test_failures_and_errors_are_reported(tmp_path):
    out = run(tmp_path, "def solve(nums):\n    return 0\n", "score")
    assert out["passed"] < out["total"]
    assert out["failures"]
    out = run(tmp_path, "def solve(nums):\n    return nums[10]\n", "score")
    assert "IndexError" in out["error"]["text"]
    assert out["error"]["line"] == 2
    out = run(tmp_path, "def solve(nums)\n    return 0\n", "visual")
    assert out["error"]["text"].startswith("SyntaxError")


def test_forbidden_names_are_rejected_but_self_methods_are_not(tmp_path):
    out = run(tmp_path, "def solve(nums):\n    return max(sorted(nums), default=None)\n", "score", forbid=["sorted"])
    assert "sorted" in out["error"]["text"]
    cls_cases = "def visual():\n    return [('add', 1), ('add', 2)]\n\ndef cases(n, rng):\n    return [[('add', i) for i in range(n)]]\n"
    cls = """
    class Box:
        def __init__(self):
            self.items = [None] * 64
            self.size = 0
        def add(self, x):
            self.append(x)
            return self.size
        def append(self, x):
            self.items[self.size] = x
            self.size += 1
    """
    out = run(tmp_path, cls, "score", cases=cls_cases, reference=cls, kind="class", entry="Box", forbid=["append"], sizes=[8, 16, 32])
    assert "error" not in out, out.get("error")
    assert out["passed"] == out["total"]


def test_infinite_loop_is_cut_off_in_visual_mode(tmp_path):
    out = run(tmp_path, "def solve(nums):\n    i = 0\n    while True:\n        i += 1\n", "visual", max_frames=200)
    assert out["truncated"] is True
    assert len(out["frames"]) == 200


def test_step_limit_stops_runaway_profiling(tmp_path):
    slow = """
    def solve(nums):
        total = 0
        for a in nums:
            for b in nums:
                for c in nums:
                    total += 1
        return max(nums) if nums else None
    """
    out = run(tmp_path, slow, "score", step_limit=20000)
    assert out.get("step_limit_hit") is not None


def test_user_output_is_captured(tmp_path):
    out = run(tmp_path, "def solve(nums):\n    print('hello')\n    return max(nums) if nums else None\n", "visual")
    assert "hello" in out["stdout"]


@pytest.mark.parametrize("value,kind", [([1, 2], "list"), ((1, 2), "tuple"), ({1: 2}, "dict"), ({3}, "set")])
def test_encoder_tags(value, kind):
    sys.path.insert(0, os.path.dirname(HARNESS))
    import tracer

    enc = tracer.Encoder().encode(value, {})
    assert enc["k"] == kind


def test_infinite_loop_in_suite_is_reported_quickly(tmp_path):
    import time

    start = time.monotonic()
    out = run(tmp_path, "def solve(nums):\n    while True:\n        pass\n", "score", case_step_limit=50000)
    assert "infinite loop" in out["error"]["text"]
    assert time.monotonic() - start < 10
