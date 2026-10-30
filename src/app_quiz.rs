//! The system design screen: walkthrough diagrams and scenario quizzes.

use std::time::Duration;

use ratatui::crossterm::event::{KeyCode, KeyEvent, KeyModifiers};
use ratatui::text::{Line, Span};

use crate::app::{App, Screen};
use crate::content::{Challenge, DiagramStep, Stage};
use crate::quiz::{self, Answer, MAX_ATTEMPTS};
use crate::runner::trace::Timeline;
use crate::tui::viz::diagram::FRAMES_PER_STEP;

/// Diagrams play faster than code traces: about one second per step at the default speed.
const DIAGRAM_SPEED: usize = 5;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum QuizPhase {
    Answering,
    /// A wrong answer with attempts left.
    Wrong,
    Correct,
    /// Out of attempts: the answer is shown.
    Revealed,
    Done,
}

pub struct QuizWs {
    pub key: String,
    /// Index of the current question.
    pub q: usize,
    pub phase: QuizPhase,
    /// Selected choice for multiple-choice questions.
    pub selected: usize,
    /// Typed text for number questions.
    pub input: String,
    pub attempts: Vec<u8>,
    pub first_try: Vec<bool>,
    pub hint_shown: Vec<bool>,
    /// Steps the diagram is animating now, and the playback position over them.
    pub playing: Vec<DiagramStep>,
    pub timeline: Timeline,
    /// Whether `playing` loops (the scene before an answer) or plays once (an explanation).
    pub looping: bool,
    /// Feedback for the current question or the final summary.
    pub feedback: Vec<Line<'static>>,
    pub problem_scroll: u16,
}

impl QuizWs {
    pub fn step(&self) -> Option<(&DiagramStep, usize)> {
        let pos = self.timeline.pos;
        self.playing.get(pos / FRAMES_PER_STEP).map(|s| (s, pos % FRAMES_PER_STEP))
    }

    fn play(&mut self, steps: Vec<DiagramStep>, looping: bool, speed: usize) {
        self.timeline = Timeline::new(steps.len() * FRAMES_PER_STEP, speed);
        self.playing = steps;
        self.looping = looping;
    }
}

impl App {
    pub(crate) fn open_quiz(&mut self, ch: &Challenge) {
        let n = ch.meta.questions.len();
        let mut ws = QuizWs {
            key: ch.key(),
            q: 0,
            phase: if ch.meta.stage == Stage::Watch { QuizPhase::Done } else { QuizPhase::Answering },
            selected: 0,
            input: String::new(),
            attempts: vec![0; n],
            first_try: vec![false; n],
            hint_shown: vec![false; n],
            playing: Vec::new(),
            timeline: Timeline::new(0, DIAGRAM_SPEED),
            looping: false,
            feedback: Vec::new(),
            problem_scroll: 0,
        };
        let steps = ch.meta.diagram.as_ref().map(|d| d.steps.clone()).unwrap_or_default();
        let watch = ch.meta.stage == Stage::Watch;
        ws.play(steps, !watch, DIAGRAM_SPEED);
        if watch {
            ws.feedback.push(Line::from(Span::styled(
                "Space plays or pauses, left/right step, [ ] change speed.",
                self.theme.dim(),
            )));
        }
        self.progress.last_challenge = Some(ch.key());
        self.screen = Screen::Quiz(Box::new(ws));
    }

    pub(crate) fn quiz_tick(&mut self, elapsed: Duration) {
        let Screen::Quiz(ws) = &mut self.screen else { return };
        ws.timeline.tick(elapsed.as_millis() as u64);
        if ws.looping && ws.timeline.at_end() && !ws.playing.is_empty() {
            ws.timeline.seek(0);
            ws.timeline.playing = true;
        }
        let key = ws.key.clone();
        let walkthrough_done = !ws.looping && ws.timeline.at_end() && !ws.playing.is_empty();
        let is_watch = self.lib.challenge(&key).is_some_and(|c| c.meta.stage == Stage::Watch);
        if is_watch && walkthrough_done && !self.progress.is_done(&key) {
            self.finish_challenge(&key, None, None, Vec::new());
        }
    }

    pub(crate) fn quiz_key(&mut self, key: KeyEvent) {
        let Screen::Quiz(ws) = &mut self.screen else { return };
        let Some(ch) = self.lib.challenge(&ws.key).cloned() else { return };
        if key.modifiers.contains(KeyModifiers::CONTROL) {
            if key.code == KeyCode::Char('q') {
                self.go_home();
            }
            return;
        }
        // diagram playback works in every phase
        let frames = FRAMES_PER_STEP as i64;
        match key.code {
            KeyCode::Char(' ') => return ws.timeline.toggle(),
            KeyCode::Left => return ws.timeline.step(-frames),
            KeyCode::Right => return ws.timeline.step(frames),
            KeyCode::Char('[') => return ws.timeline.slower(),
            KeyCode::Char(']') => return ws.timeline.faster(),
            KeyCode::PageDown => {
                ws.problem_scroll = ws.problem_scroll.saturating_add(3);
                return;
            }
            KeyCode::PageUp => {
                ws.problem_scroll = ws.problem_scroll.saturating_sub(3);
                return;
            }
            KeyCode::Esc => return self.go_home(),
            _ => {}
        }
        match ws.phase {
            QuizPhase::Answering => self.quiz_answer_key(&ch, key),
            QuizPhase::Wrong => {
                if matches!(key.code, KeyCode::Enter | KeyCode::Char('r')) {
                    ws.phase = QuizPhase::Answering;
                    ws.feedback.clear();
                } else if key.code == KeyCode::Char('q') {
                    self.go_home();
                }
            }
            QuizPhase::Correct | QuizPhase::Revealed => {
                if matches!(key.code, KeyCode::Enter | KeyCode::Char('n')) {
                    self.next_question(&ch);
                } else if key.code == KeyCode::Char('q') {
                    self.go_home();
                }
            }
            QuizPhase::Done => match key.code {
                KeyCode::Char('n') | KeyCode::Enter => self.open_next(),
                KeyCode::Char('r') if !ch.meta.questions.is_empty() => self.open_quiz(&ch),
                KeyCode::Char('g') => ws.timeline.seek(0),
                KeyCode::Char('q') => self.go_home(),
                KeyCode::Char('t') => self.toggle_theme(),
                KeyCode::Char('?') => self.help = true,
                _ => {}
            },
        }
    }

    fn quiz_answer_key(&mut self, ch: &Challenge, key: KeyEvent) {
        let Screen::Quiz(ws) = &mut self.screen else { return };
        let Some(q) = ch.meta.questions.get(ws.q) else { return };
        if q.is_choice() {
            let n = q.choices.len();
            match key.code {
                KeyCode::Up | KeyCode::Char('k') => ws.selected = ws.selected.saturating_sub(1),
                KeyCode::Down | KeyCode::Char('j') => ws.selected = (ws.selected + 1).min(n - 1),
                KeyCode::Char(c @ '1'..='9') => {
                    let i = c as usize - '1' as usize;
                    if i < n {
                        ws.selected = i;
                    }
                }
                KeyCode::Char(c @ 'a'..='f') if (c as usize - 'a' as usize) < n => {
                    ws.selected = c as usize - 'a' as usize;
                }
                KeyCode::Enter => {
                    let answer = Answer::Choice(ws.selected);
                    self.submit_answer(ch, answer);
                }
                KeyCode::Char('h') => self.quiz_hint(ch),
                KeyCode::Char('q') => self.go_home(),
                KeyCode::Char('?') => self.help = true,
                _ => {}
            }
            return;
        }
        match key.code {
            KeyCode::Char(c) if c.is_ascii_digit() || ".,_%eEkKmMgGbBtT".contains(c) => {
                if ws.input.len() < 24 {
                    ws.input.push(c);
                }
            }
            KeyCode::Backspace => {
                ws.input.pop();
            }
            KeyCode::Enter => match quiz::parse_number(&ws.input) {
                Some(v) => self.submit_answer(ch, Answer::Number(v)),
                None => {
                    ws.feedback = vec![Line::from(Span::styled(
                        "Type a number, for example 12000, 12k or 1.5M.",
                        self.theme.bold(self.theme.warn),
                    ))];
                }
            },
            KeyCode::Char('h') => self.quiz_hint(ch),
            KeyCode::Char('q') => self.go_home(),
            KeyCode::Char('?') => self.help = true,
            _ => {}
        }
    }

    fn quiz_hint(&mut self, ch: &Challenge) {
        let Screen::Quiz(ws) = &mut self.screen else { return };
        let Some(q) = ch.meta.questions.get(ws.q) else { return };
        if q.hint.is_empty() || ws.hint_shown[ws.q] {
            return;
        }
        ws.hint_shown[ws.q] = true;
        let key = ws.key.clone();
        if !self.progress.is_done(&key) {
            self.progress.use_hint(&key);
        }
    }

    fn submit_answer(&mut self, ch: &Challenge, answer: Answer) {
        let t = &self.theme;
        let Screen::Quiz(ws) = &mut self.screen else { return };
        let Some(q) = ch.meta.questions.get(ws.q) else { return };
        let correct = quiz::is_correct(q, answer);
        let expected = if q.is_choice() {
            let i = q.answer as usize;
            format!(
                "{}) {}",
                (b'a' + (i as u8).saturating_sub(1)) as char,
                q.choices.get(i.saturating_sub(1)).cloned().unwrap_or_default()
            )
        } else {
            format!("about {} {}", quiz::format_number(q.answer), q.unit).trim_end().to_string()
        };
        ws.feedback.clear();
        if correct {
            ws.first_try[ws.q] = ws.attempts[ws.q] == 0;
            ws.phase = QuizPhase::Correct;
            let note = if let Answer::Number(v) = answer {
                format!(
                    "Correct: {} is within {:.0}% of {}.",
                    quiz::format_number(v),
                    q.tolerance * 100.0,
                    quiz::format_number(q.answer)
                )
            } else {
                "Correct.".to_string()
            };
            ws.feedback.push(Line::from(Span::styled(note, t.bold(t.good))));
        } else {
            ws.attempts[ws.q] += 1;
            if ws.attempts[ws.q] >= MAX_ATTEMPTS {
                ws.phase = QuizPhase::Revealed;
                ws.feedback.push(Line::from(Span::styled(format!("The answer is {expected}."), t.bold(t.bad))));
            } else {
                ws.phase = QuizPhase::Wrong;
                let tip = if q.hint.is_empty() || ws.hint_shown[ws.q] { "" } else { "  h shows a hint." };
                ws.feedback.push(Line::from(Span::styled(
                    format!("Not quite. Enter tries again ({} left).{tip}", MAX_ATTEMPTS - ws.attempts[ws.q]),
                    t.bold(t.warn),
                )));
                return;
            }
        }
        for line in q.explanation.trim().lines() {
            ws.feedback.push(Line::from(Span::styled(line.to_string(), t.text())));
        }
        ws.feedback.push(Line::from(Span::styled("Enter: next question", t.dim())));
        let steps = if q.steps.is_empty() { ws.playing.clone() } else { q.steps.clone() };
        let speed = ws.timeline.speed;
        ws.play(steps, false, speed);
    }

    fn next_question(&mut self, ch: &Challenge) {
        let Screen::Quiz(ws) = &mut self.screen else { return };
        ws.q += 1;
        ws.selected = 0;
        ws.input.clear();
        ws.feedback.clear();
        let speed = ws.timeline.speed;
        let scene = ch.meta.diagram.as_ref().map(|d| d.steps.clone()).unwrap_or_default();
        ws.play(scene, true, speed);
        if ws.q < ch.meta.questions.len() {
            ws.phase = QuizPhase::Answering;
            return;
        }
        ws.phase = QuizPhase::Done;
        let total = ch.meta.questions.len();
        let first = ws.first_try.iter().filter(|b| **b).count();
        let grade = quiz::grade(first, total);
        let t = &self.theme;
        let grade_label = if t.is_game() { grade.medal().to_string() } else { format!("grade {}", grade.letter()) };
        let mut lines = vec![Line::from(vec![
            Span::styled(format!("{first}/{total} right on the first try  "), t.bold(t.fg)),
            Span::styled(grade_label, t.bold(t.accent)),
        ])];
        for (i, q) in ch.meta.questions.iter().enumerate() {
            let mark = if ws.first_try[i] { "+" } else { "-" };
            let style = if ws.first_try[i] { t.dim() } else { t.bold(t.warn) };
            let short: String = q.prompt.chars().take(60).collect();
            lines.push(Line::from(Span::styled(format!(" {mark} {short}"), style)));
        }
        let key = ws.key.clone();
        self.finish_challenge(&key, Some(grade), None, lines);
    }
}
