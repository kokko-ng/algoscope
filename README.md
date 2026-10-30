# algoscope

A terminal workbench for data structures and algorithms. You write Python in an editor inside the
terminal. algoscope runs your code, animates it step by step in ASCII, and profiles how its cost
grows compared with a reference solution.

It is built for focused 20-30 minute sessions. Every topic goes through three stages:

1. **Watch.** Step through an animated reference implementation, with captions on the key lines.
2. **Build.** Implement the structure or algorithm yourself.
3. **Apply.** Use it on two or three problems.

Topics unlock along a dependency tree, from arrays and two pointers through hashing, sorting, linked
lists, trees, heaps, tries, graphs and dynamic programming. Correct solutions earn points scaled by
an efficiency grade.

The default look is a plain dev tool: a spec pane, an editor, a trace viewer and a results pane,
with progress shown as a version number. Press F2 for the game theme, with zones, XP, medals and
level-up animations. Press F2 again to switch back.

## Install

You need Rust (stable) and Python 3.10 or newer on `PATH`. Set `ALGOSCOPE_PYTHON` to use a
different interpreter.

```sh
cargo install --path .
algoscope
```

Nothing goes over the network. Progress, drafts and settings are stored in the platform data
directory (`algoscope where` prints it). `algoscope reset` deletes them.

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
| F1 | help |

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
and written to a temp directory for each run. Curriculum content is in `content/`; see
[docs/content.md](docs/content.md) to add topics or challenges.
