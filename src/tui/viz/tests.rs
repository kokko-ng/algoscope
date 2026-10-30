//! Snapshot tests for the visualisers and the main screens, rendered to a test buffer.

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
        ws.timeline = crate::runner::trace::Timeline::new(n, 3);
        ws.timeline.playing = false;
        ws.timeline.seek(step.min(n.saturating_sub(1)));
        ws.timeline.since_change = 100;
        ws.focus = crate::app::Focus::Viz;
    }
    let mut term = Terminal::new(TestBackend::new(w, h)).unwrap();
    term.draw(|f| ui::draw(f, &mut app)).unwrap();
    let text = buffer_text(term.backend().buffer());
    // the session clock changes between runs
    text.lines().map(|l| if l.contains("help") && l.contains(':') { l.split("  ").next().unwrap_or("").to_string() } else { l.to_string() }).collect::<Vec<_>>().join("\n")
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
