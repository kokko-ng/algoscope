"""algoscope harness.

Usage: python3 -I harness.py <run_dir> <visual|score>

run_dir holds config.json, solution.py, reference.py and cases.py. Results are
written to run_dir/out.json. The solution's own output is captured, never mixed
with the results.
"""

from __future__ import annotations

import ast
import contextlib
import copy
import importlib.util
import inspect
import io
import json
import random
import sys
import traceback
import types
from pathlib import Path
from typing import TYPE_CHECKING, Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

# path setup must run before importing sibling harness modules
import algoscope  # noqa: E402

# path setup must run before importing sibling harness modules
import traced  # noqa: E402

# path setup must run before importing sibling harness modules
import tracer  # noqa: E402

if TYPE_CHECKING:
    from collections.abc import Callable

STDOUT_LIMIT = 4000
CANON_DEPTH = 50
CHAIN_LIMIT = 100_000
TEXT_LIMIT = 200
VISUAL_TEXT_LIMIT = 400
MAX_FAILURES = 3
CASE_STEP_LIMIT = 3_000_000
PROFILE_STEP_LIMIT = 4_000_000
DEFAULT_CHECK_SIZES = [0, 1, 2, 3, 5, 8, 13, 40]
DEFAULT_SIZES = [50, 100, 200, 400]

Config = dict[str, Any]
Out = dict[str, Any]
Case = Any


class SolutionError(Exception):
    """The solution cannot be run as written (for example, its entry point is missing)."""


def load(path: Path, name: str) -> types.ModuleType:
    """Import a Python file as a module."""
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        msg = f"cannot load {path}"
        raise SolutionError(msg)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ListsToCostLists(ast.NodeTransformer):
    """Route list displays, comprehensions and list() calls through traced.cost_list."""

    @staticmethod
    def _wrap(node: ast.expr) -> ast.expr:
        call = ast.Call(func=ast.Name(id="__cost_list__", ctx=ast.Load()), args=[node], keywords=[])
        return ast.copy_location(call, node)

    def visit_List(self, node: ast.List) -> ast.expr:
        """Wrap list displays that build a value."""
        self.generic_visit(node)
        return self._wrap(node) if isinstance(node.ctx, ast.Load) else node

    def visit_ListComp(self, node: ast.ListComp) -> ast.expr:
        """Wrap list comprehensions."""
        self.generic_visit(node)
        return self._wrap(node)

    def visit_Call(self, node: ast.Call) -> ast.expr:
        """Redirect list(...) calls."""
        self.generic_visit(node)
        if isinstance(node.func, ast.Name) and node.func.id == "list":
            node.func = ast.copy_location(ast.Name(id="__cost_list__", ctx=ast.Load()), node.func)
        return node


def load_costed(path: Path, name: str) -> types.ModuleType:
    """Load a module for profiling: lists it builds and the builtins it calls charge their real cost."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    tree = ast.fix_missing_locations(ListsToCostLists().visit(tree))
    module = types.ModuleType(name)
    module.__file__ = str(path)
    module.__dict__.update(traced.BUILTINS)
    sys.modules[name] = module
    # Running the solution is the harness's whole purpose; it executes in a throwaway process.
    # running the solution is the harness's job; it executes in a throwaway process
    exec(compile(tree, str(path), "exec"), module.__dict__)  # noqa: S102
    return module


def use_costed_libraries() -> None:
    """Make `import heapq` and `import bisect` in profiled code charge their real cost."""
    sys.modules["heapq"] = traced.costed_heapq()
    sys.modules["bisect"] = traced.costed_bisect()


class Capture(io.StringIO):
    """Captures the solution's printed output, up to a limit."""

    def write(self, s: str) -> int:
        """Keep output until the limit, then drop the rest."""
        if self.tell() < STDOUT_LIMIT:
            return super().write(s)
        return len(s)


def user_traceback(exc: BaseException, filename: Path) -> dict[str, Any]:
    """Format a traceback keeping only frames from the solution file."""
    frames = [f for f in traceback.extract_tb(exc.__traceback__) if f.filename == str(filename)]
    lines = [f"line {f.lineno}, in {f.name}: {(f.line or '').strip()}" for f in frames[-4:]]
    lines.append(f"{type(exc).__name__}: {exc}")
    return {"text": "\n".join(lines), "line": frames[-1].lineno if frames else None}


def _bound_names(tree: ast.AST) -> set[str]:
    """Names the solution binds itself (variables, parameters, functions): these are not the builtin."""
    bound = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            bound.add(node.id)
        elif isinstance(node, ast.arg):
            bound.add(node.arg)
        elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            bound.add(node.name)
    return bound


LITERALS: dict[type[ast.AST], str] = {ast.Dict: "dict", ast.DictComp: "dict", ast.Set: "set", ast.SetComp: "set"}


def _forbidden_use(node: ast.AST, forbid: list[str], bound: set[str]) -> str | None:
    if isinstance(node, ast.Name):
        return node.id if node.id in forbid and node.id not in bound else None
    if isinstance(node, ast.Attribute):
        # calls to the solution's own methods (self.append) are fine
        own = isinstance(node.value, ast.Name) and node.value.id == "self"
        return node.attr if node.attr in forbid and not own else None
    if isinstance(node, ast.Import):
        return next((a.name for a in node.names if a.name.split(".")[0] in forbid), None)
    if isinstance(node, ast.ImportFrom):
        return node.module if node.module and node.module.split(".")[0] in forbid else None
    literal = LITERALS.get(type(node))
    return f"{literal} literal" if literal in forbid else None


def check_forbidden(path: Path, forbid: list[str] | None) -> dict[str, Any] | None:
    """Static check for builtins, methods and modules an exercise asks you to implement yourself."""
    if not forbid:
        return None
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    bound = _bound_names(tree)
    for node in ast.walk(tree):
        hit = _forbidden_use(node, forbid, bound)
        if hit:
            return {"text": f"`{hit}` is off limits in this exercise: build it yourself.", "line": node.lineno}  # type: ignore[attr-defined]
    return None


def _canon_nodes(x: Any, depth: int) -> Any:
    """Linked lists become value lists; binary trees become level-order lists."""
    if hasattr(x, "val") and hasattr(x, "next"):
        out: list[Any] = []
        seen: set[int] = set()
        while x is not None and id(x) not in seen and len(out) < CHAIN_LIMIT:
            seen.add(id(x))
            out.append(canon(x.val, depth + 1))
            x = x.next
        return out
    if hasattr(x, "val") and hasattr(x, "left") and hasattr(x, "right"):
        return canon(algoscope.tree_values(x), depth + 1)
    if hasattr(x, "__dict__"):
        return {k: canon(v, depth + 1) for k, v in vars(x).items() if not k.startswith("_")}
    return repr(x)


def canon(x: Any, depth: int = 0) -> Any:
    """Normalise a value for comparison: nodes become value lists, floats are rounded."""
    if depth > CANON_DEPTH:
        return repr(x)
    if x is None or isinstance(x, (bool, int, str, float)):
        return round(x, 6) if isinstance(x, float) else x
    if isinstance(x, (list, tuple)):
        return [canon(v, depth + 1) for v in x]
    if isinstance(x, (set, frozenset)):
        return sorted((canon(v, depth + 1) for v in x), key=repr)
    if isinstance(x, dict):
        return {repr(canon(k, depth + 1)): canon(v, depth + 1) for k, v in x.items()}
    return _canon_nodes(x, depth)


def short_json(x: Any, limit: int = TEXT_LIMIT) -> str:
    """Compact JSON text for a value, truncated."""
    try:
        text = json.dumps(canon(x), default=repr)
    except (TypeError, ValueError, RecursionError):
        text = repr(x)
    return text if len(text) <= limit else text[:limit] + "..."


def args_text(case: Case, limit: int = TEXT_LIMIT) -> str:
    """Show a function case as its arguments, without the outer tuple."""
    if isinstance(case, tuple):
        text = ", ".join(short_json(a, limit) for a in case)
        return text if len(text) <= limit else text[:limit] + "..."
    return short_json(case, limit)


def as_tuple(case: Case) -> tuple[Any, ...]:
    """Function cases are argument tuples; a bare value is a single argument."""
    return case if isinstance(case, tuple) else (case,)


class Runner:
    """Calls a solution's entry point for one case: a function call or a sequence of class operations."""

    def __init__(self, cfg: Config, module: types.ModuleType, label: str) -> None:
        """Bind to the configured entry point of `module`."""
        self.cfg = cfg
        self.kind: str = cfg.get("kind", "function")
        self.output: str = cfg.get("output", "return")
        entry = cfg["entry"]
        if not hasattr(module, entry):
            what = "class" if self.kind == "class" else "function"
            msg = f"{label} does not define the {what} `{entry}`"
            raise SolutionError(msg)
        self.target: Callable[..., Any] = getattr(module, entry)
        self.on_op: Callable[[str], None] | None = None

    def params(self) -> list[str]:
        """Parameter names of a function entry point."""
        if self.kind != "function":
            return []
        try:
            return list(inspect.signature(self.target).parameters)
        except (TypeError, ValueError):
            return []

    def _announce(self, name: str, args: tuple[Any, ...] | list[Any]) -> None:
        if self.on_op:
            self.on_op(f"{name}({', '.join(map(tracer.short, args))})")

    def run(self, case: Case) -> Any:
        """Run one case and return what is compared against the reference."""
        if self.kind == "class":
            ops = list(case)
            ctor: tuple[Any, ...] = ()
            if ops and ops[0][0] == "__init__":
                ctor = tuple(ops[0][1:])
                ops = ops[1:]
            self._announce(self.cfg["entry"], ctor)
            obj = self.target(*ctor)
            results = []
            for name, *args in ops:
                self._announce(name, args)
                results.append(getattr(obj, name)(*args))
            return results
        args = as_tuple(case)
        ret = self.target(*args)
        if self.output == "return":
            return ret
        if self.output.startswith("arg"):
            return args[int(self.output[3:])]
        msg = f"unknown output mode {self.output}"
        raise SolutionError(msg)


def compare(cases_mod: types.ModuleType, case: Case, got: Any, expected: Any) -> bool:
    """Whether an answer matches the reference, using the challenge's own check when it has one."""
    if hasattr(cases_mod, "check"):
        try:
            return bool(cases_mod.check(copy.deepcopy(case), got, expected))
        # a check that trips over a malformed answer means the answer is wrong
        except Exception:  # noqa: BLE001
            return False
    return bool(canon(got) == canon(expected))


def _trace_solution(cfg: Config, sol_path: Path, case: Case, out: Out) -> tuple[tracer.Recorder, Any, str]:
    """Run the solution under the recorder. Returns the recorder, the answer and captured output."""
    capture = Capture()
    rec = tracer.Recorder(str(sol_path), cfg.get("watch", []), cfg.get("max_frames", 2500))
    got = None
    with contextlib.redirect_stdout(capture):
        sol = Runner(cfg, load(sol_path, "solution"), "your code")
        run_case = copy.deepcopy(case)
        if sol.kind == "function":
            names = sol.params()
            args = as_tuple(run_case)
            run_case = tuple(traced.traced(a, names[i] if i < len(names) else f"arg{i}") for i, a in enumerate(args))

        def on_op(label: str) -> None:
            rec.op = label

        sol.on_op = on_op
        traced.ACCESS.clear()
        sys.settrace(rec.global_trace)
        try:
            got = sol.run(run_case)
        except tracer.TraceLimitError:
            pass
        # any exception from the solution is reported, not raised
        except Exception as exc:  # noqa: BLE001
            sys.settrace(None)
            out["error"] = user_traceback(exc, sol_path)
        finally:
            sys.settrace(None)
    return rec, got, capture.getvalue()


def run_visual(cfg: Config, run_dir: Path, out: Out) -> None:
    """Trace the solution on the small visual case."""
    sol_path = run_dir / "solution.py"
    cases_mod = load(run_dir / "cases.py", "cases")
    case = cases_mod.visual()
    ref = Runner(cfg, load(run_dir / "reference.py", "reference"), "reference.py")
    expected = ref.run(copy.deepcopy(case))

    forbidden = check_forbidden(sol_path, cfg.get("forbid"))
    if forbidden:
        out["error"] = forbidden
        return
    rec, got, stdout = _trace_solution(cfg, sol_path, case, out)
    out["frames"] = rec.frames
    out["truncated"] = rec.truncated
    out["stdout"] = stdout
    out["input"] = args_text(case, VISUAL_TEXT_LIMIT)
    out["expected"] = short_json(expected, VISUAL_TEXT_LIMIT)
    if "error" not in out and not rec.truncated:
        out["got"] = short_json(got, VISUAL_TEXT_LIMIT)
        out["passed"] = compare(cases_mod, case, got, expected)


def run_limited(runner: Runner, filename: Path, case: Case, limit: int) -> Any:
    """Run one case with a step budget so runaway loops stop quickly. Raises traced.StepLimit."""
    meter = traced.Meter(limit)
    traced.METER = meter
    counter = tracer.Counter(str(filename), meter)
    sys.settrace(counter.global_trace)
    try:
        return runner.run(case)
    finally:
        sys.settrace(None)
        traced.METER = None


def measure(runner: Runner, filename: Path, case: Case, limit: int) -> tuple[int, bool]:
    """Run one case under the step counter. Returns (steps, hit_limit)."""
    meter = traced.Meter(limit)
    traced.METER = meter
    counter = tracer.Counter(str(filename), meter)
    run_case = case
    if runner.kind == "function":
        run_case = tuple(traced.costed(a) for a in as_tuple(case))
    sys.settrace(counter.global_trace)
    try:
        runner.run(run_case)
    except traced.StepLimit:
        return meter.steps, True
    else:
        return meter.steps, False
    finally:
        sys.settrace(None)
        traced.METER = None


def build_suite(cfg: Config, cases_mod: types.ModuleType) -> list[Case]:
    """Fixed edge cases, the visual case and seeded random cases at each check size."""
    suite: list[Case] = []
    if hasattr(cases_mod, "fixed"):
        suite.extend(cases_mod.fixed())
    suite.append(cases_mod.visual())
    for n in cfg.get("check_sizes", DEFAULT_CHECK_SIZES):
        for seed in range(cfg.get("seeds", 2)):
            # seeded so every run sees the same cases; not security sensitive
            # seeded so every run sees the same cases; not security sensitive
            suite.extend(cases_mod.cases(n, random.Random(seed * 7919 + n)))  # noqa: S311
    return suite


def check_suite(cfg: Config, run_dir: Path, ref: Runner, sol: Runner, out: Out) -> bool:
    """Run every case against the reference. Records results in `out`; returns whether all passed."""
    cases_mod = load(run_dir / "cases.py", "cases")
    sol_path = run_dir / "solution.py"
    suite = build_suite(cfg, cases_mod)
    passed = 0
    failures: list[dict[str, str]] = []
    for case in suite:
        expected = ref.run(copy.deepcopy(case))
        try:
            got = run_limited(sol, sol_path, copy.deepcopy(case), cfg.get("case_step_limit", CASE_STEP_LIMIT))
        except traced.StepLimit:
            out["error"] = {
                "text": "a small test case ran for over 3,000,000 steps: "
                "an infinite loop, or an approach far slower than needed",
                "line": None,
                "input": args_text(case),
            }
            break
        # any exception from the solution is reported, not raised
        except Exception as exc:  # noqa: BLE001
            out["error"] = user_traceback(exc, sol_path)
            out["error"]["input"] = args_text(case)
            break
        if compare(cases_mod, case, got, expected):
            passed += 1
        elif len(failures) < MAX_FAILURES:
            failures.append({"input": args_text(case), "expected": short_json(expected), "got": short_json(got)})
    out["passed"] = passed
    out["total"] = len(suite)
    out["failures"] = failures
    return passed == len(suite) and "error" not in out


def profile(cfg: Config, run_dir: Path, ref: Runner, sol: Runner, out: Out) -> None:
    """Count steps for the reference and the solution at each profiling size."""
    cases_mod = load(run_dir / "cases.py", "cases")
    bench = getattr(cases_mod, "bench", cases_mod.cases)
    limit = cfg.get("step_limit", PROFILE_STEP_LIMIT)
    user_steps: list[list[int]] = []
    ref_steps: list[list[int]] = []
    for n in cfg.get("sizes", DEFAULT_SIZES):
        total_user = total_ref = 0
        over = False
        for seed in range(cfg.get("seeds", 2)):
            # seeded test data, not security sensitive
            for case in bench(n, random.Random(seed * 104729 + n)):  # noqa: S311
                steps, _ = measure(ref, run_dir / "reference.py", copy.deepcopy(case), limit)
                total_ref += steps
                steps, hit = measure(sol, run_dir / "solution.py", copy.deepcopy(case), limit)
                total_user += steps
                over = over or hit
        ref_steps.append([n, total_ref])
        user_steps.append([n, total_user])
        if over:
            out["step_limit_hit"] = n
            break
    out["steps"] = {"user": user_steps, "ref": ref_steps}


def run_score(cfg: Config, run_dir: Path, out: Out) -> None:
    """Run the full suite, then profile when every case passes."""
    sol_path = run_dir / "solution.py"
    forbidden = check_forbidden(sol_path, cfg.get("forbid"))
    if forbidden:
        out["error"] = forbidden
        return
    capture = Capture()
    use_costed_libraries()
    ref = Runner(cfg, load_costed(run_dir / "reference.py", "reference"), "reference.py")
    with contextlib.redirect_stdout(capture):
        try:
            sol = Runner(cfg, load_costed(sol_path, "solution"), "your code")
        except SolutionError as exc:
            out["error"] = {"text": str(exc), "line": None}
            return
        all_passed = check_suite(cfg, run_dir, ref, sol, out)
    out["stdout"] = capture.getvalue()
    if all_passed:
        with contextlib.redirect_stdout(Capture()):
            profile(cfg, run_dir, ref, sol, out)


def main() -> None:
    """Run one mode and write out.json."""
    run_dir, mode = Path(sys.argv[1]).resolve(), sys.argv[2]
    sys.setrecursionlimit(20_000)
    cfg = json.loads((run_dir / "config.json").read_text(encoding="utf-8"))
    out: Out = {"mode": mode}
    try:
        if mode == "visual":
            run_visual(cfg, run_dir, out)
        elif mode == "score":
            run_score(cfg, run_dir, out)
        else:
            sys.exit(f"unknown mode {mode}")
    except SyntaxError as exc:
        out["error"] = {"text": f"SyntaxError: {exc.msg}", "line": exc.lineno}
    except SolutionError as exc:
        out["error"] = {"text": str(exc), "line": None}
    except RecursionError:
        out["error"] = {"text": "RecursionError: maximum recursion depth exceeded", "line": None}
    # errors in the solution's module code land here and are reported
    except Exception as exc:  # noqa: BLE001
        out["error"] = user_traceback(exc, run_dir / "solution.py")
        out["error"]["internal"] = traceback.format_exc()[-2000:]
    (run_dir / "out.json").write_text(json.dumps(out, default=repr), encoding="utf-8")


if __name__ == "__main__":
    main()
