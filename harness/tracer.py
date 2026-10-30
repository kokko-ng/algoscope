"""Line tracers: a recorder that snapshots state for the animation and a step counter for scoring."""

from __future__ import annotations

import math
import sys
import types
from collections import deque

import traced

MAX_ITEMS = 64
MAX_OBJECTS = 300
MAX_STR = 80


class TraceLimit(BaseException):
    """Raised when the visual trace reaches its frame cap."""


class Encoder:
    """Encodes Python values into tagged JSON. Objects get stable small ids across frames."""

    def __init__(self):
        self.ids: dict[int, int] = {}
        self.keep: list = []  # keeps objects alive so id() values are not reused

    def oid(self, obj):
        key = id(obj)
        if key not in self.ids:
            self.ids[key] = len(self.ids) + 1
            self.keep.append(obj)
        return self.ids[key]

    def encode(self, v, heap, depth=0):
        if v is None or isinstance(v, bool):
            return v
        if isinstance(v, int):
            return v if abs(v) < 2**53 else {"k": "num", "v": str(v)}
        if isinstance(v, float):
            if math.isfinite(v):
                return v
            return {"k": "num", "v": repr(v)}
        if isinstance(v, str):
            return v if len(v) <= MAX_STR else v[:MAX_STR] + "..."
        if depth > 12:
            return {"k": "repr", "v": "..."}
        if isinstance(v, (list, tuple, deque)):
            kind = "list" if isinstance(v, list) else "tuple" if isinstance(v, tuple) else "deque"
            items = [self.encode(x, heap, depth + 1) for x in list(v)[:MAX_ITEMS]]
            return {"k": kind, "items": items, "len": len(v)}
        if isinstance(v, dict):
            items = []
            for i, (key, val) in enumerate(v.items()):
                if i >= MAX_ITEMS:
                    break
                items.append([self.encode(key, heap, depth + 1), self.encode(val, heap, depth + 1)])
            return {"k": "dict", "items": items, "len": len(v)}
        if isinstance(v, (set, frozenset)):
            try:
                ordered = sorted(v)
            except TypeError:
                ordered = sorted(v, key=repr)
            items = [self.encode(x, heap, depth + 1) for x in ordered[:MAX_ITEMS]]
            return {"k": "set", "items": items, "len": len(v)}
        if isinstance(v, (types.FunctionType, types.BuiltinFunctionType, types.ModuleType, type, types.MethodType)):
            return {"k": "repr", "v": getattr(v, "__name__", "?")}
        fields = _fields(v)
        if fields is not None:
            ident = self.oid(v)
            key = str(ident)
            if key not in heap and len(heap) < MAX_OBJECTS:
                heap[key] = None  # placeholder breaks cycles
                heap[key] = {
                    "cls": type(v).__name__,
                    # objects are stored flat in the heap table, so their fields start a fresh depth
                    "fields": {name: self.encode(val, heap, 0) for name, val in fields},
                }
            return {"k": "ref", "id": ident}
        return {"k": "repr", "v": _short_repr(v)}


def _fields(v):
    d = getattr(v, "__dict__", None)
    if isinstance(d, dict):
        return [(k, val) for k, val in d.items() if not k.startswith("_")]
    slots = getattr(type(v), "__slots__", None)
    if slots and not isinstance(v, (list, dict, set)):
        names = [slots] if isinstance(slots, str) else list(slots)
        return [(n, getattr(v, n)) for n in names if hasattr(v, n) and not n.startswith("_")]
    return None


def _short_repr(v):
    try:
        r = repr(v)
    except Exception:
        r = f"<{type(v).__name__}>"
    return r if len(r) <= MAX_STR else r[:MAX_STR] + "..."


def short(v):
    """Compact text for call-stack argument display."""
    if v is None or isinstance(v, (bool, int, float)):
        return repr(v)
    if isinstance(v, str):
        return repr(v) if len(v) <= 12 else repr(v[:10]) + "..."
    if isinstance(v, (list, tuple)):
        return f"[{len(v)}]"
    if isinstance(v, dict):
        return f"{{{len(v)}}}"
    val = getattr(v, "val", None)
    if val is not None and isinstance(val, (int, float, str)):
        return f"<{val}>"
    return type(v).__name__


def _resolve(frames, dotted):
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

    def __init__(self, filename, watch, max_frames):
        self.filename = filename
        self.watch = watch
        self.max_frames = max_frames
        self.frames: list[dict] = []
        self.truncated = False
        self.enc = Encoder()
        self.op = None
        self.last_line = None

    def global_trace(self, frame, event, arg):
        if frame.f_code.co_filename != self.filename:
            return None
        return self.local_trace

    def local_trace(self, frame, event, arg):
        if event in ("line", "return"):
            self.record(frame, event, arg)
        return self.local_trace

    def solution_frames(self, frame):
        out = []
        f = frame
        while f is not None:
            if f.f_code.co_filename == self.filename:
                out.append(f)
            f = f.f_back
        return out

    def record(self, frame, event, arg):
        if len(self.frames) >= self.max_frames:
            self.truncated = True
            sys.settrace(None)
            raise TraceLimit()
        frames = self.solution_frames(frame)
        heap: dict = {}
        vars_out = {}
        for name in self.watch:
            found, value = _resolve(frames, name)
            if found:
                vars_out[name] = self.enc.encode(value, heap)
        local_scalars = {}
        for name, value in frame.f_locals.items():
            if name.startswith("_") or name in vars_out:
                continue
            if isinstance(value, SCALARS):
                local_scalars[name] = self.enc.encode(value, heap)
        stack = []
        for f in reversed(frames):
            code = f.f_code
            argnames = code.co_varnames[: code.co_argcount]
            args = ", ".join(f"{a}={short(f.f_locals.get(a))}" for a in argnames if a != "self")
            stack.append({"func": code.co_name, "args": args, "line": f.f_lineno})
        reads, writes = [], []
        for kind, name, idx in traced.ACCESS:
            (reads if kind == "r" else writes).append([name, idx])
        traced.ACCESS.clear()
        entry = {
            "ev": event,
            "line": frame.f_lineno,
            "prev": self.last_line,
            "vars": vars_out,
            "locals": local_scalars,
            "heap": heap,
            "stack": stack,
            "reads": reads[-16:],
            "writes": writes[-16:],
        }
        if self.op is not None:
            entry["op"] = self.op
        if event == "return":
            entry["ret"] = self.enc.encode(arg, heap)
        self.frames.append(entry)
        self.last_line = frame.f_lineno


class Counter:
    """Counts executed lines in the solution file and charges them to the shared meter."""

    def __init__(self, filename, meter):
        self.filename = filename
        self.meter = meter

    def global_trace(self, frame, event, arg):
        if frame.f_code.co_filename != self.filename:
            return None
        return self.local_trace

    def local_trace(self, frame, event, arg):
        if event == "line":
            self.meter.charge(1)
        return self.local_trace
