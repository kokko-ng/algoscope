"""List subclasses and cost accounting used while running solutions.

TracedList records element reads and writes for the animation (visual mode).
CostList charges hidden linear work (`x in lst`, `insert(0, x)`, slices) to the
step counter so it cannot hide behind a single line (score mode).
"""

from __future__ import annotations

import bisect as real_bisect
import heapq as real_heapq
import math
import operator
import types
from typing import TYPE_CHECKING, Any, SupportsIndex, overload

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Iterator

ACCESS: list[tuple[str, str, int]] = []
"""(kind, list name, index) tuples recorded since the last trace event; kind is "r" or "w"."""


def _absolute(i: SupportsIndex, length: int) -> int:
    i = operator.index(i)
    return i if i >= 0 else length + i


class TracedList(list[Any]):
    """A list that records which indices are read and written, for the animation."""

    __slots__ = ("_name",)

    def __init__(self, items: Iterable[Any] = (), name: str = "?") -> None:
        """Create a traced list labelled with the variable name it is shown under."""
        super().__init__(items)
        self._name = name

    @overload
    def __getitem__(self, i: SupportsIndex) -> Any: ...
    @overload
    def __getitem__(self, i: slice) -> list[Any]: ...
    def __getitem__(self, i: SupportsIndex | slice) -> Any:
        """Record a read of a single index."""
        if not isinstance(i, slice):
            ACCESS.append(("r", self._name, _absolute(i, len(self))))
        return super().__getitem__(i)

    @overload
    def __setitem__(self, i: SupportsIndex, v: Any) -> None: ...
    @overload
    def __setitem__(self, i: slice, v: Iterable[Any]) -> None: ...
    def __setitem__(self, i: SupportsIndex | slice, v: Any) -> None:
        """Record a write to a single index."""
        if not isinstance(i, slice):
            ACCESS.append(("w", self._name, _absolute(i, len(self))))
        super().__setitem__(i, v)

    def append(self, v: Any) -> None:
        """Record a write to the new last index."""
        ACCESS.append(("w", self._name, len(self)))
        super().append(v)

    def insert(self, i: SupportsIndex, v: Any) -> None:
        """Record a write where the value lands."""
        idx = max(0, min(len(self), _absolute(i, len(self))))
        ACCESS.append(("w", self._name, idx))
        super().insert(i, v)

    def pop(self, i: SupportsIndex = -1) -> Any:
        """Record a write at the removed index."""
        ACCESS.append(("w", self._name, _absolute(i, len(self))))
        return super().pop(i)


def traced(value: Any, name: str) -> Any:
    """Wrap lists (and lists of lists) so element access is recorded."""
    if type(value) is list:
        return TracedList(
            [traced(x, f"{name}[{i}]") if type(x) is list else x for i, x in enumerate(value)],
            name,
        )
    return value


class StepLimit(BaseException):
    """Raised when a run exceeds its step budget. BaseException so user code cannot swallow it."""


class Meter:
    """Shared step counter that the line tracer and CostList both charge."""

    def __init__(self, limit: int) -> None:
        """Start a meter that raises StepLimit once `limit` steps are exceeded."""
        self.steps = 0
        self.limit = limit

    def charge(self, n: int) -> None:
        """Add n steps."""
        self.steps += n
        if self.steps > self.limit:
            raise StepLimit


METER: Meter | None = None
"""The meter charged by CostList and the costed builtins; None outside measured runs."""


def _charge(n: int) -> None:
    if METER is not None and n > 0:
        METER.charge(n)


def nlogn(n: int) -> int:
    """Steps charged for sorting n items."""
    return n * max(1, math.ceil(math.log2(n))) if n > 1 else n


def log_cost(n: int) -> int:
    """Steps charged for one heap or binary-search operation on n items."""
    return max(1, math.ceil(math.log2(n + 1)))


class CostList(list[Any]):
    """A list whose linear-time operations charge their real cost to the meter."""

    __slots__ = ()

    def __contains__(self, v: object) -> bool:
        """Charge a linear scan."""
        _charge(len(self))
        return super().__contains__(v)

    def index(self, value: Any, start: SupportsIndex = 0, stop: SupportsIndex = 2**63 - 1) -> int:
        """Charge a linear scan."""
        _charge(len(self))
        return super().index(value, start, stop)

    def count(self, value: Any) -> int:
        """Charge a linear scan."""
        _charge(len(self))
        return super().count(value)

    def remove(self, value: Any) -> None:
        """Charge a linear scan and shift."""
        _charge(len(self))
        super().remove(value)

    def insert(self, i: SupportsIndex, v: Any) -> None:
        """Charge for shifting every element after the insertion point."""
        _charge(len(self) - max(0, min(len(self), _absolute(i, len(self)))))
        super().insert(i, v)

    def pop(self, i: SupportsIndex = -1) -> Any:
        """Charge for shifting every element after the removed one."""
        if operator.index(i) != -1:
            _charge(len(self) - _absolute(i, len(self)))
        return super().pop(i)

    @overload
    def __getitem__(self, i: SupportsIndex) -> Any: ...
    @overload
    def __getitem__(self, i: slice) -> CostList: ...
    def __getitem__(self, i: SupportsIndex | slice) -> Any:
        """Charge for copying a slice."""
        if isinstance(i, slice):
            out = CostList(super().__getitem__(i))
            _charge(len(out))
            return out
        return super().__getitem__(i)

    def __add__(self, other: list[Any]) -> CostList:
        """Charge for building the concatenation."""
        out = CostList(list.__add__(self, other))
        _charge(len(out))
        return out

    def __mul__(self, k: SupportsIndex) -> CostList:
        """Charge for building the repetition."""
        out = CostList(list.__mul__(self, k))
        _charge(len(out))
        return out

    def __rmul__(self, k: SupportsIndex) -> CostList:
        """Charge for building the repetition."""
        return self.__mul__(k)

    def extend(self, items: Iterable[Any]) -> None:
        """Charge for each item added."""
        materialised = list(items)
        _charge(len(materialised))
        super().extend(materialised)

    def sort(self, *, key: Callable[[Any], Any] | None = None, reverse: bool = False) -> None:
        """Charge n log n."""
        _charge(nlogn(len(self)))
        super().sort(key=key, reverse=reverse)

    def copy(self) -> CostList:
        """Charge for copying every element."""
        _charge(len(self))
        return CostList(self)


def costed(value: Any) -> Any:
    """Wrap lists (and lists of lists) in CostList."""
    if type(value) is list:
        return CostList(costed(x) if type(x) is list else x for x in value)
    return value


# ---- score mode: charging for builtins and library calls ---------------------


def cost_list(items: Iterable[Any] = ()) -> CostList:
    """Stand in for list displays, comprehensions and list() calls in profiled code."""
    out = CostList(items)
    _charge(len(out))
    return out


def c_sorted(items: Iterable[Any], *, key: Callable[[Any], Any] | None = None, reverse: bool = False) -> CostList:
    """Charge n log n for sorted()."""
    out = sorted(items, key=key, reverse=reverse)
    _charge(nlogn(len(out)))
    return CostList(out)


def _linear(fn: Callable[..., Any]) -> Callable[..., Any]:
    """Wrap min/max/sum so a single sized argument charges its length."""

    def wrapped(*args: Any, **kwargs: Any) -> Any:
        if len(args) == 1 and hasattr(args[0], "__len__"):
            _charge(len(args[0]))
        return fn(*args, **kwargs)

    wrapped.__name__ = fn.__name__
    return wrapped


BUILTINS: dict[str, Callable[..., Any]] = {
    "sorted": c_sorted,
    "min": _linear(min),
    "max": _linear(max),
    "sum": _linear(sum),
    "__cost_list__": cost_list,
}
"""Names injected into profiled modules ahead of the real builtins."""


def _heappush(h: list[Any], x: Any) -> None:
    _charge(log_cost(len(h)))
    real_heapq.heappush(h, x)


def _heappop(h: list[Any]) -> Any:
    _charge(log_cost(len(h)))
    return real_heapq.heappop(h)


def _heappushpop(h: list[Any], x: Any) -> Any:
    _charge(log_cost(len(h)))
    return real_heapq.heappushpop(h, x)


def _heapreplace(h: list[Any], x: Any) -> Any:
    _charge(log_cost(len(h)))
    return real_heapq.heapreplace(h, x)


def _heapify(h: list[Any]) -> None:
    _charge(len(h))
    real_heapq.heapify(h)


def _nlargest(k: int, items: Iterable[Any], key: Callable[[Any], Any] | None = None) -> CostList:
    materialised = list(items)
    _charge(len(materialised) * log_cost(k))
    return CostList(real_heapq.nlargest(k, materialised, key=key))


def _nsmallest(k: int, items: Iterable[Any], key: Callable[[Any], Any] | None = None) -> CostList:
    materialised = list(items)
    _charge(len(materialised) * log_cost(k))
    return CostList(real_heapq.nsmallest(k, materialised, key=key))


def _merge(*iterables: Iterable[Any], key: Callable[[Any], Any] | None = None, reverse: bool = False) -> Iterator[Any]:
    for x in real_heapq.merge(*iterables, key=key, reverse=reverse):
        _charge(log_cost(len(iterables)))
        yield x


HEAPQ: dict[str, Callable[..., Any]] = {
    "heappush": _heappush,
    "heappop": _heappop,
    "heappushpop": _heappushpop,
    "heapreplace": _heapreplace,
    "heapify": _heapify,
    "nlargest": _nlargest,
    "nsmallest": _nsmallest,
    "merge": _merge,
}


def costed_heapq() -> types.ModuleType:
    """Build a heapq look-alike that charges log n per push or pop and n for heapify."""
    mod = types.ModuleType("heapq")
    for name, fn in HEAPQ.items():
        setattr(mod, name, fn)
    return mod


def _costed_search(fn: Callable[..., Any], *, inserts: bool) -> Callable[..., Any]:
    def wrapped(a: list[Any], x: Any, *rest: Any, **kwargs: Any) -> Any:
        _charge(log_cost(len(a)) + (len(a) if inserts else 0))
        return fn(a, x, *rest, **kwargs)

    return wrapped


def costed_bisect() -> types.ModuleType:
    """Build a bisect look-alike: searches charge log n, insorts also charge the shift."""
    mod = types.ModuleType("bisect")
    for name in ("bisect_left", "bisect_right", "bisect", "insort_left", "insort_right", "insort"):
        setattr(mod, name, _costed_search(getattr(real_bisect, name), inserts=name.startswith("insort")))
    return mod
