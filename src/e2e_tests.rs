//! End-to-end and robustness tests: the whole app driven by key presses, the runner's failure modes, and fuzzing.

use std::thread;
use std::time::{Duration, Instant};

use ratatui::Terminal;
use ratatui::backend::TestBackend;
use ratatui::crossterm::event::{KeyCode, KeyEvent, KeyModifiers};

use crate::app::{App, Screen};
use crate::app_quiz::QuizPhase;
use crate::content::{Challenge, Library, Stage, Track};
use crate::progress::{KeymapKind, Store};
use crate::quiz;
use crate::runner::{self, Mode};
use crate::scoring::{self, Grade};
use crate::tui::editor::Editor;
use crate::tui::ui;

/// Small deterministic generator so fuzz runs are reproducible.
struct Rng(u64);

impl Rng {
    fn next(&mut self) -> u64 {
        self.0 ^= self.0 << 13;
        self.0 ^= self.0 >> 7;
        self.0 ^= self.0 << 17;
        self.0
    }

    fn below(&mut self, n: usize) -> usize {
        (self.next() % n as u64) as usize
    }
}

fn new_app() -> (App, tempfile::TempDir) {
    let dir = tempfile::tempdir().unwrap();
    let app = App::new(Library::load().unwrap(), Store::new(dir.path().to_path_buf()));
    (app, dir)
}

fn press(app: &mut App, code: KeyCode, mods: KeyModifiers) {
    app.on_key(KeyEvent::new(code, mods));
}

fn key(app: &mut App, code: KeyCode) {
    press(app, code, KeyModifiers::NONE);
}

fn draw(app: &mut App, w: u16, h: u16) {
    let mut term = Terminal::new(TestBackend::new(w, h)).unwrap();
    term.draw(|f| ui::draw(f, app)).unwrap();
}

/// Tick the app until no job is pending, or fail after a minute.
fn wait_for_job(app: &mut App) {
    let start = Instant::now();
    loop {
        app.tick(Duration::from_millis(33));
        let pending = matches!(&app.screen, Screen::Work(ws) if ws.pending.is_some());
        if !pending {
            return;
        }
        assert!(start.elapsed() < Duration::from_secs(90), "job did not finish");
        thread::sleep(Duration::from_millis(10));
    }
}

fn challenges(track: Track) -> Vec<Challenge> {
    let lib = Library::load().unwrap();
    lib.track_topics(track).flat_map(|t| t.challenges.clone()).collect()
}

/// Run `f` over the items on 8 threads.
fn in_parallel<T: Send + Sync>(items: &[T], f: impl Fn(&T) + Sync) {
    thread::scope(|s| {
        for chunk in items.chunks(items.len().div_ceil(8).max(1)) {
            let f = &f;
            s.spawn(move || chunk.iter().for_each(f));
        }
    });
}

// ---- data structures and algorithms, through the app ------------------------------------------------

/// Every challenge completes through the real app: walkthroughs by playing to the end, the rest by
/// submitting the reference with Ctrl+T. The starter never completes a challenge.
#[test]
fn every_dsa_challenge_completes_through_the_app() {
    in_parallel(&challenges(Track::Dsa), |ch| {
        let (mut app, _dir) = new_app();
        let key = ch.key();
        app.open(&key);
        if ch.meta.stage == Stage::Watch {
            wait_for_job(&mut app);
            key_end_of_trace(&mut app);
            assert!(app.progress.is_done(&key), "{key}: walkthrough not completed");
            return;
        }
        // the starter fails the suite
        press(&mut app, KeyCode::Char('t'), KeyModifiers::CONTROL);
        wait_for_job(&mut app);
        assert!(!app.progress.is_done(&key), "{key}: the starter completed the challenge");
        // the reference passes and grades gold
        if let Screen::Work(ws) = &mut app.screen {
            ws.editor.set_text(&ch.reference);
        }
        press(&mut app, KeyCode::Char('t'), KeyModifiers::CONTROL);
        wait_for_job(&mut app);
        let p = app.progress.get(&key);
        assert!(p.done, "{key}: the reference did not complete the challenge");
        assert_eq!(p.grade, Some(Grade::Gold), "{key}");
        assert_eq!(app.progress.xp, u64::from(scoring::award(ch.meta.xp, Some(Grade::Gold), 0)), "{key}");
    });
}

fn key_end_of_trace(app: &mut App) {
    if let Screen::Work(ws) = &mut app.screen {
        ws.focus = crate::app::Focus::Viz;
    }
    key(app, KeyCode::End);
    app.tick(Duration::from_millis(33));
}

// ---- system design, through the app -----------------------------------------------------------------

fn type_text(app: &mut App, text: &str) {
    for c in text.chars() {
        key(app, KeyCode::Char(c));
    }
}

fn phase(app: &App) -> QuizPhase {
    match &app.screen {
        Screen::Quiz(ws) => ws.phase,
        _ => panic!("not on the quiz screen"),
    }
}

/// Play a design walkthrough to its end.
fn finish_walkthrough(app: &mut App) {
    for _ in 0..2000 {
        if phase(app) == QuizPhase::Done
            && matches!(&app.screen, Screen::Quiz(ws) if ws.timeline.at_end() && !ws.timeline.playing)
        {
            app.tick(Duration::from_millis(33));
            return;
        }
        key(app, KeyCode::Right);
        app.tick(Duration::from_millis(33));
    }
}

/// Every quiz answered right on the first try grades gold; every walkthrough completes.
#[test]
fn every_design_quiz_answered_correctly_grades_gold() {
    for ch in challenges(Track::Design) {
        let (mut app, _dir) = new_app();
        let k = ch.key();
        app.open(&k);
        if ch.meta.stage == Stage::Watch {
            finish_walkthrough(&mut app);
            assert!(app.progress.is_done(&k), "{k}: walkthrough not completed");
            continue;
        }
        for (i, q) in ch.meta.questions.iter().enumerate() {
            if q.is_choice() {
                let pick = (0..q.choices.len()).find(|c| q.is_answer(*c)).unwrap();
                key(&mut app, KeyCode::Char(char::from(b'a' + pick as u8)));
            } else {
                type_text(&mut app, &q.answer.to_string());
            }
            key(&mut app, KeyCode::Enter);
            assert_eq!(phase(&app), QuizPhase::Correct, "{k} question {}", i + 1);
            key(&mut app, KeyCode::Enter);
        }
        assert_eq!(phase(&app), QuizPhase::Done, "{k}");
        let p = app.progress.get(&k);
        assert_eq!(p.grade, Some(Grade::Gold), "{k}");
        assert_eq!(app.progress.xp, u64::from(scoring::award(ch.meta.xp, Some(Grade::Gold), 0)), "{k}");
    }
}

/// Two wrong answers reveal each answer; the quiz still completes, graded bronze.
#[test]
fn every_design_quiz_answered_wrongly_reveals_and_grades_bronze() {
    for ch in challenges(Track::Design).into_iter().filter(|c| c.meta.stage == Stage::Quiz) {
        let (mut app, _dir) = new_app();
        let k = ch.key();
        app.open(&k);
        for (i, q) in ch.meta.questions.iter().enumerate() {
            for attempt in 0..quiz::MAX_ATTEMPTS {
                if q.is_choice() {
                    let wrong = (0..q.choices.len()).find(|c| !q.is_answer(*c)).unwrap();
                    key(&mut app, KeyCode::Char(char::from(b'a' + wrong as u8)));
                } else {
                    type_text(&mut app, &(q.answer.abs() * 1000.0 + 1000.0).to_string());
                }
                key(&mut app, KeyCode::Enter);
                let expected = if attempt + 1 < quiz::MAX_ATTEMPTS { QuizPhase::Wrong } else { QuizPhase::Revealed };
                assert_eq!(phase(&app), expected, "{k} question {} attempt {}", i + 1, attempt + 1);
                if expected == QuizPhase::Wrong {
                    key(&mut app, KeyCode::Enter);
                    if !q.is_choice() {
                        for _ in 0..40 {
                            key(&mut app, KeyCode::Backspace);
                        }
                    }
                }
            }
            key(&mut app, KeyCode::Enter);
        }
        assert_eq!(phase(&app), QuizPhase::Done, "{k}");
        assert_eq!(app.progress.get(&k).grade, Some(Grade::Bronze), "{k}");
    }
}

/// The "about X" text shown when an answer is revealed must itself be accepted as an answer.
#[test]
fn revealed_number_answers_are_accepted_as_written() {
    for ch in challenges(Track::Design) {
        for (i, q) in ch.meta.questions.iter().enumerate().filter(|(_, q)| !q.is_choice()) {
            let shown = quiz::format_number(q.answer);
            let parsed = quiz::parse_number(&shown).unwrap_or_else(|| panic!("{}: cannot parse {shown}", ch.key()));
            assert!(
                quiz::is_correct(q, quiz::Answer::Number(parsed)),
                "{} question {}: the shown answer {shown} is rejected",
                ch.key(),
                i + 1
            );
        }
    }
}

// ---- the runner's failure modes -----------------------------------------------------------------------

fn some_challenge() -> Challenge {
    Library::load().unwrap().challenge("foundations/max-gain").unwrap().clone()
}

#[test]
fn missing_python_is_reported_clearly() {
    let err = runner::check_python_at("/nonexistent/python3").unwrap_err().to_string();
    assert!(err.contains("could not run"), "{err}");
    let err = runner::run_with(&some_challenge(), Mode::Visual, "", "/nonexistent/python3", Duration::from_secs(5))
        .unwrap_err();
    assert!(err.contains("could not start"), "{err}");
}

#[test]
fn a_sleeping_solution_is_killed_at_the_time_limit() {
    let code = "import time\n\ndef solve(readings):\n    time.sleep(60)\n";
    let start = Instant::now();
    let err =
        runner::run_with(&some_challenge(), Mode::Score, code, &runner::python(), Duration::from_secs(2)).unwrap_err();
    assert!(err.contains("timed out"), "{err}");
    assert!(start.elapsed() < Duration::from_secs(10));
}

#[test]
fn a_harness_that_dies_reports_its_exit() {
    let code = "import os\n\ndef solve(readings):\n    os._exit(3)\n";
    let err = runner::run(&some_challenge(), Mode::Score, code).unwrap_err();
    assert!(err.contains("exited"), "{err}");
}

#[test]
fn corrupted_progress_and_settings_fall_back_to_defaults() {
    let dir = tempfile::tempdir().unwrap();
    std::fs::write(dir.path().join("progress.json"), "{not json").unwrap();
    std::fs::write(dir.path().join("settings.toml"), "theme = 7\n[[[").unwrap();
    let store = Store::new(dir.path().to_path_buf());
    assert_eq!(store.load_progress().xp, 0);
    assert_eq!(store.load_settings().keymap, KeymapKind::Standard);
    // and the app starts on them
    let mut app = App::new(Library::load().unwrap(), store);
    draw(&mut app, 80, 24);
}

// ---- fuzzing --------------------------------------------------------------------------------------

const EDITOR_KEYS: &[KeyCode] = &[
    KeyCode::Left,
    KeyCode::Right,
    KeyCode::Up,
    KeyCode::Down,
    KeyCode::Home,
    KeyCode::End,
    KeyCode::PageUp,
    KeyCode::PageDown,
    KeyCode::Enter,
    KeyCode::Backspace,
    KeyCode::Delete,
    KeyCode::Tab,
    KeyCode::BackTab,
    KeyCode::Esc,
];

const EDITOR_CHARS: &str = "abcxyz019 :()[]{}.,=+-_'\"#\u{e9}\u{4e2d}hjklwbe0$^gGdyycpPuoOiaIAxXrJvV><";

fn random_key(rng: &mut Rng) -> KeyEvent {
    let chars: Vec<char> = EDITOR_CHARS.chars().collect();
    let mods = match rng.below(10) {
        0 => KeyModifiers::CONTROL,
        1 => KeyModifiers::SHIFT,
        2 => KeyModifiers::ALT,
        _ => KeyModifiers::NONE,
    };
    if rng.below(3) == 0 {
        KeyEvent::new(EDITOR_KEYS[rng.below(EDITOR_KEYS.len())], mods)
    } else {
        KeyEvent::new(KeyCode::Char(chars[rng.below(chars.len())]), mods)
    }
}

/// Thousands of random keys in both keymaps never panic and never leave the cursor outside the buffer.
#[test]
fn fuzz_editor_keeps_its_invariants() {
    for keymap in [KeymapKind::Standard, KeymapKind::Vim] {
        for seed in 1..=6u64 {
            let mut rng = Rng(seed.wrapping_mul(0x9E37_79B9_7F4A_7C15));
            let mut ed = Editor::new("def solve(nums):\n    return max(nums)\n", keymap);
            for step in 0..6000 {
                if rng.below(200) == 0 {
                    ed.paste("for i in range(3):\n\tprint(i)\r\n");
                } else {
                    ed.handle_key(random_key(&mut rng));
                }
                assert!(!ed.lines.is_empty(), "{keymap:?} seed {seed} step {step}: empty buffer");
                assert!(ed.cur.row < ed.lines.len(), "{keymap:?} seed {seed} step {step}: row out of range");
                assert!(ed.cur.col <= ed.line_len(ed.cur.row), "{keymap:?} seed {seed} step {step}: col out of range");
                assert!(!ed.text().contains('\t'), "tabs are expanded");
            }
            // undo all the way back must always be possible
            for _ in 0..10_000 {
                ed.undo();
            }
            assert!(ed.cur.row < ed.lines.len());
        }
    }
}

const APP_KEYS: &[KeyCode] = &[
    KeyCode::Up,
    KeyCode::Down,
    KeyCode::Left,
    KeyCode::Right,
    KeyCode::Enter,
    KeyCode::Esc,
    KeyCode::Tab,
    KeyCode::Backspace,
    KeyCode::Home,
    KeyCode::End,
    KeyCode::PageDown,
    KeyCode::F(1),
    KeyCode::F(2),
    KeyCode::Char(' '),
    KeyCode::Char('1'),
    KeyCode::Char('2'),
    KeyCode::Char('a'),
    KeyCode::Char('b'),
    KeyCode::Char('h'),
    KeyCode::Char('n'),
    KeyCode::Char('r'),
    KeyCode::Char('k'),
    KeyCode::Char('5'),
    KeyCode::Char('.'),
    KeyCode::Char('['),
    KeyCode::Char(']'),
    KeyCode::Char('z'),
    KeyCode::Char('v'),
    KeyCode::Char('?'),
    KeyCode::Char('q'),
];

/// Random keys across every screen, drawn at sizes from 1x1 to 160x50, never panic.
#[test]
fn fuzz_app_across_screens_and_sizes() {
    let sizes = [(1, 1), (8, 3), (20, 6), (40, 12), (80, 24), (160, 50)];
    for seed in 1..=4u64 {
        let mut rng = Rng(seed.wrapping_mul(0xD1B5_4A32_D192_ED03));
        let (mut app, _dir) = new_app();
        for step in 0..4000 {
            if app.quit {
                app = new_app().0;
            }
            let code = APP_KEYS[rng.below(APP_KEYS.len())];
            app.on_key(KeyEvent::new(code, KeyModifiers::NONE));
            if rng.below(40) == 0 {
                app.on_paste("x = 1\ny = 2\n");
            }
            app.tick(Duration::from_millis(33));
            if step % 25 == 0 {
                let (w, h) = sizes[rng.below(sizes.len())];
                draw(&mut app, w, h);
            }
        }
    }
}

/// Number parsing never panics on arbitrary input.
#[test]
fn fuzz_number_parser() {
    let alphabet: Vec<char> = "0123456789.,_%eEkKmMgGbBtT -+".chars().collect();
    let mut rng = Rng(42);
    for _ in 0..50_000 {
        let len = rng.below(10);
        let s: String = (0..len).map(|_| alphabet[rng.below(alphabet.len())]).collect();
        if let Some(v) = quiz::parse_number(&s) {
            assert!(v.is_finite(), "{s} parsed to {v}");
        }
    }
}
