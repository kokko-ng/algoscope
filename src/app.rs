//! Application state and update logic (Elm style: events in, state changes, ui.rs draws).

use std::time::{Duration, Instant};

use ratatui::crossterm::event::{KeyCode, KeyEvent, KeyModifiers};
use ratatui::style::Style;
use ratatui::text::{Line, Span};

use crate::content::{Challenge, Library, Stage};
use crate::progress::{KeymapKind, Progress, Settings, Store, ThemeKind, TopicState};
use crate::runner::trace::{ScoreResult, Timeline, VisualResult};
use crate::runner::{Done, Mode, Outcome, Worker};
use crate::scoring::{self, Grade, Report};
use crate::tui::editor::{Action, Editor};
use crate::tui::theme::Theme;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Focus {
    Editor,
    Viz,
}

pub struct Workspace {
    pub key: String,
    pub editor: Editor,
    pub focus: Focus,
    pub visual: Option<VisualResult>,
    pub timeline: Timeline,
    pub report: Option<Report>,
    pub pending: Option<(u64, Mode, Instant)>,
    pub log: Vec<Line<'static>>,
    pub hints_shown: usize,
    pub zoom: bool,
    pub error_line: Option<u32>,
    pub problem_scroll: u16,
    pub confirm_reset: bool,
    last_autosave: Instant,
}

pub enum Screen {
    Home,
    Work(Box<Workspace>),
}

pub struct Celebration {
    pub title: String,
    pub lines: Vec<String>,
    pub started: Instant,
}

pub struct App {
    pub lib: Library,
    pub store: Store,
    pub progress: Progress,
    pub settings: Settings,
    pub theme: Theme,
    pub worker: Worker,
    pub screen: Screen,
    pub topic_idx: usize,
    pub chal_idx: usize,
    pub home_focus_challenges: bool,
    pub help: bool,
    pub celebration: Option<Celebration>,
    pub toast: Option<(String, Instant)>,
    pub started: Instant,
    pub quit: bool,
    pub ticks: u64,
    saved_seconds: u64,
}

impl App {
    pub fn new(lib: Library, store: Store) -> App {
        let progress = store.load_progress();
        let settings = store.load_settings();
        let theme = Theme::new(settings.theme);
        let mut app = App {
            lib,
            store,
            progress,
            settings,
            theme,
            worker: Worker::spawn(),
            screen: Screen::Home,
            topic_idx: 0,
            chal_idx: 0,
            home_focus_challenges: false,
            help: false,
            celebration: None,
            toast: None,
            started: Instant::now(),
            quit: false,
            ticks: 0,
            saved_seconds: 0,
        };
        // start on the topic of the last challenge played
        if let Some(last) = app.progress.last_challenge.clone() {
            if let Some((topic, _)) = last.split_once('/') {
                if let Some(i) = app.lib.topics.iter().position(|t| t.meta.id == topic) {
                    app.topic_idx = i;
                }
            }
        }
        app
    }

    pub fn toast(&mut self, msg: impl Into<String>) {
        self.toast = Some((msg.into(), Instant::now()));
    }

    pub fn save(&mut self) {
        let elapsed = self.started.elapsed().as_secs();
        self.progress.seconds_practised += elapsed - self.saved_seconds;
        self.saved_seconds = elapsed;
        if let Err(e) = self.store.save_progress(&self.progress) {
            self.toast(format!("could not save progress: {e}"));
        }
    }

    fn save_settings(&mut self) {
        if let Err(e) = self.store.save_settings(&self.settings) {
            self.toast(format!("could not save settings: {e}"));
        }
    }

    pub fn toggle_theme(&mut self) {
        self.settings.theme = match self.settings.theme {
            ThemeKind::Stealth => ThemeKind::Game,
            ThemeKind::Game => ThemeKind::Stealth,
        };
        self.theme = Theme::new(self.settings.theme);
        if self.settings.theme == ThemeKind::Stealth {
            self.celebration = None;
        }
        self.save_settings();
    }

    pub fn toggle_keymap(&mut self) {
        self.settings.keymap = match self.settings.keymap {
            KeymapKind::Standard => KeymapKind::Vim,
            KeymapKind::Vim => KeymapKind::Standard,
        };
        if let Screen::Work(ws) = &mut self.screen {
            ws.editor.set_keymap(self.settings.keymap);
        }
        let name = match self.settings.keymap {
            KeymapKind::Standard => "standard",
            KeymapKind::Vim => "vim",
        };
        self.toast(format!("keymap: {name}"));
        self.save_settings();
    }

    pub fn topic_state(&self, idx: usize) -> TopicState {
        self.progress.topic_state(&self.lib, &self.lib.topics[idx])
    }

    pub fn current_challenge(&self) -> Option<&Challenge> {
        match &self.screen {
            Screen::Work(ws) => self.lib.challenge(&ws.key),
            Screen::Home => None,
        }
    }

    // ---- opening challenges -------------------------------------------

    pub fn open(&mut self, key: &str) {
        let Some(ch) = self.lib.challenge(key).cloned() else { return };
        self.close_workspace();
        let watch = ch.meta.stage == Stage::Watch;
        let text = if watch {
            ch.reference.clone()
        } else {
            self.progress.drafts.get(key).cloned().unwrap_or_else(|| ch.starter.clone())
        };
        let mut editor = Editor::new(&text, self.settings.keymap);
        editor.readonly = watch;
        let mut ws = Workspace {
            key: key.to_string(),
            editor,
            focus: if watch { Focus::Viz } else { Focus::Editor },
            visual: None,
            timeline: Timeline::new(0, self.settings.speed),
            report: None,
            pending: None,
            log: Vec::new(),
            hints_shown: self.progress.get(key).hints_used as usize,
            zoom: false,
            error_line: None,
            problem_scroll: 0,
            confirm_reset: false,
            last_autosave: Instant::now(),
        };
        let t = &self.theme;
        let intro = match ch.meta.stage {
            Stage::Watch => "Step through the reference. Space plays or pauses, left/right step, [ ] change speed.",
            _ => "Ctrl+E traces your code on the example. Ctrl+T runs the full suite and profiles it.",
        };
        ws.log.push(Line::from(Span::styled(intro.to_string(), t.dim())));
        if ch.meta.stage == Stage::Watch {
            let id = self.worker.submit(Mode::Visual, &ch, ch.reference.clone());
            ws.pending = Some((id, Mode::Visual, Instant::now()));
        }
        self.progress.last_challenge = Some(key.to_string());
        self.screen = Screen::Work(Box::new(ws));
    }

    fn close_workspace(&mut self) {
        if let Screen::Work(ws) = &mut self.screen {
            if !ws.editor.readonly {
                self.progress.drafts.insert(ws.key.clone(), ws.editor.text());
            }
            self.settings.speed = ws.timeline.speed;
        }
        self.save();
        self.save_settings();
    }

    pub fn go_home(&mut self) {
        if let Screen::Work(ws) = &self.screen {
            let key = ws.key.clone();
            if let Some((topic, id)) = key.split_once('/') {
                if let Some(ti) = self.lib.topics.iter().position(|t| t.meta.id == topic) {
                    self.topic_idx = ti;
                    self.chal_idx = self.lib.topics[ti].challenges.iter().position(|c| c.meta.id == id).unwrap_or(0);
                }
            }
        }
        self.close_workspace();
        self.screen = Screen::Home;
    }

    fn open_next(&mut self) {
        let Some(ch) = self.current_challenge() else { return };
        let topic = self.lib.topic(&ch.topic).cloned();
        let id = ch.meta.id.clone();
        if let Some(topic) = topic {
            let i = topic.challenges.iter().position(|c| c.meta.id == id).unwrap_or(0);
            if let Some(next) = topic.challenges.get(i + 1) {
                let key = next.key();
                self.open(&key);
                return;
            }
        }
        self.toast("topic complete: pick the next one from the tree");
        self.go_home();
    }

    // ---- running ------------------------------------------------------

    fn start_job(&mut self, mode: Mode) {
        let Screen::Work(ws) = &mut self.screen else { return };
        let Some(ch) = self.lib.challenge(&ws.key) else { return };
        if ch.meta.stage == Stage::Watch && mode == Mode::Score {
            return;
        }
        let code = ws.editor.text();
        if !ws.editor.readonly {
            self.progress.drafts.insert(ws.key.clone(), code.clone());
        }
        let id = self.worker.submit(mode, ch, code);
        ws.pending = Some((id, mode, Instant::now()));
        ws.error_line = None;
        let label = match mode {
            Mode::Visual => self.theme.labels.run,
            Mode::Score => self.theme.labels.submit,
        };
        ws.log.push(Line::from(Span::styled(format!("{label}..."), self.theme.dim())));
        self.save();
    }

    pub fn poll_worker(&mut self) {
        while let Ok(done) = self.worker.rx.try_recv() {
            self.on_done(done);
        }
    }

    fn on_done(&mut self, done: Done) {
        let Screen::Work(ws) = &mut self.screen else { return };
        if ws.pending.as_ref().map(|p| p.0) != Some(done.id) || ws.key != done.key {
            return;
        }
        ws.pending = None;
        let t = &self.theme;
        let mut lines: Vec<Line<'static>> = Vec::new();
        let elapsed = format!("{:.2}s", done.elapsed.as_secs_f64());
        match done.result {
            Err(msg) => {
                for l in msg.lines() {
                    lines.push(Line::from(Span::styled(l.to_string(), t.bold(t.bad))));
                }
            }
            Ok(Outcome::Visual(v)) => {
                if let Some(err) = &v.error {
                    ws.error_line = err.line;
                    for l in err.text.lines() {
                        lines.push(Line::from(Span::styled(l.to_string(), t.bold(t.bad))));
                    }
                }
                let n = v.frames.len();
                let mut summary = vec![Span::styled(format!("trace: {n} steps"), t.text())];
                if v.truncated {
                    summary.push(Span::styled("  (cut off: possible infinite loop)", t.bold(t.warn)));
                }
                summary.push(Span::styled(format!("  {elapsed}"), t.dim()));
                lines.push(Line::from(summary));
                let watching = ws.editor.readonly;
                if !v.input.is_empty() && !watching {
                    lines.push(Line::from(vec![Span::styled("input    ", t.dim()), Span::raw(v.input.clone())]));
                }
                match (v.passed, &v.got) {
                    _ if watching => {}
                    (Some(true), Some(got)) => lines.push(Line::from(vec![
                        Span::styled("output   ", t.dim()),
                        Span::styled(got.clone(), t.bold(t.good)),
                        Span::styled("  ok", t.good_style()),
                    ])),
                    (Some(false), Some(got)) => {
                        lines.push(Line::from(vec![Span::styled("output   ", t.dim()), Span::styled(got.clone(), t.bold(t.bad))]));
                        lines.push(Line::from(vec![Span::styled("expected ", t.dim()), Span::raw(v.expected.clone())]));
                    }
                    _ => {}
                }
                push_stdout(&mut lines, &v.stdout, t);
                ws.timeline = Timeline::new(n, ws.timeline.speed);
                if n > 0 {
                    ws.focus = Focus::Viz;
                }
                ws.visual = Some(v);
            }
            Ok(Outcome::Score(s)) => {
                let award = score_lines(&mut lines, &s, t, &elapsed);
                if let Some((report, base_ok)) = award {
                    ws.report = Some(report.clone());
                    let key = ws.key.clone();
                    if base_ok {
                        self.finish_challenge(&key, Some(report), lines);
                        return;
                    }
                }
                if let Some(err) = &s.error {
                    ws.error_line = err.line;
                }
            }
        }
        ws.log.extend(lines);
    }

    /// Record completion, award XP and celebrate.
    fn finish_challenge(&mut self, key: &str, report: Option<Report>, mut lines: Vec<Line<'static>>) {
        let Some(ch) = self.lib.challenge(key) else { return };
        let base = ch.meta.xp;
        let hints = self.progress.get(key).hints_used;
        let grade = report.as_ref().map(|r| r.grade);
        let earned = scoring::award(base, grade, hints);
        let level_before = scoring::level(self.progress.xp);
        let delta = self.progress.complete(key, earned, grade, report.as_ref().map(|r| r.ratio));
        let level_after = scoring::level(self.progress.xp);
        let t = &self.theme;
        let xp = t.labels.xp;
        if delta > 0 {
            lines.push(Line::from(Span::styled(format!("+{delta} {xp}"), t.bold(t.accent))));
        } else {
            lines.push(Line::from(Span::styled(format!("no new {xp} (best result already recorded)"), t.dim())));
        }
        lines.push(Line::from(Span::styled("n: next   q: back to the tree", t.dim())));
        if t.celebrate && delta > 0 {
            let mut body = vec![format!("+{delta} {xp}")];
            if let Some(g) = grade {
                body.insert(0, format!("{} efficiency", g.medal()));
            }
            let title = if level_after > level_before {
                body.push(format!("LEVEL {level_after} REACHED"));
                "LEVEL UP".to_string()
            } else {
                match ch.meta.stage {
                    Stage::Watch => "LORE LEARNED".into(),
                    Stage::Build => "FORGED".into(),
                    Stage::Apply => "TRIAL CLEARED".into(),
                }
            };
            self.celebration = Some(Celebration { title, lines: body, started: Instant::now() });
        } else if level_after > level_before {
            self.toast(format!("version bump: {}", version_string(self.progress.xp)));
        }
        if let Screen::Work(ws) = &mut self.screen {
            ws.log.extend(lines);
        }
        self.save();
    }

    // ---- ticking --------------------------------------------------------

    pub fn tick(&mut self, elapsed: Duration) {
        self.ticks += 1;
        self.poll_worker();
        if self.toast.as_ref().is_some_and(|(_, at)| at.elapsed() > Duration::from_secs(3)) {
            self.toast = None;
        }
        if self.celebration.as_ref().is_some_and(|c| c.started.elapsed() > Duration::from_millis(3500)) {
            self.celebration = None;
        }
        let mut finished_watch = None;
        if let Screen::Work(ws) = &mut self.screen {
            ws.timeline.tick(elapsed.as_millis() as u64);
            if let Some(frame) = ws.visual.as_ref().and_then(|v| v.frames.get(ws.timeline.pos)) {
                ws.editor.reveal_line(frame.line as usize);
            }
            if ws.editor.readonly
                && ws.timeline.at_end()
                && ws.visual.as_ref().is_some_and(|v| !v.frames.is_empty() && v.error.is_none())
                && !self.progress.is_done(&ws.key)
            {
                finished_watch = Some(ws.key.clone());
            }
            if ws.editor.dirty && ws.last_autosave.elapsed() > Duration::from_secs(5) {
                ws.last_autosave = Instant::now();
                ws.editor.dirty = false;
                self.progress.drafts.insert(ws.key.clone(), ws.editor.text());
                self.save();
            }
        }
        if let Some(key) = finished_watch {
            self.finish_challenge(&key, None, Vec::new());
        }
    }

    // ---- input ----------------------------------------------------------

    pub fn on_paste(&mut self, text: &str) {
        if let Screen::Work(ws) = &mut self.screen {
            if ws.focus == Focus::Editor {
                ws.editor.paste(text);
            }
        }
    }

    pub fn on_key(&mut self, key: KeyEvent) {
        if self.celebration.is_some() {
            self.celebration = None;
            return;
        }
        if self.help {
            self.help = false;
            return;
        }
        if key.code == KeyCode::F(2) {
            self.toggle_theme();
            return;
        }
        if key.code == KeyCode::F(1) {
            self.help = true;
            return;
        }
        if key.modifiers.contains(KeyModifiers::CONTROL) && key.code == KeyCode::Char('c') {
            // Ctrl+C copies inside the editor; elsewhere it quits
            let in_editor = matches!(&self.screen, Screen::Work(ws) if ws.focus == Focus::Editor);
            if !in_editor {
                self.quit_app();
                return;
            }
        }
        match self.screen {
            Screen::Home => self.home_key(key),
            Screen::Work(_) => self.work_key(key),
        }
    }

    pub fn quit_app(&mut self) {
        self.close_workspace();
        self.quit = true;
    }

    fn home_key(&mut self, key: KeyEvent) {
        let n_topics = self.lib.topics.len();
        let n_ch = self.lib.topics.get(self.topic_idx).map_or(0, |t| t.challenges.len());
        match key.code {
            KeyCode::Char('q') | KeyCode::Esc => self.quit_app(),
            KeyCode::Char('?') => self.help = true,
            KeyCode::Char('t') => self.toggle_theme(),
            KeyCode::Char('v') => self.toggle_keymap(),
            KeyCode::Up | KeyCode::Char('k') => {
                if self.home_focus_challenges {
                    self.chal_idx = self.chal_idx.saturating_sub(1);
                } else {
                    self.topic_idx = self.topic_idx.saturating_sub(1);
                    self.chal_idx = 0;
                }
            }
            KeyCode::Down | KeyCode::Char('j') => {
                if self.home_focus_challenges {
                    self.chal_idx = (self.chal_idx + 1).min(n_ch.saturating_sub(1));
                } else {
                    self.topic_idx = (self.topic_idx + 1).min(n_topics.saturating_sub(1));
                    self.chal_idx = 0;
                }
            }
            KeyCode::Right | KeyCode::Char('l') | KeyCode::Tab => self.home_focus_challenges = true,
            KeyCode::Left | KeyCode::Char('h') | KeyCode::BackTab => self.home_focus_challenges = false,
            KeyCode::Enter | KeyCode::Char(' ') => {
                if self.topic_state(self.topic_idx) == TopicState::Locked {
                    let topic = &self.lib.topics[self.topic_idx];
                    let needs: Vec<String> = topic
                        .meta
                        .prereqs
                        .iter()
                        .filter_map(|p| self.lib.topic(p))
                        .map(|t| t.meta.title.clone())
                        .collect();
                    self.toast(format!("{}: finish the build stage of {}", self.theme.labels.locked, needs.join(", ")));
                    return;
                }
                let topic = &self.lib.topics[self.topic_idx];
                let key = if self.home_focus_challenges {
                    topic.challenges.get(self.chal_idx).map(Challenge::key)
                } else {
                    self.progress.next_in_topic(topic)
                };
                if let Some(key) = key {
                    self.open(&key);
                }
            }
            _ => {}
        }
    }

    fn work_key(&mut self, key: KeyEvent) {
        // Esc followed quickly by a key arrives as Alt+key; split it back into the two presses
        if let (KeyCode::Char(c), true) = (key.code, key.modifiers.contains(KeyModifiers::ALT)) {
            if matches!(&self.screen, Screen::Work(ws) if ws.focus == Focus::Editor) {
                self.work_key(KeyEvent::new(KeyCode::Esc, KeyModifiers::NONE));
                self.work_key(KeyEvent::new(KeyCode::Char(c), key.modifiers - KeyModifiers::ALT));
                return;
            }
        }
        let ctrl = key.modifiers.contains(KeyModifiers::CONTROL);
        let Screen::Work(ws) = &mut self.screen else { return };
        if ws.focus == Focus::Editor {
            let action = ws.editor.handle_key(key);
            match action {
                Action::Leave => ws.focus = Focus::Viz,
                Action::Run => self.start_job(Mode::Visual),
                Action::Submit => self.start_job(Mode::Score),
                Action::Quit => self.go_home(),
                Action::Save => {
                    let text = ws.editor.text();
                    let k = ws.key.clone();
                    ws.editor.message = Some("draft saved".into());
                    self.progress.drafts.insert(k, text);
                    self.save();
                }
                Action::Unhandled if key.code == KeyCode::Tab || key.code == KeyCode::BackTab => {
                    ws.focus = Focus::Viz;
                }
                Action::None | Action::Unhandled => {}
            }
            return;
        }
        if ctrl {
            match key.code {
                KeyCode::Char('e') => self.start_job(Mode::Visual),
                KeyCode::Char('t') => self.start_job(Mode::Score),
                KeyCode::Char('q') => self.go_home(),
                _ => {}
            }
            return;
        }
        let reset_armed = std::mem::take(&mut ws.confirm_reset);
        match key.code {
            KeyCode::Char(' ') => ws.timeline.toggle(),
            KeyCode::Right | KeyCode::Char('.') | KeyCode::Char('l') => ws.timeline.step(1),
            KeyCode::Left | KeyCode::Char(',') => ws.timeline.step(-1),
            KeyCode::Down | KeyCode::Char('J') => ws.timeline.step(10),
            KeyCode::Up | KeyCode::Char('K') => ws.timeline.step(-10),
            KeyCode::Char(']') => ws.timeline.faster(),
            KeyCode::Char('[') => ws.timeline.slower(),
            KeyCode::Home | KeyCode::Char('g') => ws.timeline.step(-(ws.timeline.len as i64)),
            KeyCode::End | KeyCode::Char('G') => ws.timeline.step(ws.timeline.len as i64),
            KeyCode::Char('z') => ws.zoom = !ws.zoom,
            KeyCode::PageDown => ws.problem_scroll = ws.problem_scroll.saturating_add(3),
            KeyCode::PageUp => ws.problem_scroll = ws.problem_scroll.saturating_sub(3),
            KeyCode::Enter | KeyCode::Char('i') | KeyCode::Char('e') | KeyCode::Tab | KeyCode::BackTab => {
                ws.focus = Focus::Editor;
                ws.zoom = false;
            }
            KeyCode::Char('h') => self.reveal_hint(),
            KeyCode::Char('n') => self.open_next(),
            KeyCode::Char('t') => self.toggle_theme(),
            KeyCode::Char('v') => self.toggle_keymap(),
            KeyCode::Char('?') => self.help = true,
            KeyCode::Char(':') if self.settings.keymap == KeymapKind::Vim => {
                ws.focus = Focus::Editor;
                ws.editor.vim.mode = crate::tui::editor::VimMode::Command;
                ws.editor.vim.cmdline.clear();
            }
            KeyCode::Char('q') | KeyCode::Esc => self.go_home(),
            KeyCode::Char('r') => {
                if ws.editor.readonly {
                    ws.timeline.seek(0);
                    ws.timeline.playing = true;
                } else if reset_armed {
                    let starter = self.lib.challenge(&ws.key).map(|c| c.starter.clone()).unwrap_or_default();
                    ws.editor.set_text(&starter);
                    ws.editor.dirty = true;
                    ws.log.push(Line::from(Span::styled("code reset to the starter", self.theme.dim())));
                } else {
                    ws.confirm_reset = true;
                    ws.log.push(Line::from(Span::styled(
                        "press r again to reset your code to the starter",
                        self.theme.bold(self.theme.warn),
                    )));
                }
            }
            _ => {}
        }
    }

    fn reveal_hint(&mut self) {
        let Screen::Work(ws) = &mut self.screen else { return };
        let Some(ch) = self.lib.challenge(&ws.key) else { return };
        if ws.hints_shown >= ch.meta.hints.len() {
            ws.log.push(Line::from(Span::styled("no more hints for this one", self.theme.dim())));
            return;
        }
        ws.hints_shown += 1;
        if self.progress.get(&ws.key).hints_used < ws.hints_shown as u32 && !self.progress.is_done(&ws.key) {
            self.progress.use_hint(&ws.key);
        }
        ws.log.push(Line::from(Span::styled(
            format!("{} {} revealed (-10% {} on this one)", self.theme.labels.hint, ws.hints_shown, self.theme.labels.xp),
            self.theme.dim(),
        )));
    }
}

trait GoodStyle {
    fn good_style(&self) -> Style;
}

impl GoodStyle for Theme {
    fn good_style(&self) -> Style {
        Style::default().fg(self.good)
    }
}

fn push_stdout(lines: &mut Vec<Line<'static>>, stdout: &str, t: &Theme) {
    let out: Vec<&str> = stdout.lines().collect();
    if out.is_empty() {
        return;
    }
    lines.push(Line::from(Span::styled("stdout", t.dim())));
    for l in out.iter().take(12) {
        lines.push(Line::from(Span::raw(format!("  {l}"))));
    }
    if out.len() > 12 {
        lines.push(Line::from(Span::styled(format!("  ... {} more lines", out.len() - 12), t.dim())));
    }
}

fn fmt_num(n: u64) -> String {
    let s = n.to_string();
    let mut out = String::new();
    for (i, c) in s.chars().enumerate() {
        if i > 0 && (s.len() - i) % 3 == 0 {
            out.push(',');
        }
        out.push(c);
    }
    out
}

/// Describe a score result. Returns the grade report and whether the challenge is complete.
fn score_lines(lines: &mut Vec<Line<'static>>, s: &ScoreResult, t: &Theme, elapsed: &str) -> Option<(Report, bool)> {
    if let Some(err) = &s.error {
        for l in err.text.lines() {
            lines.push(Line::from(Span::styled(l.to_string(), t.bold(t.bad))));
        }
        if let Some(input) = &err.input {
            lines.push(Line::from(vec![Span::styled("input    ", t.dim()), Span::raw(input.clone())]));
        }
    }
    let ok = s.total > 0 && s.passed == s.total && s.error.is_none();
    let style = if ok { t.bold(t.good) } else { t.bold(t.bad) };
    let failed = s.total.saturating_sub(s.passed);
    let mut head = vec![Span::styled(format!("{} passed", s.passed), style)];
    if failed > 0 {
        head.push(Span::styled(format!(", {failed} failed"), t.bold(t.bad)));
    }
    head.push(Span::styled(format!("  of {} cases  {elapsed}", s.total), t.dim()));
    lines.push(Line::from(head));
    for f in &s.failures {
        lines.push(Line::from(vec![Span::styled("input    ", t.dim()), Span::raw(f.input.clone())]));
        lines.push(Line::from(vec![Span::styled("expected ", t.dim()), Span::raw(f.expected.clone())]));
        lines.push(Line::from(vec![Span::styled("got      ", t.dim()), Span::styled(f.got.clone(), t.bold(t.bad))]));
    }
    push_stdout(lines, &s.stdout, t);
    if !ok {
        return None;
    }
    let steps = s.steps.as_ref()?;
    let report = scoring::grade(steps, s.step_limit_hit.is_some());
    let g = report.grade;
    let gstyle = match g {
        Grade::Gold => t.bold(t.good),
        Grade::Silver => t.bold(t.accent),
        Grade::Bronze => t.bold(t.warn),
    };
    let grade_label = if t.is_game() { g.medal().to_string() } else { format!("grade {}", g.letter()) };
    lines.push(Line::from(vec![
        Span::styled(format!("cost {} steps", fmt_num(report.user_steps)), t.text()),
        Span::styled(format!(" (ref {}) at n={}  ", fmt_num(report.ref_steps), report.n), t.dim()),
        Span::styled(grade_label, gstyle),
    ]));
    lines.push(Line::from(Span::styled(
        format!(
            "growth {} {}   reference {} {}",
            format_args!("{:.2}", report.user_slope),
            scoring::growth_name(report.user_slope),
            format_args!("{:.2}", report.ref_slope),
            scoring::growth_name(report.ref_slope)
        ),
        t.dim(),
    )));
    if let Some(n) = s.step_limit_hit {
        lines.push(Line::from(Span::styled(format!("stopped measuring at n={n}: step budget exceeded"), t.bold(t.warn))));
    }
    Some((report, true))
}

/// The stealth theme shows the level as a version number.
pub fn version_string(xp: u64) -> String {
    let level = scoring::level(xp);
    let minor = (scoring::level_progress(xp) * 10.0).floor() as u32;
    format!("0.{level}.{minor}")
}
