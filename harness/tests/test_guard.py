"""The guard stops solutions from reaching outside their exercise folder."""

import json
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parent.parent / "harness.py"
CASES = (
    "def visual():\n    return ([3, 1, 2],)\n\n"
    "def cases(n, rng):\n    return [([rng.randint(0, 9) for _ in range(n)],)]\n"
)
OUTSIDE = Path("/tmp/algoscope-guard-test")  # noqa: S108 - the path the guard must refuse to write
REFERENCE = "def solve(nums):\n    return max(nums) if nums else None\n"


def run(tmp_path, body, mode="visual"):
    (tmp_path / "solution.py").write_text(textwrap.dedent(body))
    (tmp_path / "reference.py").write_text(REFERENCE)
    (tmp_path / "cases.py").write_text(CASES)
    (tmp_path / "config.json").write_text(json.dumps({"kind": "function", "entry": "solve", "sizes": [5, 10]}))
    subprocess.run([sys.executable, "-I", str(HARNESS), str(tmp_path), mode], check=True, timeout=60)
    return json.loads((tmp_path / "out.json").read_text())


BLOCKED = {
    "subprocess": "import subprocess\n\ndef solve(nums):\n    subprocess.run(['echo', 'hi'], check=False)\n",
    "os.system": "import os\n\ndef solve(nums):\n    os.system('echo hi')\n",
    "socket": ("import socket\n\ndef solve(nums):\n    socket.create_connection(('127.0.0.1', 9), timeout=1)\n"),
    "write outside": f"def solve(nums):\n    open('{OUTSIDE}', 'w').write('x')\n",
    "delete outside": "import os\n\ndef solve(nums):\n    os.remove('/tmp/algoscope-guard-missing')\n",
    "ctypes": "import ctypes\n\ndef solve(nums):\n    ctypes.CDLL(None)\n",
}


@pytest.mark.parametrize("mode", ["visual", "score"])
@pytest.mark.parametrize("name", sorted(BLOCKED))
def test_blocked_actions_are_reported(tmp_path, name, mode):
    out = run(tmp_path, BLOCKED[name], mode)
    assert "solutions cannot" in out["error"]["text"], out["error"]
    assert not OUTSIDE.exists()


def test_writing_inside_the_exercise_folder_is_allowed(tmp_path):
    body = (
        "def solve(nums):\n    with open('scratch.txt', 'w') as fh:\n        fh.write('ok')\n"
        "    return max(nums) if nums else None\n"
    )
    out = run(tmp_path, body, "score")
    assert out["passed"] == out["total"]


def test_reading_files_is_allowed(tmp_path):
    body = "def solve(nums):\n    open('cases.py').read()\n    return max(nums) if nums else None\n"
    out = run(tmp_path, body)
    assert out["passed"] is True


def test_environment_is_not_part_of_the_result(tmp_path):
    out = run(tmp_path, "import os\n\ndef solve(nums):\n    print(sorted(os.environ))\n    return max(nums)\n")
    assert out["passed"] is True
