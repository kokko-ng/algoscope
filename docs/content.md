# Writing content

Content lives in `content/<track>/<topic>/` and is embedded into the binary at build time. The tracks
are `dsa` (data structures and algorithms) and `design` (system design). Each topic is a folder with a
`topic.toml` and one folder per challenge. Prerequisites must be topics of the same track.

## Voice

Neutral and craft-focused: "problem", "exercise", "trace", "suite". The game theme renames things
on screen; content text stays plain. Never mention interviews, hiring, companies or job prep.
No emojis. Short sentences, second person, no filler.

## topic.toml

```toml
id = "sliding-window"            # folder name
title = "Sliding window"         # stealth theme name
zone = "The Moving Frame"        # game theme name
summary = "Two or three sentences on the idea and why it matters."
prereqs = ["two-pointers"]       # topic ids; the topic unlocks when their build stages are done
order = 3                        # position in the curriculum
challenges = ["window-walkthrough", "window-engine", "max-window-sum", "longest-unique"]
```

Every topic has exactly one `watch`, at least one `build` and two or three `apply` challenges, in that order.

## A challenge folder

| file | purpose |
|---|---|
| `challenge.toml` | metadata, statement, hints, views |
| `reference.py` | correct, idiomatic solution. Its steps are the yardstick for grading |
| `starter.py` | what the user starts from (not needed for `watch`). Must fail the suite |
| `cases.py` | inputs: `visual()`, `cases(n, rng)`, optional `fixed()`, `bench(n, rng)`, `check(case, got, expected)` |

### challenge.toml

```toml
id = "max-window-sum"
title = "Best window of size k"
stage = "apply"                  # watch | build | apply
xp = 120                         # watch 40, build 150-200, apply 80-160
complexity = "O(n)"              # the reference's growth; check-content verifies it
kind = "function"                # or "class" (entry is a class driven by operation lists)
entry = "solve"                  # function or class name
output = "return"                # or "arg0": the first argument after the call (in-place problems)
forbid = ["sorted", "sort"]      # names, attributes or modules the solution may not use
sizes = [50, 100, 200, 400]      # n values for profiling (default shown)
check_sizes = [0, 1, 2, 3, 5, 8, 13, 40]   # n values for the correctness suite (default shown)
seeds = 2                        # cases per size
statement = """Markdown-ish plain text."""
hints = ["gentle nudge", "stronger nudge"]   # each costs 10% of the reward

[[view]]                         # what the trace pane draws, top to bottom
var = "nums"                     # a local name, or dotted like "self.slots"
as = "array"                     # see view kinds below
label = "nums"                   # optional display name
pointers = ["lo", "hi"]          # index variables drawn as arrows (array, bars), or node refs
window = ["lo", "hi"]            # optional: shade the inclusive range between two index variables

[[captions]]                     # watch stage only: shown when that line runs
line = 7
text = "What is happening and why."
```

### View kinds

| kind | value it expects | pointers |
|---|---|---|
| `array` | list | int variables, drawn as arrows under cells |
| `bars` | list of numbers (sorting) | int variables |
| `grid` | list of lists (DP tables, matrices) | first two pointers are (row, col) of the focus cell |
| `value` | anything, one line | none |
| `set` | set or list, one line | none |
| `map` | dict | none |
| `buckets` | list of lists (hash table chains) | none |
| `stack` | list, top drawn first | none |
| `queue` | list or deque, front on the left | none |
| `linked` | a node with `val` and `next` (ListNode) | variables holding nodes (`slow`, `fast`) |
| `tree` | a node with `val`, `left`, `right` (TreeNode) | variables holding nodes |
| `heap` | list used as a binary heap | int index variables |
| `trie` | a node with a `children` dict and an `end`/`is_end` flag | variables holding nodes |
| `graph` | dict `{node: [neighbours]}` or list of lists; weighted neighbours as `(v, w)` | scalar = current node; first collection = visited; second = frontier |

Views only show variables in scope at that step; anything else reads "(not assigned yet)". Every
pointer and window variable is snapshotted, so you can point at a name that exists in only part of
the code.

### cases.py

```python
def visual():
    """One small, readable input for the trace: 5-10 elements, under ~400 steps."""
    return ([1, 3, 4, 6, 8, 11, 14], 17)  # a tuple of positional arguments


def fixed():
    """Edge cases, each an argument tuple."""
    return [([], 5), ([2], 4)]


def cases(n, rng):
    """Random inputs of size n for correctness. Return a list of argument tuples."""
    return [(sorted(rng.sample(range(10 * n + 10), n)), rng.randint(0, 20 * n))]


def bench(n, rng):
    """Optional: worst-case-ish inputs of size n for profiling (defaults to cases)."""


def check(case, got, expected):
    """Optional: custom comparison when many answers are valid."""
```

- Expected outputs come from running `reference.py`, so cases never hard-code answers.
- Single-argument functions still return 1-tuples: `return ([5, 2, 9],)`.
- For `kind = "class"` a case is a list of operations: `[("__init__", 8), ("push", 3), ("pop",)]`.
  The leading `__init__` entry is optional. The output compared is the list of every method's return value.
- Linked lists and trees: `from algoscope import ListNode, TreeNode, build_list, build_tree` works in
  every file, and solutions get the same import. Outputs that are nodes are compared by value
  (a list for linked lists, level order for trees).
- Outputs are compared after normalising: tuples become lists, sets sort, floats round to 6 places.
- Profiling counts executed lines in the solution file plus the real cost of hidden work: linear
  list operations (`in`, `index`, `insert(0, ..)`, `pop(0)`, slices, `+`, `*`) on every list, `sorted`
  and `list.sort` at n log n, single-iterable `min`/`max`/`sum` at n, and `heapq`/`bisect` calls at
  log n. Still list builtins in `forbid` when the exercise is about implementing them.
- Each correctness case has a budget of 3,000,000 steps (`case_step_limit` in the harness). Keep
  `check_sizes` small enough that the slow-but-correct approaches you want graded bronze finish
  within it; exponential approaches that blow it are reported as far too slow.
- Keep the reference's profiled sizes under ~1M steps at the largest n. Exponential problems
  (backtracking) use small sizes such as `sizes = [6, 8, 10, 12]`.
- The step-count fit must match the declared complexity: `O(1)`/`O(log n)` below 0.4, `O(n)` 0.75-1.2,
  `O(n log n)` 0.95-1.5, `O(n^2)` 1.6-2.4, `O(2^n)`/`O(n!)` above 2.5. Recognised strings are listed
  in `src/check.rs`; add a mapping there if you need a new one.

## Checking

```sh
cargo run -- check-content                 # everything embedded
cargo run -- check-content --topic graphs  # topic ids containing "graphs"
cargo run -- check-content --dir path/to/topics   # topics on disk, without rebuilding
```

For every challenge, the check confirms that:

- the reference traces cleanly
- every view variable shows up
- the trace stays under 900 steps
- the reference passes the full suite and grades gold
- the measured growth matches `complexity`
- the starter fails the suite

## System design content

System design topics live in `content/design/<topic>/`. Their challenges are pure data: each folder
has only a `challenge.toml`, with no Python files. A topic has one `watch` walkthrough first, then 2-4
`quiz` challenges. A design topic unlocks its dependants once its first quiz is done.

### The diagram

Every design challenge has a `[diagram]`: boxes on a grid, links between them, and animation steps.

```toml
[diagram]
nodes = [
  { id = "client", label = "Client", at = [0, 0] },      # at = [column, row]
  { id = "lb", label = "Load balancer", at = [1, 0] },
  { id = "db", label = "Database", at = [2, 1] },
]
links = [["client", "lb"], ["lb", "db"]]

[[diagram.steps]]
flow = ["client", "lb", "db"]     # packets travel along this path (two or more node ids)
packets = 3                       # how many packets, one after another (default 1)
highlight = ["lb"]                # nodes drawn in the accent colour
down = ["db"]                     # nodes drawn as failed
labels = { lb = "2,300 req/s" }   # short notes under nodes
caption = "One or two sentences that explain this step."
```

- Keep diagrams to 3 columns and 3 rows at most, with labels of 16 characters or fewer.
- A walkthrough plays its `diagram.steps` once: use 4-7 steps, each with a caption.
- In a quiz, `diagram.steps` is the scene that loops while the user answers. Captions are optional.

### Questions

```toml
[[questions]]
prompt = "What is the average number of photo views per second?"
answer = 2315          # a number answer
tolerance = 0.25       # accepted relative error: 0.25 accepts 75% to 125% of the answer
unit = "views per second"
hint = "Multiply users by views per user, then divide by the seconds in a day."
explanation = "Shown after a correct answer or after two wrong attempts. Show the working."

[[questions.steps]]    # optional animation that plays with the explanation
flow = ["users", "app"]
caption = "Daily volume divided by seconds in a day gives the average rate."

[[questions]]
prompt = "Which operation takes the longest?"
choices = ["A memory reference", "A disk seek", "A round trip between continents"]
answer = 3             # 1-based: the third choice
explanation = "..."
```

- Number answers accept forms like `12000`, `12k`, `1.5M`, `3e6` and `2.5GB`. State the unit in
  the prompt when it matters (for example "in TB").
- Set the tolerance so that sensible rounding passes and a wrong method fails: 0.25 for estimates,
  0.1 for exact arithmetic.
- Grades come from first-try accuracy: all right is gold, 60% or more is silver, less is bronze.
- Give the scenario's numbers in the statement, so the quiz never depends on memorised trivia, except
  for the standard figures that the topic teaches (latency numbers, seconds in a day).
- `check-content` validates design content statically: answers in range, tolerances, node ids in
  every link and step, and an explanation for each question.
