"""Line tracers: a recorder that snapshots state for the animation and a step counter for scoring."""

from __future__ import annotations

import math
import sys
import types
from collections import deque
from typing import Any

import traced

MAX_ITEMS = 64
MAX_OBJECTS = 300
MAX_STR = 80
MAX_DEPTH = 12
MAX_ACCESSES = 16
MAX_STACK = 40
SHORT_STR = 12
SAFE_INT = 2**53

Json = Any
"""A JSON-serialisable value."""

Heap = dict[str, Any]
"""Objects seen in one frame, keyed by their small id."""

TraceFn = Any
"""What sys.settrace accepts: a trace function or None."""


class TraceLimitError(BaseException):
    """Raised when the visual trace reaches its frame cap."""


def _clip(s: str) -> str:
    return s if len(s) <= MAX_STR else s[:MAX_STR] + "..."


def _short_repr(v: object) -> str:
    try:
        r = repr(v)
    except Exception:  # noqa: BLE001 - a broken __repr__ in user code must not break the trace
        r = f"<{type(v).__name__}>"
    return _clip(r)


def _fields(v: object) -> list[tuple[str, Any]] | None:
    """Public attributes of an object, or None when it is not a plain object."""
    d = getattr(v, "__dict__", None)
    if isinstance(d, dict):
        return [(k, val) for k, val in d.items() if not k.startswith("_")]
    slots = getattr(type(v), "__slots__", None)
    if slots and not isinstance(v, (list, dict, set)):
        names = [slots] if isinstance(slots, str) else list(slots)
        return [(n, getattr(v, n)) for n in names if hasattr(v, n) and not n.startswith("_")]
    return None


def _sorted_items(v: set[Any] | frozenset[Any]) -> list[Any]:
    try:
        return sorted(v)
    except TypeError:
        return sorted(v, key=repr)


class Encoder:
    """Encodes Python values into tagged JSON. Objects get stable small ids across frames."""

    def __init__(self) -> None:
        """Start with no objects seen."""
        self.ids: dict[int, int] = {}
        self.keep: list[object] = []  # keeps objects alive so id() values are not reused

    def oid(self, obj: object) -> int:
        """Return the small stable id for an object."""
        key = id(obj)
        if key not in self.ids:
            self.ids[key] = len(self.ids) + 1
            self.keep.append(obj)
        return self.ids[key]

    def encode(self, v: object, heap: Heap, depth: int = 0) -> Json:
        """Encode one value; objects are added to `heap` and referenced by id."""
        scalar = self._scalar(v)
        if scalar is not NotImplemented:
            return scalar
        if depth > MAX_DEPTH:
            return {"k": "repr", "v": "..."}
        container = self._container(v, heap, depth)
        if container is not None:
            return container
        if isinstance(v, (types.FunctionType, types.BuiltinFunctionType, types.ModuleType, type, types.MethodType)):
            return {"k": "repr", "v": getattr(v, "__name__", "?")}
        fields = _fields(v)
        if fields is None:
            return {"k": "repr", "v": _short_repr(v)}
        ident = self.oid(v)
        key = str(ident)
        if key not in heap and len(heap) < MAX_OBJECTS:
            heap[key] = None  # placeholder breaks cycles
            # objects are stored flat in the heap table, so their fields start a fresh depth
            heap[key] = {"cls": type(v).__name__, "fields": {name: self.encode(val, heap) for name, val in fields}}
        return {"k": "ref", "id": ident}

    @staticmethod
    def _scalar(v: object) -> Json:
        if v is None or isinstance(v, (bool, str)):
            return _clip(v) if isinstance(v, str) else v
        if isinstance(v, int):
            return v if abs(v) < SAFE_INT else {"k": "num", "v": str(v)}
        if isinstance(v, float):
            return v if math.isfinite(v) else {"k": "num", "v": repr(v)}
        return NotImplemented

    def _container(self, v: object, heap: Heap, depth: int) -> Json | None:
        if isinstance(v, (list, tuple, deque)):
            kind = "list" if isinstance(v, list) else "tuple" if isinstance(v, tuple) else "deque"
            items = [self.encode(x, heap, depth + 1) for x in list(v)[:MAX_ITEMS]]
            return {"k": kind, "items": items, "len": len(v)}
        if isinstance(v, dict):
            pairs = list(v.items())[:MAX_ITEMS]
            items = [[self.encode(key, heap, depth + 1), self.encode(val, heap, depth + 1)] for key, val in pairs]
            return {"k": "dict", "items": items, "len": len(v)}
        if isinstance(v, (set, frozenset)):
            items = [self.encode(x, heap, depth + 1) for x in _sorted_items(v)[:MAX_ITEMS]]
            return {"k": "set", "items": items, "len": len(v)}
        return None


def short(v: object) -> str:
    """Compact text for call-stack argument display."""
    if v is None or isinstance(v, (bool, int, float)):
        return repr(v)
    if isinstance(v, str):
        return repr(v) if len(v) <= SHORT_STR else repr(v[: SHORT_STR - 2]) + "..."
    if isinstance(v, (list, tuple)):
        return f"[{len(v)}]"
    if isinstance(v, dict):
        return f"{{{len(v)}}}"
    val = getattr(v, "val", None)
    if val is not None and isinstance(val, (int, float, str)):
        return f"<{val}>"
    return type(v).__name__


def _resolve(frames: list[types.FrameType], dotted: str) -> tuple[bool, Any]:
    """Find a dotted name (e.g. 'self.data') in the innermost frame that defines its base."""
    base, *rest = dotted.split(".")
    for frame in frames:
        loc = frame.f_locals
        if base in loc:
            value = loc[base]
            try:
                for attr in rest:
                    value = getattr(value, attr)
            except AttributeError:
                return False, None
            return True, value
    return False, None


SCALARS = (int, float, str, bool, type(None))


class Recorder:
    """Records one frame per executed line in the solution file."""

    def __init__(self, filename: str, watch: list[str], max_frames: int) -> None:
        """Record lines of `filename`, snapshotting the `watch` names, up to `max_frames` frames."""
        self.filename = filename
        self.watch = watch
        self.max_frames = max_frames
        self.frames: list[dict[str, Json]] = []
        self.truncated = False
        self.enc = Encoder()
        self.op: str | None = None
        self.last_line: int | None = None

    def global_trace(self, frame: types.FrameType, _event: str, _arg: object) -> TraceFn:
        """Trace only frames from the solution file."""
        if frame.f_code.co_filename != self.filename:
            return None
        return self.local_trace

    def local_trace(self, frame: types.FrameType, event: str, arg: object) -> TraceFn:
        """Record line and return events."""
        if event in {"line", "return"}:
            self.record(frame, event, arg)
        return self.local_trace

    def solution_frames(self, frame: types.FrameType) -> list[types.FrameType]:
        """Solution frames from innermost to outermost."""
        out = []
        f: types.FrameType | None = frame
        while f is not None:
            if f.f_code.co_filename == self.filename:
                out.append(f)
            f = f.f_back
        return out

    def _watched(self, frames: list[types.FrameType], heap: Heap) -> dict[str, Json]:
        out = {}
        for name in self.watch:
            found, value = _resolve(frames, name)
            if found:
                out[name] = self.enc.encode(value, heap)
        return out

    def _scalars(self, frame: types.FrameType, skip: dict[str, Json], heap: Heap) -> dict[str, Json]:
        return {
            name: self.enc.encode(value, heap)
            for name, value in frame.f_locals.items()
            if not name.startswith("_") and name not in skip and isinstance(value, SCALARS)
        }

    @staticmethod
    def _stack(frames: list[types.FrameType]) -> list[dict[str, Json]]:
        stack = []
        # the innermost frames are the interesting ones; deep recursion must not make each frame O(depth)
        for f in reversed(frames[:MAX_STACK]):
            code = f.f_code
            argnames = code.co_varnames[: code.co_argcount]
            args = ", ".join(f"{a}={short(f.f_locals.get(a))}" for a in argnames if a != "self")
            stack.append({"func": code.co_name, "args": args, "line": f.f_lineno})
        return stack

    def record(self, frame: types.FrameType, event: str, arg: object) -> None:
        """Snapshot the watched state as one frame."""
        if len(self.frames) >= self.max_frames:
            self.truncated = True
            sys.settrace(None)
            raise TraceLimitError
        frames = self.solution_frames(frame)
        heap: Heap = {}
        vars_out = self._watched(frames, heap)
        reads = [[name, idx] for kind, name, idx in traced.ACCESS if kind == "r"]
        writes = [[name, idx] for kind, name, idx in traced.ACCESS if kind == "w"]
        traced.ACCESS.clear()
        entry: dict[str, Json] = {
            "ev": event,
            "line": frame.f_lineno,
            "prev": self.last_line,
            "vars": vars_out,
            "locals": self._scalars(frame, vars_out, heap),
            "heap": heap,
            "stack": self._stack(frames),
            "reads": reads[-MAX_ACCESSES:],
            "writes": writes[-MAX_ACCESSES:],
        }
        if self.op is not None:
            entry["op"] = self.op
        if event == "return":
            entry["ret"] = self.enc.encode(arg, heap)
        self.frames.append(entry)
        self.last_line = frame.f_lineno


class Counter:
    """Counts executed lines in the solution file and charges them to the shared meter."""

    def __init__(self, filename: str, meter: traced.Meter) -> None:
        """Count lines of `filename` against `meter`."""
        self.filename = filename
        self.meter = meter

    def global_trace(self, frame: types.FrameType, _event: str, _arg: object) -> TraceFn:
        """Trace only frames from the solution file."""
        if frame.f_code.co_filename != self.filename:
            return None
        return self.local_trace

    def local_trace(self, _frame: types.FrameType, event: str, _arg: object) -> TraceFn:
        """Charge one step per executed line."""
        if event == "line":
            self.meter.charge(1)
        return self.local_trace
