//! Drawing for every screen.

use ratatui::Frame;
use ratatui::layout::{Constraint, Layout, Rect};
use ratatui::style::Modifier;
use ratatui::text::{Line, Span, Text};
use ratatui::widgets::{Block, Borders, Clear, Paragraph, Wrap};

use crate::app::{App, Focus, Screen, Workspace, version_string};
use crate::content::Stage;
use crate::progress::{KeymapKind, TopicState};
use crate::scoring::{self, Grade};
use crate::tui::editor::EditorView;
use crate::tui::theme::Theme;
use crate::tui::viz::{Ctx, VizView, wrap};

pub fn draw(f: &mut Frame, app: &mut App) {
    let area = f.area();
    let [main, status] = Layout::vertical([Constraint::Min(1), Constraint::Length(1)]).areas(area);
    match &app.screen {
        Screen::Home => draw_home(f, app, main),
        Screen::Work(_) => draw_work(f, app, main),
    }
    draw_status(f, app, status);
    if app.help {
        draw_help(f, app, area);
    }
    if app.celebration.is_some() {
        draw_celebration(f, app, area);
    }
}

fn block<'a>(t: &Theme, title: &str, focused: bool) -> Block<'a> {
    Block::default()
        .borders(Borders::ALL)
        .border_style(t.border(focused))
        .title(Span::styled(format!(" {title} "), t.title(focused)))
}

fn draw_status(f: &mut Frame, app: &App, area: Rect) {
    let t = &app.theme;
    let xp = app.progress.xp;
    let mut left = vec![];
    if t.is_game() {
        let level = scoring::level(xp);
        let p = scoring::level_progress(xp);
        let filled = (p * 10.0).round() as usize;
        left.push(Span::styled(format!(" {} ", t.labels.app), t.bold(t.accent)));
        left.push(Span::styled(format!("LV {level} "), t.bold(t.warn)));
        left.push(Span::styled("█".repeat(filled), t.accent()));
        left.push(Span::styled("░".repeat(10 - filled), t.dim()));
        left.push(Span::styled(format!(" {xp} XP "), t.text()));
    } else {
        left.push(Span::styled(format!(" {} {} ", t.labels.app, version_string(xp)), t.dim()));
        left.push(Span::styled(format!("{xp} {} ", t.labels.xp), t.dim()));
    }
    if let Some(ch) = app.current_challenge() {
        let topic = app.lib.topic(&ch.topic).map(|t| t.meta.title.clone()).unwrap_or_default();
        left.push(Span::styled(format!("| {topic} / {} ", ch.meta.title), t.dim()));
    }
    let secs = app.started.elapsed().as_secs();
    let keymap = match app.settings.keymap {
        KeymapKind::Standard => "std",
        KeymapKind::Vim => "vim",
    };
    let right = format!("{:02}:{:02}  {keymap}  F1 help ", secs / 60, secs % 60);
    let mut line = Line::from(left);
    if let Some((msg, _)) = &app.toast {
        line.spans.push(Span::styled(format!("  {msg}"), t.bold(t.warn)));
    }
    let rw = right.len() as u16;
    f.render_widget(Paragraph::new(line), Rect { width: area.width.saturating_sub(rw + 1), ..area });
    if area.width > rw {
        let r = Rect { x: area.right() - rw, width: rw, ..area };
        f.render_widget(Paragraph::new(Span::styled(right, t.dim())), r);
    }
}

// ---- home ---------------------------------------------------------------

fn state_icon(t: &Theme, s: TopicState) -> Span<'static> {
    let (stealth, game, color) = match s {
        TopicState::Locked => ("[-]", "x", t.dim),
        TopicState::Open => ("[ ]", "o", t.accent),
        TopicState::Done => ("[x]", "●", t.good),
        TopicState::Mastered => ("[*]", "◆", t.warn),
    };
    Span::styled(if t.is_game() { game } else { stealth }.to_string(), t.bold(color))
}

fn draw_home(f: &mut Frame, app: &App, area: Rect) {
    let t = &app.theme;
    let [left, right] = Layout::horizontal([Constraint::Percentage(48), Constraint::Percentage(52)]).areas(area);

    let mut lines = Vec::new();
    for (i, prefix) in app.lib.tree_order() {
        let topic = &app.lib.topics[i];
        let state = app.topic_state(i);
        let selected = i == app.topic_idx;
        let name = if t.is_game() { topic.meta.zone.clone() } else { topic.meta.title.clone() };
        let pct = (app.progress.topic_fraction(topic) * 100.0).round() as u32;
        let mut style = if state == TopicState::Locked { t.dim() } else { t.text() };
        if selected {
            style = style.add_modifier(Modifier::REVERSED);
            if !app.home_focus_challenges {
                style = style.add_modifier(Modifier::BOLD);
            }
        }
        lines.push(Line::from(vec![
            Span::styled(prefix, t.dim()),
            state_icon(t, state),
            Span::raw(" "),
            Span::styled(name, style),
            Span::styled(if pct > 0 { format!("  {pct}%") } else { String::new() }, t.dim()),
        ]));
    }
    let row = app.lib.tree_order().iter().position(|(i, _)| *i == app.topic_idx).unwrap_or(0) as u16;
    let scroll = row.saturating_sub(left.height.saturating_sub(4));
    f.render_widget(
        Paragraph::new(lines).scroll((scroll, 0)).block(block(t, t.labels.tree, !app.home_focus_challenges)),
        left,
    );

    let Some(topic) = app.lib.topics.get(app.topic_idx) else { return };
    let state = app.topic_state(app.topic_idx);
    let mut text: Vec<Line> = Vec::new();
    let title =
        if t.is_game() { format!("{}  ({})", topic.meta.zone, topic.meta.title) } else { topic.meta.title.clone() };
    text.push(Line::from(Span::styled(title, t.bold(t.title))));
    for l in wrap(&topic.meta.summary, right.width.saturating_sub(4) as usize) {
        text.push(Line::from(Span::styled(l, t.text())));
    }
    if state == TopicState::Locked {
        let needs: Vec<String> =
            topic.meta.prereqs.iter().filter_map(|p| app.lib.topic(p)).map(|p| p.meta.title.clone()).collect();
        text.push(Line::from(Span::styled(
            format!("{}: needs the build stage of {}", t.labels.locked, needs.join(", ")),
            t.bold(t.warn),
        )));
    }
    text.push(Line::from(""));
    for (ci, ch) in topic.challenges.iter().enumerate() {
        let p = app.progress.get(&ch.key());
        let stage_label = match ch.meta.stage {
            Stage::Watch => t.labels.watch,
            Stage::Build => t.labels.build,
            Stage::Apply => t.labels.apply,
        };
        let mark = if p.done { if t.is_game() { "●" } else { "x" } } else { " " };
        let grade = match p.grade {
            Some(g) if t.is_game() => g.medal().to_string(),
            Some(g) => g.letter().to_string(),
            None => String::new(),
        };
        let gstyle = match p.grade {
            Some(Grade::Gold) => t.bold(t.good),
            Some(Grade::Silver) => t.bold(t.accent),
            _ => t.bold(t.warn),
        };
        let mut style = t.text();
        if app.home_focus_challenges && ci == app.chal_idx {
            style = style.add_modifier(Modifier::REVERSED | Modifier::BOLD);
        }
        text.push(Line::from(vec![
            Span::styled(format!(" [{mark}] "), t.dim()),
            Span::styled(format!("{stage_label:<12}"), t.accent()),
            Span::styled(ch.meta.title.clone(), style),
            Span::styled(format!("  {} {}", ch.meta.xp, t.labels.xp), t.dim()),
            Span::styled(format!("  {grade}"), gstyle),
        ]));
    }
    text.push(Line::from(""));
    text.push(Line::from(Span::styled(
        "enter: start   arrows: move   t: theme   v: vim/standard keys   q: quit",
        t.dim(),
    )));
    let hours = app.progress.seconds_practised as f64 / 3600.0;
    let done: usize =
        app.lib.topics.iter().flat_map(|t| &t.challenges).filter(|c| app.progress.is_done(&c.key())).count();
    text.push(Line::from(Span::styled(
        format!("{done}/{} done   {hours:.1}h practised", app.lib.total_challenges()),
        t.dim(),
    )));
    f.render_widget(
        Paragraph::new(text).wrap(Wrap { trim: false }).block(block(t, t.labels.home, app.home_focus_challenges)),
        right,
    );
}

// ---- workspace ------------------------------------------------------------

fn draw_work(f: &mut Frame, app: &mut App, area: Rect) {
    let App { screen, theme, lib, .. } = app;
    let Screen::Work(ws) = screen else { return };
    let t = &*theme;
    let Some(ch) = lib.challenge(&ws.key) else { return };

    if ws.zoom {
        draw_viz(f, t, ws, &ch.meta.view, &ch.meta.captions, area, true);
        return;
    }
    let left_w = (area.width * 34 / 100).clamp(26, 56);
    let [left, right] = Layout::horizontal([Constraint::Length(left_w), Constraint::Min(30)]).areas(area);
    let out_h = (left.height * 2 / 5).max(6);
    let [problem, output] = Layout::vertical([Constraint::Min(4), Constraint::Length(out_h)]).areas(left);
    let ed_h = (right.height / 2).max(6);
    let [code, viz] = Layout::vertical([Constraint::Length(ed_h), Constraint::Min(6)]).areas(right);

    // problem
    let mut lines: Vec<Line> = Vec::new();
    let stage = match ch.meta.stage {
        Stage::Watch => t.labels.watch,
        Stage::Build => t.labels.build,
        Stage::Apply => t.labels.apply,
    };
    lines.push(Line::from(Span::styled(ch.meta.title.clone(), t.bold(t.title))));
    lines.push(Line::from(vec![
        Span::styled(format!("{stage}  "), t.accent()),
        Span::styled(format!("{} {}  ", ch.meta.xp, t.labels.xp), t.dim()),
        Span::styled(format!("target {}", ch.meta.complexity), t.dim()),
    ]));
    lines.push(Line::from(""));
    let w = problem.width.saturating_sub(2) as usize;
    for l in wrap(ch.meta.statement.trim(), w) {
        lines.push(Line::from(Span::styled(l, t.text())));
    }
    for (i, h) in ch.meta.hints.iter().take(ws.hints_shown).enumerate() {
        lines.push(Line::from(""));
        lines.push(Line::from(Span::styled(format!("{} {}", t.labels.hint, i + 1), t.bold(t.warn))));
        for l in wrap(h, w) {
            lines.push(Line::from(Span::styled(l, t.text())));
        }
    }
    if ws.hints_shown < ch.meta.hints.len() && ch.meta.stage != Stage::Watch {
        lines.push(Line::from(""));
        lines.push(Line::from(Span::styled(
            format!("h: {} ({} left)", t.labels.hint.to_lowercase(), ch.meta.hints.len() - ws.hints_shown),
            t.dim(),
        )));
    }
    f.render_widget(
        Paragraph::new(lines).scroll((ws.problem_scroll, 0)).block(block(t, t.labels.problem, false)),
        problem,
    );

    // output log, newest at the bottom
    let inner_h = output.height.saturating_sub(2) as usize;
    let inner_w = output.width.saturating_sub(2).max(1) as usize;
    let mut rows = 0usize;
    let mut start = ws.log.len();
    while start > 0 {
        let lw: usize = ws.log[start - 1].width().max(1).div_ceil(inner_w);
        if rows + lw > inner_h {
            break;
        }
        rows += lw;
        start -= 1;
    }
    let mut log: Vec<Line> = ws.log[start..].to_vec();
    if let Some((_, mode, at)) = &ws.pending {
        let spin = ["|", "/", "-", "\\"][(at.elapsed().as_millis() / 120 % 4) as usize];
        let what = match mode {
            crate::runner::Mode::Visual => t.labels.run,
            crate::runner::Mode::Score => t.labels.submit,
        };
        log.push(Line::from(Span::styled(format!("{spin} {what} running"), t.accent())));
    }
    f.render_widget(
        Paragraph::new(Text::from(log)).wrap(Wrap { trim: false }).block(block(t, t.labels.output, false)),
        output,
    );

    // editor
    let frame = ws.visual.as_ref().and_then(|v| v.frames.get(ws.timeline.pos));
    let (tw, th) = EditorView::text_area(code, ws.editor.lines.len());
    ws.editor.ensure_visible(th as usize, tw as usize);
    if frame.is_some()
        && ws.focus == Focus::Viz
        && let Some(fr) = frame
    {
        ws.editor.reveal_line(fr.line as usize);
    }
    let title = if ch.meta.stage == Stage::Watch { "reference.py".to_string() } else { "solution.py".to_string() };
    let view = EditorView {
        ed: &ws.editor,
        theme: t,
        focused: ws.focus == Focus::Editor,
        title,
        exec_line: frame.map(|f| f.line),
        prev_line: frame.and_then(|f| f.prev),
        error_line: ws.error_line,
    };
    f.render_widget(view, code);

    draw_viz(f, t, ws, &ch.meta.view, &ch.meta.captions, viz, false);
}

fn draw_viz(
    f: &mut Frame,
    t: &Theme,
    ws: &Workspace,
    views: &[crate::content::ViewSpec],
    captions: &[crate::content::Caption],
    area: Rect,
    zoomed: bool,
) {
    let focused = ws.focus == Focus::Viz;
    let tl = &ws.timeline;
    let mut title = t.labels.trace.to_string();
    let mut bottom = Vec::new();
    if let Some(v) = &ws.visual
        && !v.frames.is_empty()
    {
        title = format!("{}  step {}/{}", t.labels.trace, tl.pos + 1, tl.len);
        let state = if tl.playing { "playing" } else { "paused" };
        bottom.push(Span::styled(format!(" {state}  speed {}/7 ", tl.speed + 1), t.dim()));
        if focused {
            bottom.push(Span::styled(" space play  <- -> step  [ ] speed  z zoom ", t.dim()));
        }
    }
    if zoomed {
        title.push_str("  (z to restore)");
    }
    let b = block(t, &title, focused).title_bottom(Line::from(bottom));
    let inner = b.inner(area);
    f.render_widget(b, area);
    let Some(v) = &ws.visual else {
        let msg = if ws.pending.is_some() { "tracing..." } else { "Ctrl+E to trace your code on the example input" };
        f.render_widget(Paragraph::new(Span::styled(msg, t.dim())), inner);
        return;
    };
    let Some(frame) = v.frames.get(tl.pos) else {
        let msg = if v.error.is_some() { "no steps recorded: see the output" } else { "no steps recorded" };
        f.render_widget(Paragraph::new(Span::styled(msg, t.dim())), inner);
        return;
    };
    let prev = if tl.pos > 0 { v.frames.get(tl.pos - 1) } else { None };
    let tween_ticks = (crate::runner::trace::SPEEDS[tl.speed] / 33).clamp(1, 8) as f64;
    let tween = (f64::from(tl.since_change) / tween_ticks).min(1.0);
    // most recent caption reached so far
    let caption = if captions.is_empty() {
        None
    } else {
        v.frames[..=tl.pos]
            .iter()
            .rev()
            .find_map(|fr| captions.iter().find(|c| c.line == fr.line))
            .map(|c| c.text.as_str())
    };
    let viz = VizView { ctx: Ctx { theme: t, frame, prev, tween }, views, caption };
    viz.render(inner, f.buffer_mut());
}

// ---- overlays ---------------------------------------------------------------

fn centered(area: Rect, w: u16, h: u16) -> Rect {
    let w = w.min(area.width);
    let h = h.min(area.height);
    Rect { x: area.x + (area.width - w) / 2, y: area.y + (area.height - h) / 2, width: w, height: h }
}

fn draw_help(f: &mut Frame, app: &App, area: Rect) {
    let t = &app.theme;
    let rows: &[(&str, &str)] = &[
        ("Ctrl+E", "trace your code on the example input"),
        ("Ctrl+T", "run the full suite and profile efficiency"),
        ("Esc / Tab", "editor -> trace pane (vim: Esc from normal mode)"),
        ("Enter / i", "trace pane -> editor"),
        ("space", "play / pause the trace"),
        ("<- ->  , .", "step one frame;  up/down: 10 frames"),
        ("[ ]", "slower / faster"),
        ("g / G", "first / last frame"),
        ("z", "zoom the trace pane"),
        ("h", "reveal a hint (costs 10% of the reward)"),
        ("n", "next challenge in the topic"),
        ("r r", "reset code to the starter"),
        ("q / Ctrl+Q", "back to the tree (drafts autosave)"),
        ("F2 / t", "switch stealth / game theme"),
        ("v", "switch standard / vim keys (outside the editor)"),
        ("vim", ":w save  :run  :submit  :q"),
    ];
    let mut lines = vec![Line::from(Span::styled("keys", t.bold(t.title))), Line::from("")];
    for (k, d) in rows {
        lines.push(Line::from(vec![Span::styled(format!("{k:<12}"), t.bold(t.accent)), Span::styled(*d, t.text())]));
    }
    lines.push(Line::from(""));
    lines.push(Line::from(Span::styled("any key closes", t.dim())));
    let r = centered(area, 66, lines.len() as u16 + 2);
    f.render_widget(Clear, r);
    f.render_widget(Paragraph::new(lines).block(block(t, "help", true)), r);
}

fn draw_celebration(f: &mut Frame, app: &App, area: Rect) {
    let t = &app.theme;
    let Some(c) = &app.celebration else { return };
    let ms = c.started.elapsed().as_millis() as u64;
    let w = 46u16;
    let h = 9 + c.lines.len() as u16;
    let r = centered(area, w, h);
    f.render_widget(Clear, r);
    // sparkle field that drifts with time
    let sparks = ["*", "+", ".", "·", "x"];
    let colors = [t.accent, t.accent2, t.warn, t.good];
    let buf = f.buffer_mut();
    for i in 0..(u64::from(w) * 2) {
        let seed = i.wrapping_mul(2_654_435_761) ^ (ms / 90);
        let x = r.x + (seed % u64::from(w)) as u16;
        let y = r.y + ((seed / 7 + ms / 160) % u64::from(h)) as u16;
        if (seed >> 5).is_multiple_of(3) {
            let s = sparks[(seed % sparks.len() as u64) as usize];
            buf.set_string(x, y, s, ratatui::style::Style::default().fg(colors[(seed % 4) as usize]));
        }
    }
    let reveal = ((ms / 40) as usize).min(c.title.len());
    let title: String = c.title.chars().take(reveal).collect();
    let mut lines = vec![
        Line::from(""),
        Line::from(""),
        Line::from(Span::styled(format!("{:^w$}", spaced(&title), w = w as usize - 2), t.bold(t.warn))),
    ];
    lines.push(Line::from(""));
    for l in &c.lines {
        lines.push(Line::from(Span::styled(format!("{:^w$}", l, w = w as usize - 2), t.bold(t.accent))));
    }
    let inner = Rect { x: r.x + 1, y: r.y + 1, width: r.width - 2, height: r.height - 2 };
    f.render_widget(Paragraph::new(lines), inner);
    f.render_widget(Block::default().borders(Borders::ALL).border_style(t.bold(colors[(ms / 200 % 4) as usize])), r);
}

fn spaced(s: &str) -> String {
    s.chars().map(|c| c.to_string()).collect::<Vec<_>>().join(" ")
}
