"""List subclasses used as solution inputs.

TracedList records element reads and writes for the animation (visual mode).
CostList charges hidden linear work (`x in lst`, `insert(0, x)`, slices) to the
step counter so it cannot hide behind a single line (score mode).
"""

from __future__ import annotations

import math
import types

ACCESS: list = []  # (kind, name, index) tuples since the last trace event


class TracedList(list):
    __slots__ = ("_name",)

    def __init__(self, items=(), name="?"):
        super().__init__(items)
        self._name = name

    def __getitem__(self, i):
        if isinstance(i, int):
            ACCESS.append(("r", self._name, i if i >= 0 else len(self) + i))
        return super().__getitem__(i)

    def __setitem__(self, i, v):
        if isinstance(i, int):
            ACCESS.append(("w", self._name, i if i >= 0 else len(self) + i))
        super().__setitem__(i, v)

    def append(self, v):
        ACCESS.append(("w", self._name, len(self)))
        super().append(v)

    def insert(self, i, v):
        idx = max(0, min(len(self), i if i >= 0 else len(self) + i))
        ACCESS.append(("w", self._name, idx))
        super().insert(i, v)

    def pop(self, i=-1):
        ACCESS.append(("w", self._name, i if i >= 0 else len(self) + i))
        return super().pop(i)


def traced(value, name):
    """Wrap lists (and lists of lists) so element access is recorded."""
    if type(value) is list:
        return TracedList(
            [traced(x, f"{name}[{i}]") if type(x) is list else x for i, x in enumerate(value)],
            name,
        )
    return value


class Meter:
    """Shared step counter that the line tracer and CostList both charge."""

    def __init__(self, limit):
        self.steps = 0
        self.limit = limit

    def charge(self, n):
        self.steps += n
        if self.steps > self.limit:
            raise StepLimit()


class StepLimit(BaseException):
    """Raised when a run exceeds its step budget. BaseException so user code cannot swallow it."""


METER: Meter | None = None


def _charge(n):
    if METER is not None and n > 0:
        METER.charge(n)


class CostList(list):
    __slots__ = ()

    def __contains__(self, v):
        _charge(len(self))
        return super().__contains__(v)

    def index(self, *a):
        _charge(len(self))
        return super().index(*a)

    def count(self, v):
        _charge(len(self))
        return super().count(v)

    def remove(self, v):
        _charge(len(self))
        super().remove(v)

    def insert(self, i, v):
        _charge(len(self) - max(0, min(len(self), i if i >= 0 else len(self) + i)))
        super().insert(i, v)

    def pop(self, i=-1):
        if i != -1:
            _charge(len(self) - (i if i >= 0 else len(self) + i))
        return super().pop(i)

    def __getitem__(self, i):
        if isinstance(i, slice):
            out = super().__getitem__(i)
            _charge(len(out))
            return CostList(out)
        return super().__getitem__(i)

    def __add__(self, other):
        out = CostList(list.__add__(self, other))
        _charge(len(out))
        return out

    def __mul__(self, k):
        out = CostList(list.__mul__(self, k))
        _charge(len(out))
        return out

    __rmul__ = __mul__

    def extend(self, items):
        items = list(items)
        _charge(len(items))
        super().extend(items)

    def sort(self, *a, **kw):
        _charge(nlogn(len(self)))
        super().sort(*a, **kw)

    def copy(self):
        _charge(len(self))
        return CostList(self)


def nlogn(n):
    return n * max(1, math.ceil(math.log2(n))) if n > 1 else n


def log_cost(n):
    return max(1, math.ceil(math.log2(n + 1)))


def costed(value):
    if type(value) is list:
        return CostList(costed(x) if type(x) is list else x for x in value)
    return value


# ---- score mode: charging for builtins and library calls ---------------------


def cost_list(items=()):
    """Stands in for list displays, comprehensions and list() calls in profiled code."""
    out = CostList(items)
    _charge(len(out))
    return out


def _sized(args):
    return len(args) == 1 and hasattr(args[0], "__len__")


def c_sorted(items, *a, **kw):
    out = sorted(items, *a, **kw)
    _charge(nlogn(len(out)))
    return CostList(out)


def _linear(fn):
    def wrapped(*a, **kw):
        if _sized(a):
            _charge(len(a[0]))
        return fn(*a, **kw)

    wrapped.__name__ = fn.__name__
    return wrapped


BUILTINS = {
    "sorted": c_sorted,
    "min": _linear(min),
    "max": _linear(max),
    "sum": _linear(sum),
    "__cost_list__": cost_list,
}


def costed_heapq():
    """A heapq look-alike that charges log n per push or pop and n for heapify."""
    import heapq as real

    mod = types.ModuleType("heapq")

    def heappush(h, x):
        _charge(log_cost(len(h)))
        real.heappush(h, x)

    def heappop(h):
        _charge(log_cost(len(h)))
        return real.heappop(h)

    def heappushpop(h, x):
        _charge(log_cost(len(h)))
        return real.heappushpop(h, x)

    def heapreplace(h, x):
        _charge(log_cost(len(h)))
        return real.heapreplace(h, x)

    def heapify(h):
        _charge(len(h))
        real.heapify(h)

    def nlargest(k, items, key=None):
        items = list(items)
        _charge(len(items) * log_cost(k))
        return CostList(real.nlargest(k, items, key=key))

    def nsmallest(k, items, key=None):
        items = list(items)
        _charge(len(items) * log_cost(k))
        return CostList(real.nsmallest(k, items, key=key))

    def merge(*iterables, key=None, reverse=False):
        for x in real.merge(*iterables, key=key, reverse=reverse):
            _charge(log_cost(len(iterables)))
            yield x

    for f in (heappush, heappop, heappushpop, heapreplace, heapify, nlargest, nsmallest, merge):
        setattr(mod, f.__name__, f)
    return mod


def costed_bisect():
    import bisect as real

    mod = types.ModuleType("bisect")
    for name in ("bisect_left", "bisect_right", "bisect", "insort_left", "insort_right", "insort"):
        fn = getattr(real, name)

        def wrapped(a, x, *rest, _fn=fn, _insert=name.startswith("insort"), **kw):
            _charge(log_cost(len(a)) + (len(a) if _insert else 0))
            return _fn(a, x, *rest, **kw)

        setattr(mod, name, wrapped)
    return mod
