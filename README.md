# algoscope

A terminal workbench for data structures, algorithms and system design. You write Python in an
editor inside the terminal. algoscope runs your code, animates it step by step in ASCII, and
profiles how its cost grows compared with a reference solution. For system design, it animates
requests through an architecture and quizzes you on estimates and trade-offs.

## Tracks

There are two tracks. Switch between them with `1` and `2` on the home screen.

### Data structures and algorithms

It is built for focused 20-30 minute sessions. Every topic goes through three stages:

1. **Watch.** Step through an animated reference implementation, with captions on the key lines.
2. **Build.** Implement the structure or algorithm yourself.
3. **Apply.** Use it on two or three problems.

Topics unlock along a dependency tree, from arrays and two pointers through hashing, sorting, linked
lists, trees, heaps, tries, graphs and dynamic programming. Correct solutions earn points scaled by
an efficiency grade.

### System design

The second track teaches system design through capacity estimation and trade-off questions. Each
topic starts with an animated walkthrough: boxes for clients, load balancers, caches, queues and
databases, with requests that travel between them. Quizzes follow. They set a scenario with real
numbers and ask for estimates or choices. You type answers like `12k` or `1.5M`; each estimate is
accepted within a stated tolerance. Each answer reveals a worked explanation with its own animation.
Grades come from first-try accuracy.

The 13 topics run from back-of-the-envelope estimation through caching, replication, sharding,
quorums, queues, resilience and availability, to case studies of a URL shortener, a news feed and a
chat service.

### Themes

The default look is a plain dev tool: a spec pane, an editor, a trace viewer and a results pane,
with progress shown as a version number. Press F2 for the game theme, with zones, XP, medals and
level-up animations. Press F2 again to switch back.

## Install

algoscope runs your solutions with Python 3.10 or newer. Set `ALGOSCOPE_PYTHON` to choose the
interpreter; the Homebrew formula sets it for you.

**Homebrew** (macOS and Linux):

```sh
brew install kokko-ng/tap/algoscope
```

**Prebuilt binaries** for macOS (Apple silicon and Intel), Linux (x86-64 and ARM) and Windows are on the
[releases page](https://github.com/kokko-ng/algoscope/releases). Unpack the archive and put
`algoscope` on your `PATH`.

**From source** (needs Rust):

```sh
cargo install --path .
```

Then:

```sh
algoscope            # resumes where you left off
algoscope design     # opens on the system design track
algoscope dsa        # opens on the data structures and algorithms track
```

Nothing goes over the network. Progress, drafts and settings are stored in the platform data
directory (`algoscope where` prints it). `algoscope reset` deletes them.

### Colours

Press `c` on the home screen to cycle between the theme's colours, a colour-blind-safe set (blue and
orange in place of green and red), and monochrome. Setting `NO_COLOR` forces monochrome; highlights
then use bold, underline and reverse video.

### How solutions run

Each run happens in a fresh temporary folder, in a separate Python process with a minimal environment
(no tokens or credentials from your shell). A guard stops solution code from starting processes,
opening network connections, loading native code, or changing files outside that folder, and limits
CPU time and file size. This protects against accidents, not against deliberately hostile code: the
content shipped with algoscope is trusted, and so is your own code.

## Keys

| Key | Action |
|---|---|
| Ctrl+E | trace your code on the example input |
| Ctrl+T | run the full suite and profile efficiency |
| Esc / Tab | editor to trace pane (in vim mode, Esc from normal mode) |
| Enter / i | trace pane to editor |
| space, left/right, `[` `]` | play/pause, step, change speed |
| g / G, z | first/last step, zoom the trace pane |
| h | reveal a hint (each costs 10% of the reward) |
| n | next challenge in the topic |
| q | back to the tree (drafts autosave) |
| F2 / t | stealth or game theme |
| v | standard or vim keys (outside the editor) |
| 1 / 2 | home: data structures and algorithms or system design |
| F1 | help |

In a system design quiz, choose with the arrow keys or `a`-`d`, or type a number, then press Enter.
A wrong answer gives one more try; after that the answer and its explanation appear.

The standard keymap uses arrows, shift-select and Ctrl+C/X/V/Z/Y. The vim keymap supports
normal, insert, visual and visual-line modes, common motions and operators, counts, and the
`:w`, `:run`, `:submit` and `:q` commands.

## How grading works

The harness counts executed lines of your solution, plus the hidden linear work in list
operations like `x in items` or `items.insert(0, x)`, at several input sizes. From those counts
it fits a growth exponent and compares it with the reference:

| Grade | Requirement |
|---|---|
| A / gold | same growth class, at most 1.25x the reference's steps |
| B / silver | same growth class, at most 2.5x the reference's steps |
| C / bronze | correct, but grows faster or costs more |

Step counts are deterministic, so the same code always earns the same grade.

## Development

```sh
cargo test                                   # unit, snapshot and render tests
uv run --no-project --with pytest python -m pytest harness/tests
cargo run -- check-content                   # verify every challenge end to end
```

Every commit goes through a strict [pre-commit](https://pre-commit.com) suite. Install it once with
`pre-commit install`; run it any time with `pre-commit run --all-files`. It runs:

- **Hygiene:** whitespace, line endings, merge markers, large files, private keys, secret scanning
  (gitleaks) and spelling (codespell).
- **House rules:** no emoji, and curriculum wording that stays neutral and safe for work.
- **Python:** ruff with every rule enabled and formatting, plus `mypy --strict` on the harness.
- **Rust:** `rustfmt`, clippy with pedantic lints denied, and the full test suite.
- **Content:** `check-content` over the whole curriculum.
- **Commit messages:** Conventional Commits via commitizen, checked when you commit and again when
  you push.

CI runs the same suite and checks the harness and content against Python 3.10 to 3.14.

The Rust side (`src/`) handles the TUI, editor, runner and scoring. The Python harness
(`harness/`) runs solutions, records trace frames and counts steps. It is embedded in the binary
and written to a temp directory for each run. Curriculum content is in `content/dsa/` and `content/design/`; see
[docs/content.md](docs/content.md) to add topics or challenges.

Two reference guides cover every topic in the curriculum, with tested Python samples. Both are
written in ASD-STE100 Simplified Technical English:

- [docs/dsa-guide.md](docs/dsa-guide.md): data structures and algorithms
- [docs/system-design-guide.md](docs/system-design-guide.md): system design
