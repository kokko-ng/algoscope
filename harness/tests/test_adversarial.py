"""Solutions that misbehave must produce a clean result, never crash the harness or hang it."""

import json
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parent.parent / "harness.py"

CASES = """
def visual():
    return ([5, 1, 4, 2],)

def cases(n, rng):
    return [([rng.randint(0, 99) for _ in range(n)],)]
"""

REFERENCE = "def solve(nums):\n    return max(nums) if nums else None\n"


def run(tmp_path, solution, mode, timeout=60, **cfg: object):
    (tmp_path / "solution.py").write_text(textwrap.dedent(solution))
    (tmp_path / "reference.py").write_text(REFERENCE)
    (tmp_path / "cases.py").write_text(textwrap.dedent(CASES))
    config = {"kind": "function", "entry": "solve", "watch": ["nums"], "sizes": [10, 20], "max_frames": 300}
    config.update(cfg)
    (tmp_path / "config.json").write_text(json.dumps(config))
    proc = subprocess.run(
        [sys.executable, "-I", str(HARNESS), str(tmp_path), mode],
        timeout=timeout,
        check=False,
        stdin=subprocess.DEVNULL,
        capture_output=True,
    )
    out = tmp_path / "out.json"
    return proc, (json.loads(out.read_text()) if out.exists() else None)


BOTH = pytest.mark.parametrize("mode", ["visual", "score"])


@BOTH
def test_sys_exit_is_reported(tmp_path, mode):
    _, out = run(tmp_path, "import sys\n\ndef solve(nums):\n    sys.exit(3)\n", mode)
    assert out is not None
    assert "SystemExit" in out["error"]["text"]


@BOTH
def test_keyboard_interrupt_is_reported(tmp_path, mode):
    _, out = run(tmp_path, "def solve(nums):\n    raise KeyboardInterrupt\n", mode)
    assert out is not None
    assert "KeyboardInterrupt" in out["error"]["text"]


@BOTH
def test_hard_exit_leaves_no_result_but_does_not_hang(tmp_path, mode):
    proc, out = run(tmp_path, "import os\n\ndef solve(nums):\n    os._exit(7)\n", mode)
    assert out is None
    assert proc.returncode == 7


@BOTH
def test_output_flood_is_capped(tmp_path, mode):
    flood = (
        "def solve(nums):\n    for _ in range(200000):\n        print('x' * 50)\n"
        "    return max(nums) if nums else None\n"
    )
    _, out = run(tmp_path, flood, mode, step_limit=10**9, case_step_limit=10**9)
    assert out is not None
    assert len(out["stdout"]) <= 4100


@BOTH
def test_reading_stdin_fails_cleanly(tmp_path, mode):
    _, out = run(tmp_path, "def solve(nums):\n    return int(input())\n", mode)
    assert out is not None
    assert "EOFError" in out["error"]["text"]


def test_stderr_writes_do_not_break_results(tmp_path):
    code = (
        "import sys\n\ndef solve(nums):\n    sys.stderr.write('noise\\n' * 1000)\n"
        "    return max(nums) if nums else None\n"
    )
    _, out = run(tmp_path, code, "score")
    assert out["passed"] == out["total"]


@BOTH
def test_unserialisable_return_value(tmp_path, mode):
    _, out = run(tmp_path, "def solve(nums):\n    return (x for x in nums)\n", mode)
    assert out is not None
    json.dumps(out)  # the result itself is valid JSON
    assert out.get("passed") in (False, 0, None)


@BOTH
def test_unbounded_recursion(tmp_path, mode):
    _, out = run(tmp_path, "def solve(nums):\n    return solve(nums)\n", mode, max_frames=2500, timeout=30)
    assert out is not None
    assert "error" in out or out.get("truncated")


def test_mutating_the_input_does_not_corrupt_the_expected_answer(tmp_path):
    code = "def solve(nums):\n    best = max(nums) if nums else None\n    nums.clear()\n    return best\n"
    _, out = run(tmp_path, code, "score")
    assert out["passed"] == out["total"]


@BOTH
def test_missing_entry_point(tmp_path, mode):
    _, out = run(tmp_path, "def answer(nums):\n    return 0\n", mode)
    assert "does not define the function `solve`" in out["error"]["text"]


@BOTH
def test_import_error_at_module_level(tmp_path, mode):
    _, out = run(tmp_path, "import not_a_real_module\n\ndef solve(nums):\n    return 0\n", mode)
    assert "ModuleNotFoundError" in out["error"]["text"]


@BOTH
def test_print_at_import_time_is_captured(tmp_path, mode):
    code = "print('loading')\n\ndef solve(nums):\n    return max(nums) if nums else None\n"
    _, out = run(tmp_path, code, mode)
    assert out is not None
    assert "error" not in out


def test_tampering_with_the_tracer_cannot_fake_steps(tmp_path):
    code = (
        "import sys\n\ndef solve(nums):\n    sys.settrace(None)\n    best = None\n"
        "    for x in nums:\n        for y in nums:\n            if best is None or x > best:\n"
        "                best = x\n    return best\n"
    )
    _, out = run(tmp_path, code, "score", sizes=[10, 20, 40])
    assert out["passed"] == out["total"]
    # turning tracing off hides line steps; the run must still be measured, not crash
    assert "steps" in out


def test_non_utf8_output_does_not_break_the_result(tmp_path):
    code = "def solve(nums):\n    print('\\udcff')\n    return max(nums) if nums else None\n"
    _, out = run(tmp_path, code, "visual")
    assert out is not None


def test_exit_during_profiling_is_reported(tmp_path):
    code = (
        "import sys\n\ndef solve(nums):\n    if len(nums) > 15:\n        sys.exit(1)\n"
        "    return max(nums) if nums else None\n"
    )
    _, out = run(tmp_path, code, "score", check_sizes=[0, 1, 5], sizes=[10, 20])
    assert out["passed"] == out["total"]
    assert "while profiling at n=20" in out["error"]["text"]
    assert "steps" not in out


def test_deep_recursion_trace_is_fast(tmp_path):
    import time

    code = (
        "def solve(nums, depth=0):\n    if depth < 400:\n        return solve(nums, depth + 1)\n    return max(nums)\n"
    )
    start = time.monotonic()
    _, out = run(tmp_path, code, "visual", max_frames=2500)
    assert out["passed"] is True
    assert time.monotonic() - start < 15
    assert max(len(f["stack"]) for f in out["frames"]) <= 40
