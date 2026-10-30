"""List subclasses used as solution inputs.

TracedList records element reads and writes for the animation (visual mode).
CostList charges hidden linear work (`x in lst`, `insert(0, x)`, slices) to the
step counter so it cannot hide behind a single line (score mode).
"""

from __future__ import annotations

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
            _charge(len(range(*i.indices(len(self)))))
        return super().__getitem__(i)

    def copy(self):
        _charge(len(self))
        return list(self)


def costed(value):
    if type(value) is list:
        return CostList(costed(x) if type(x) is list else x for x in value)
    return value
