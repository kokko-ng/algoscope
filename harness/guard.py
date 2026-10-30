"""A best-effort guard around solution code.

Solutions run in a throwaway process, in a temp folder. This module adds an audit hook that stops them
from starting processes, opening network connections, loading native code, and changing files outside
that folder, plus resource limits where the platform supports them. It is a guard against accidents
and casual misuse, not a security boundary: run untrusted content in a container.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import types

BLOCKED = {
    "subprocess.Popen": "start processes",
    "os.system": "start processes",
    "os.exec": "start processes",
    "os.posix_spawn": "start processes",
    "os.spawn": "start processes",
    "os.fork": "start processes",
    "os.forkpty": "start processes",
    "pty.spawn": "start processes",
    "socket.connect": "open network connections",
    "socket.bind": "open network connections",
    "socket.sendto": "open network connections",
    "ctypes.dlopen": "load native code",
    "webbrowser.open": "open a browser",
}

# events whose first argument is a path the solution wants to change
PATH_CHANGES = {
    "os.remove",
    "os.rename",
    "os.rmdir",
    "os.mkdir",
    "os.chmod",
    "os.chown",
    "os.truncate",
    "os.link",
    "os.symlink",
    "os.utime",
    "shutil.rmtree",
    "shutil.copyfile",
    "shutil.move",
}

WRITE_FLAGS = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_APPEND | os.O_TRUNC

CPU_SECONDS = 120
MAX_FILE_BYTES = 64 * 1024 * 1024
MAX_MEMORY_BYTES = 2 * 1024 * 1024 * 1024


class GuardError(PermissionError):
    """Raised inside solution code when it tries something the guard blocks."""


def _inside(path: object, root: Path) -> bool:
    if isinstance(path, int):
        return True  # an already open file descriptor
    if isinstance(path, bytes):
        path = os.fsdecode(path)
    try:
        target = Path(str(path))
        if not target.is_absolute():
            target = Path.cwd() / target
        return target.resolve().is_relative_to(root)
    except (OSError, ValueError):
        return False


def _writes(mode: object, flags: object) -> bool:
    if isinstance(mode, str) and any(c in mode for c in "wax+"):
        return True
    return isinstance(flags, int) and bool(flags & WRITE_FLAGS)


def violation(event: str, args: tuple[object, ...], root: Path) -> str | None:
    """What an audit event would do that the guard forbids, or None if it is allowed."""
    if event in BLOCKED:
        return BLOCKED[event]
    if event == "open" and args:
        # the open event's arguments are (path, mode, flags)
        _, mode, flags = (*args, None, None)[:3]
        if _writes(mode, flags) and not _inside(args[0], root):
            return "write files outside the exercise folder"
    if event in PATH_CHANGES:
        paths = [a for a in args[:2] if isinstance(a, (str, bytes, os.PathLike))]
        if not all(_inside(p, root) for p in paths):
            return "change files outside the exercise folder"
    return None


def install(run_dir: Path) -> None:
    """Install the audit hook and resource limits for the rest of this process."""
    root = run_dir.resolve()
    sys.dont_write_bytecode = True

    def hook(event: str, args: tuple[object, ...]) -> None:
        what = violation(event, args, root)
        if what is not None:
            msg = f"solutions cannot {what} ({event})"
            raise GuardError(msg)

    sys.addaudithook(hook)
    _limit_resources()


def _limit_resources() -> None:
    try:
        import resource  # noqa: PLC0415 - Unix only
    except ImportError:
        return
    limits = [(resource.RLIMIT_CPU, CPU_SECONDS), (resource.RLIMIT_FSIZE, MAX_FILE_BYTES)]
    if sys.platform.startswith("linux"):
        # macOS does not enforce address-space limits reliably
        limits.append((resource.RLIMIT_AS, MAX_MEMORY_BYTES))
    for kind, value in limits:
        _set_limit(resource, kind, value)


def _set_limit(resource: types.ModuleType, kind: int, value: int) -> None:
    try:
        _, hard = resource.getrlimit(kind)
        ceiling = value if hard == resource.RLIM_INFINITY else min(value, hard)
        resource.setrlimit(kind, (ceiling, hard))
    except (ValueError, OSError):
        return
