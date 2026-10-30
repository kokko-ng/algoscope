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
import os
import random
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import traced  # noqa: E402
import tracer  # noqa: E402

STDOUT_LIMIT = 4000


class SolutionError(Exception):
    pass


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Capture(io.StringIO):
    def write(self, s):
        if self.tell() < STDOUT_LIMIT:
            return super().write(s)
        return len(s)


def user_traceback(exc, filename):
    """Format a traceback keeping only frames from the solution file."""
    frames = [f for f in traceback.extract_tb(exc.__traceback__) if f.filename == filename]
    lines = [f"line {f.lineno}, in {f.name}: {(f.line or '').strip()}" for f in frames[-4:]]
    lines.append(f"{type(exc).__name__}: {exc}")
    return {"text": "\n".join(lines), "line": frames[-1].lineno if frames else None}


def check_forbidden(path, forbid):
    """Static check for builtins, methods and modules an exercise asks you to implement yourself."""
    if not forbid:
        return None
    with open(path, encoding="utf-8") as fh:
        tree = ast.parse(fh.read(), filename=path)
    for node in ast.walk(tree):
        hit = None
        if isinstance(node, ast.Name) and node.id in forbid:
            hit = node.id
        elif isinstance(node, ast.Attribute) and node.attr in forbid:
            # calls to the solution's own methods (self.append) are fine
            if not (isinstance(node.value, ast.Name) and node.value.id == "self"):
                hit = node.attr
        elif isinstance(node, ast.Import):
            hit = next((a.name for a in node.names if a.name.split(".")[0] in forbid), None)
        elif isinstance(node, ast.ImportFrom) and node.module and node.module.split(".")[0] in forbid:
            hit = node.module
        if hit:
            return {"text": f"`{hit}` is off limits in this exercise: build it yourself.", "line": node.lineno}
    return None


def canon(x, _depth=0):
    """Normalise a value for comparison: nodes become value lists, floats are rounded."""
    if _depth > 50:
        return repr(x)
    if isinstance(x, bool) or x is None or isinstance(x, (int, str)):
        return x
    if isinstance(x, float):
        return round(x, 6)
    if isinstance(x, (list, tuple)):
        return [canon(v, _depth + 1) for v in x]
    if isinstance(x, (set, frozenset)):
        return sorted((canon(v, _depth + 1) for v in x), key=repr)
    if isinstance(x, dict):
        return {repr(canon(k, _depth + 1)): canon(v, _depth + 1) for k, v in x.items()}
    if hasattr(x, "val") and hasattr(x, "next"):
        out, seen = [], set()
        while x is not None and id(x) not in seen and len(out) < 100_000:
            seen.add(id(x))
            out.append(canon(x.val, _depth + 1))
            x = x.next
        return out
    if hasattr(x, "val") and hasattr(x, "left") and hasattr(x, "right"):
        import algoscope

        return canon(algoscope.tree_values(x), _depth + 1)
    if hasattr(x, "__dict__"):
        return {k: canon(v, _depth + 1) for k, v in vars(x).items() if not k.startswith("_")}
    return repr(x)


def args_text(case, limit=200):
    """Show a function case as its arguments, without the outer tuple."""
    if isinstance(case, tuple):
        text = ", ".join(short_json(a, limit) for a in case)
        return text if len(text) <= limit else text[:limit] + "..."
    return short_json(case, limit)


def short_json(x, limit=200):
    try:
        text = json.dumps(canon(x), default=repr)
    except Exception:
        text = repr(x)
    return text if len(text) <= limit else text[:limit] + "..."


class Runner:
    """Calls a solution's entry point for one case: a function call or a sequence of class operations."""

    def __init__(self, cfg, module, label):
        self.cfg = cfg
        self.kind = cfg.get("kind", "function")
        self.output = cfg.get("output", "return")
        entry = cfg["entry"]
        if not hasattr(module, entry):
            what = "class" if self.kind == "class" else "function"
            raise SolutionError(f"{label} does not define the {what} `{entry}`")
        self.target = getattr(module, entry)
        self.on_op = None

    def params(self):
        if self.kind != "function":
            return []
        try:
            return list(inspect.signature(self.target).parameters)
        except (TypeError, ValueError):
            return []

    def run(self, case):
        if self.kind == "class":
            ops = list(case)
            ctor = ()
            if ops and ops[0][0] == "__init__":
                ctor = tuple(ops[0][1:])
                ops = ops[1:]
            if self.on_op:
                self.on_op(f"{self.cfg['entry']}({', '.join(map(tracer.short, ctor))})")
            obj = self.target(*ctor)
            results = []
            for name, *args in ops:
                if self.on_op:
                    self.on_op(f"{name}({', '.join(map(tracer.short, args))})")
                results.append(getattr(obj, name)(*args))
            return results
        args = case if isinstance(case, tuple) else (case,)
        ret = self.target(*args)
        if self.output == "return":
            return ret
        if self.output.startswith("arg"):
            return args[int(self.output[3:])]
        raise SolutionError(f"unknown output mode {self.output}")


def as_tuple(case):
    return case if isinstance(case, tuple) else (case,)


def compare(cases_mod, case, got, expected):
    if hasattr(cases_mod, "check"):
        return bool(cases_mod.check(case, got, expected))
    return canon(got) == canon(expected)


def run_visual(cfg, run_dir, out):
    sol_path = os.path.join(run_dir, "solution.py")
    cases_mod = load(os.path.join(run_dir, "cases.py"), "cases")
    case = cases_mod.visual()
    ref = Runner(cfg, load(os.path.join(run_dir, "reference.py"), "reference"), "reference.py")
    expected = ref.run(copy.deepcopy(case))

    forbidden = check_forbidden(sol_path, cfg.get("forbid"))
    if forbidden:
        out["error"] = forbidden
        return
    capture = Capture()
    rec = tracer.Recorder(sol_path, cfg.get("watch", []), cfg.get("max_frames", 2500))
    with contextlib.redirect_stdout(capture):
        sol = Runner(cfg, load(sol_path, "solution"), "your code")
        run_case = copy.deepcopy(case)
        if sol.kind == "function":
            names = sol.params()
            args = as_tuple(run_case)
            run_case = tuple(traced.traced(a, names[i] if i < len(names) else f"arg{i}") for i, a in enumerate(args))

        def on_op(label):
            rec.op = label

        sol.on_op = on_op
        traced.ACCESS.clear()
        sys.settrace(rec.global_trace)
        try:
            got = sol.run(run_case)
        except tracer.TraceLimit:
            got = None
        except Exception as exc:  # the solution raised
            sys.settrace(None)
            out["error"] = user_traceback(exc, sol_path)
            got = None
        finally:
            sys.settrace(None)
    out["frames"] = rec.frames
    out["truncated"] = rec.truncated
    out["stdout"] = capture.getvalue()
    out["input"] = args_text(case, 400)
    out["expected"] = short_json(expected, 400)
    if "error" not in out and not rec.truncated:
        out["got"] = short_json(got, 400)
        out["passed"] = compare(cases_mod, case, got, expected)


def run_limited(runner, filename, case, limit):
    """Run one case with a step budget so runaway loops stop quickly. Raises traced.StepLimit."""
    meter = traced.Meter(limit)
    counter = tracer.Counter(filename, meter)
    sys.settrace(counter.global_trace)
    try:
        return runner.run(case)
    finally:
        sys.settrace(None)


def measure(cfg, runner, filename, case, limit):
    """Run one case under the step counter. Returns (steps, hit_limit)."""
    meter = traced.Meter(limit)
    traced.METER = meter
    counter = tracer.Counter(filename, meter)
    run_case = case
    if runner.kind == "function":
        run_case = tuple(traced.costed(a) for a in as_tuple(case))
    sys.settrace(counter.global_trace)
    try:
        runner.run(run_case)
        return meter.steps, False
    except traced.StepLimit:
        return meter.steps, True
    finally:
        sys.settrace(None)
        traced.METER = None


def run_score(cfg, run_dir, out):
    sol_path = os.path.join(run_dir, "solution.py")
    ref_path = os.path.join(run_dir, "reference.py")
    cases_mod = load(os.path.join(run_dir, "cases.py"), "cases")
    forbidden = check_forbidden(sol_path, cfg.get("forbid"))
    if forbidden:
        out["error"] = forbidden
        return
    capture = Capture()
    ref = Runner(cfg, load(ref_path, "reference"), "reference.py")
    seeds = cfg.get("seeds", 2)

    suite = []
    if hasattr(cases_mod, "fixed"):
        suite.extend(cases_mod.fixed())
    suite.append(cases_mod.visual())
    for n in cfg.get("check_sizes", [0, 1, 2, 3, 5, 8, 13, 40]):
        for seed in range(seeds):
            suite.extend(cases_mod.cases(n, random.Random(seed * 7919 + n)))

    passed = 0
    failures = []
    with contextlib.redirect_stdout(capture):
        try:
            sol = Runner(cfg, load(sol_path, "solution"), "your code")
        except SolutionError as exc:
            out["error"] = {"text": str(exc), "line": None}
            return
        for case in suite:
            expected = ref.run(copy.deepcopy(case))
            try:
                got = run_limited(sol, sol_path, copy.deepcopy(case), cfg.get("case_step_limit", 3_000_000))
            except traced.StepLimit:
                out["error"] = {
                    "text": "a test case ran for over 3,000,000 steps: look for an infinite loop",
                    "line": None,
                    "input": args_text(case),
                }
                break
            except Exception as exc:
                out["error"] = user_traceback(exc, sol_path)
                out["error"]["input"] = args_text(case)
                break
            if compare(cases_mod, case, got, expected):
                passed += 1
            elif len(failures) < 3:
                failures.append({"input": args_text(case), "expected": short_json(expected), "got": short_json(got)})
    out["passed"] = passed
    out["total"] = len(suite)
    out["failures"] = failures
    out["stdout"] = capture.getvalue()
    if passed != len(suite) or "error" in out:
        return

    limit = cfg.get("step_limit", 4_000_000)
    user_steps, ref_steps = [], []
    with contextlib.redirect_stdout(Capture()):
        for n in cfg.get("sizes", [50, 100, 200, 400]):
            total_user = total_ref = 0
            over = False
            bench = getattr(cases_mod, "bench", cases_mod.cases)
            for seed in range(seeds):
                for case in bench(n, random.Random(seed * 104729 + n)):
                    steps, hit = measure(cfg, ref, ref_path, copy.deepcopy(case), limit)
                    total_ref += steps
                    steps, hit = measure(cfg, sol, sol_path, copy.deepcopy(case), limit)
                    total_user += steps
                    over = over or hit
            ref_steps.append([n, total_ref])
            user_steps.append([n, total_user])
            if over:
                out["step_limit_hit"] = n
                break
    out["steps"] = {"user": user_steps, "ref": ref_steps}


def main():
    run_dir, mode = os.path.abspath(sys.argv[1]), sys.argv[2]
    sys.setrecursionlimit(20_000)
    with open(os.path.join(run_dir, "config.json"), encoding="utf-8") as fh:
        cfg = json.load(fh)
    out = {"mode": mode}
    try:
        if mode == "visual":
            run_visual(cfg, run_dir, out)
        elif mode == "score":
            run_score(cfg, run_dir, out)
        else:
            raise SystemExit(f"unknown mode {mode}")
    except SyntaxError as exc:
        out["error"] = {"text": f"SyntaxError: {exc.msg}", "line": exc.lineno}
    except SolutionError as exc:
        out["error"] = {"text": str(exc), "line": None}
    except RecursionError:
        out["error"] = {"text": "RecursionError: maximum recursion depth exceeded", "line": None}
    except Exception as exc:
        sol_path = os.path.join(run_dir, "solution.py")
        out["error"] = user_traceback(exc, sol_path)
        out["error"]["internal"] = traceback.format_exc()[-2000:]
    with open(os.path.join(run_dir, "out.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, default=repr)


if __name__ == "__main__":
    main()
