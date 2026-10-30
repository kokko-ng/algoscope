//! Snapshot tests for the visualisers and the main screens, rendered to a test buffer.

#![expect(clippy::needless_pass_by_value, reason = "test helpers take json! values directly")]

use ratatui::Terminal;
use ratatui::backend::TestBackend;
use ratatui::buffer::Buffer;

use crate::app::{App, Screen};
use crate::content::Library;
use crate::progress::{Store, ThemeKind};
use crate::runner::{self, Mode, Outcome};
use crate::tui::ui;

pub fn buffer_text(buf: &Buffer) -> String {
    let mut out = String::new();
    for y in 0..buf.area.height {
        let mut line = String::new();
        for x in 0..buf.area.width {
            line.push_str(buf[(x, y)].symbol());
        }
        out.push_str(line.trim_end());
        out.push('\n');
    }
    out
}

/// Render a challenge's workspace with its reference trace at a given step.
pub fn render_challenge(key: &str, step: usize, theme: ThemeKind, w: u16, h: u16) -> String {
    let lib = Library::load().unwrap();
    let dir = tempfile::tempdir().unwrap();
    let mut app = App::new(lib, Store::new(dir.path().to_path_buf()));
    if app.settings.theme != theme {
        app.toggle_theme();
    }
    app.open(key);
    let ch = app.lib.challenge(key).unwrap().clone();
    let Ok(Outcome::Visual(v)) = runner::run(&ch, Mode::Visual, &ch.reference) else { panic!("visual run failed") };
    if let Screen::Work(ws) = &mut app.screen {
        ws.pending = None;
        ws.editor.set_text(&ch.reference);
        let n = v.frames.len();
        ws.visual = Some(v);
        ws.timeline = runner::trace::Timeline::new(n, 3);
        ws.timeline.playing = false;
        ws.timeline.seek(step.min(n.saturating_sub(1)));
        ws.timeline.since_change = 100;
        ws.focus = crate::app::Focus::Viz;
    }
    let mut term = Terminal::new(TestBackend::new(w, h)).unwrap();
    term.draw(|f| ui::draw(f, &mut app)).unwrap();
    let text = buffer_text(term.backend().buffer());
    // the session clock changes between runs
    text.lines()
        .map(|l| {
            if l.contains("help") && l.contains(':') {
                l.split("  ").next().unwrap_or("").to_string()
            } else {
                l.to_string()
            }
        })
        .collect::<Vec<_>>()
        .join("\n")
}

#[test]
fn pair_sum_workspace_renders() {
    let text = render_challenge("two-pointers/pair-sum", 6, ThemeKind::Stealth, 120, 34);
    println!("{text}");
    assert!(text.contains("nums"));
    assert!(text.contains("left"));
}

#[test]
fn class_walkthrough_renders() {
    let text = render_challenge("foundations/growth-walkthrough", 30, ThemeKind::Game, 110, 30);
    println!("{text}");
    assert!(text.contains("slots"));
}

// ---- per-view snapshots from synthetic frames --------------------------------

use crate::content::ViewSpec;
use crate::runner::trace::Frame;
use crate::tui::theme::Theme;
use crate::tui::viz::{Ctx, VizView};
use ratatui::layout::Rect;
use serde_json::{Value, json};

fn spec(toml_src: &str) -> Vec<ViewSpec> {
    #[derive(serde::Deserialize)]
    struct W {
        view: Vec<ViewSpec>,
    }
    toml::from_str::<W>(toml_src).unwrap().view
}

fn draw(views: &str, frame: Value, prev: Option<Value>, w: u16, h: u16) -> String {
    let views = spec(views);
    let frame = Frame::from_json(&frame);
    let prev = prev.map(|p| Frame::from_json(&p));
    let theme = Theme::new(ThemeKind::Stealth);
    let mut buf = Buffer::empty(Rect::new(0, 0, w, h));
    let viz = VizView {
        ctx: Ctx { theme: &theme, frame: &frame, prev: prev.as_ref(), tween: 1.0 },
        views: &views,
        caption: None,
    };
    viz.render(buf.area, &mut buf);
    buffer_text(&buf)
}

fn list(items: Value) -> Value {
    let n = items.as_array().unwrap().len();
    json!({"k": "list", "items": items, "len": n})
}

fn node(cls: &str, fields: Value) -> Value {
    json!({"cls": cls, "fields": fields})
}

fn r(id: u64) -> Value {
    json!({"k": "ref", "id": id})
}

#[test]
fn array_with_pointers_window_and_access() {
    let frame = json!({"line": 3, "vars": {"nums": list(json!([4, 8, 15, 16, 23, 42])), "lo": 1, "hi": 4},
        "locals": {"k": 3}, "reads": [["nums", 2]], "writes": [["nums", 4]]});
    insta::assert_snapshot!(draw(
        "[[view]]\nvar = \"nums\"\nas = \"array\"\npointers = [\"lo\", \"hi\"]\nwindow = [\"lo\", \"hi\"]",
        frame,
        None,
        60,
        9
    ));
}

#[test]
fn bars_view() {
    let frame = json!({"line": 1, "vars": {"a": list(json!([5, 1, 4, 2, 8, 3])), "i": 2}});
    insta::assert_snapshot!(draw("[[view]]\nvar = \"a\"\nas = \"bars\"\npointers = [\"i\"]", frame, None, 40, 13));
}

#[test]
fn grid_view_marks_changes() {
    let row = |v: Value| list(v);
    let prev = json!({"line": 1, "vars": {"dp": list(json!([row(json!([1, 2, 3])), row(json!([4, 0, 0]))]))}});
    let frame =
        json!({"line": 2, "vars": {"dp": list(json!([row(json!([1, 2, 3])), row(json!([4, 6, 0]))])), "r": 1, "c": 1}});
    insta::assert_snapshot!(draw(
        "[[view]]\nvar = \"dp\"\nas = \"grid\"\npointers = [\"r\", \"c\"]",
        frame,
        Some(prev),
        40,
        6
    ));
}

#[test]
fn linked_list_with_pointers() {
    let frame = json!({"line": 4, "vars": {"head": r(1), "slow": r(2), "fast": r(3)},
        "heap": {"1": node("ListNode", json!({"val": 1, "next": r(2)})), "2": node("ListNode", json!({"val": 2, "next": r(3)})),
                 "3": node("ListNode", json!({"val": 3, "next": null}))}});
    insta::assert_snapshot!(draw(
        "[[view]]\nvar = \"head\"\nas = \"linked\"\npointers = [\"slow\", \"fast\"]",
        frame,
        None,
        50,
        5
    ));
}

#[test]
fn linked_list_cycle() {
    let frame = json!({"line": 4, "vars": {"head": r(1)},
        "heap": {"1": node("ListNode", json!({"val": 1, "next": r(2)})), "2": node("ListNode", json!({"val": 2, "next": r(1)}))}});
    insta::assert_snapshot!(draw("[[view]]\nvar = \"head\"\nas = \"linked\"", frame, None, 50, 5));
}

#[test]
fn binary_tree() {
    let t = |v: i64, l: Value, rt: Value| node("TreeNode", json!({"val": v, "left": l, "right": rt}));
    let frame = json!({"line": 2, "vars": {"root": r(1), "cur": r(3)}, "heap": {
        "1": t(8, r(2), r(3)), "2": t(3, r(4), r(5)), "3": t(10, Value::Null, r(6)),
        "4": t(1, Value::Null, Value::Null), "5": t(6, Value::Null, Value::Null), "6": t(14, Value::Null, Value::Null)}});
    insta::assert_snapshot!(draw("[[view]]\nvar = \"root\"\nas = \"tree\"\npointers = [\"cur\"]", frame, None, 40, 9));
}

#[test]
fn heap_view() {
    let frame = json!({"line": 2, "vars": {"items": list(json!([1, 3, 2, 7, 4, 5])), "i": 4}});
    insta::assert_snapshot!(draw(
        "[[view]]\nvar = \"self.items\"\nas = \"heap\"\npointers = [\"i\"]".replace("self.items", "items").as_str(),
        frame,
        None,
        40,
        11
    ));
}

#[test]
fn trie_view() {
    let n = |kids: Value, end: bool| node("Node", json!({"children": kids, "end": end}));
    let d = |pairs: Vec<(&str, u64)>| {
        let items: Vec<Value> = pairs.iter().map(|(k, id)| json!([k, r(*id)])).collect();
        json!({"k": "dict", "items": items, "len": pairs.len()})
    };
    let frame = json!({"line": 1, "vars": {"root": r(1)}, "heap": {
        "1": n(d(vec![("c", 2)]), false), "2": n(d(vec![("a", 3)]), false),
        "3": n(d(vec![("t", 4), ("r", 5)]), false), "4": n(d(vec![]), true), "5": n(d(vec![]), true)}});
    insta::assert_snapshot!(draw("[[view]]\nvar = \"root\"\nas = \"trie\"", frame, None, 30, 9));
}

#[test]
fn graph_view_with_visited_and_frontier() {
    let adj = |pairs: Vec<(&str, Vec<&str>)>| {
        let items: Vec<Value> = pairs.iter().map(|(k, ns)| json!([k, list(json!(ns))])).collect();
        json!({"k": "dict", "items": items, "len": pairs.len()})
    };
    let frame = json!({"line": 5, "vars": {
        "graph": adj(vec![("A", vec!["B", "C"]), ("B", vec!["D"]), ("C", vec!["D"]), ("D", vec![])]),
        "node": "B", "seen": {"k": "set", "items": ["A", "B", "C"], "len": 3}, "queue": {"k": "deque", "items": ["C"], "len": 1}}});
    insta::assert_snapshot!(draw(
        "[[view]]\nvar = \"graph\"\nas = \"graph\"\npointers = [\"node\", \"seen\", \"queue\"]",
        frame,
        None,
        50,
        9
    ));
}

#[test]
fn map_buckets_stack_queue_value() {
    let frame = json!({"line": 1, "vars": {
        "seen": {"k": "dict", "items": [["a", 1], ["b", 2]], "len": 2},
        "table": list(json!([list(json!([])), list(json!([list(json!(["x", 1]))])), list(json!([]))])),
        "stack": list(json!(["(", "["])), "q": {"k": "deque", "items": [1, 2, 3], "len": 3}, "best": 7}});
    let views = "[[view]]\nvar = \"seen\"\nas = \"map\"\n[[view]]\nvar = \"table\"\nas = \"buckets\"\n[[view]]\nvar = \"stack\"\nas = \"stack\"\n[[view]]\nvar = \"q\"\nas = \"queue\"\n[[view]]\nvar = \"best\"\nas = \"value\"";
    insta::assert_snapshot!(draw(views, frame, None, 50, 26));
}

/// Every challenge's reference trace renders at several steps, in both themes and two sizes, without panicking.
#[test]
fn every_challenge_renders() {
    let lib = Library::load().unwrap();
    let keys: Vec<String> =
        lib.topics.iter().flat_map(|t| t.challenges.iter().map(crate::content::Challenge::key)).collect();
    std::thread::scope(|s| {
        for chunk in keys.chunks(keys.len().div_ceil(8)) {
            s.spawn(move || {
                for key in chunk {
                    for (step, theme, w, h) in [
                        (0, ThemeKind::Stealth, 80, 24),
                        (25, ThemeKind::Game, 140, 40),
                        (usize::MAX, ThemeKind::Stealth, 100, 30),
                    ] {
                        let text = render_challenge(key, step, theme, w, h);
                        assert!(!text.is_empty(), "{key}");
                    }
                }
            });
        }
    });
}

#[test]
fn home_screen_lists_every_topic() {
    let lib = Library::load().unwrap();
    let titles: Vec<String> = lib.topics.iter().map(|t| t.meta.title.clone()).collect();
    let dir = tempfile::tempdir().unwrap();
    let mut app = App::new(lib, Store::new(dir.path().to_path_buf()));
    let mut term = Terminal::new(TestBackend::new(120, 30)).unwrap();
    term.draw(|f| ui::draw(f, &mut app)).unwrap();
    let text = buffer_text(term.backend().buffer());
    println!("{text}");
    for t in titles {
        let head: String = t.chars().take(12).collect();
        assert!(text.contains(&head), "missing {t}");
    }
}

/// Prints sample renders: `cargo test print_samples -- --ignored --nocapture`.
#[test]
#[ignore = "prints sample renders for manual inspection"]
fn print_samples() {
    let keys = std::env::var("ALGOSCOPE_SAMPLES").unwrap_or_else(|_| "trees/inorder-walkthrough".into());
    for key in keys.split(',') {
        let step: usize = std::env::var("ALGOSCOPE_STEP").ok().and_then(|s| s.parse().ok()).unwrap_or(20);
        println!("== {key}\n{}", render_challenge(key, step, ThemeKind::Stealth, 120, 36));
    }
}
