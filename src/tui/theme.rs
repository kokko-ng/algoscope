//! Stealth (default) and game themes: palette, user-facing labels and celebration behaviour.

use ratatui::style::{Color, Modifier, Style};

use crate::progress::ThemeKind;

pub struct Labels {
    pub app: &'static str,
    pub home: &'static str,
    pub tree: &'static str,
    pub problem: &'static str,
    pub output: &'static str,
    pub trace: &'static str,
    pub run: &'static str,
    pub submit: &'static str,
    pub xp: &'static str,
    pub watch: &'static str,
    pub build: &'static str,
    pub apply: &'static str,
    pub locked: &'static str,
    pub hint: &'static str,
}

const STEALTH: Labels = Labels {
    app: "algoscope",
    home: "suites",
    tree: "dependency graph",
    problem: "spec",
    output: "results",
    trace: "trace",
    run: "trace",
    submit: "profile",
    xp: "pts",
    watch: "walkthrough",
    build: "implement",
    apply: "exercise",
    locked: "blocked",
    hint: "note",
};

const GAME: Labels = Labels {
    app: "ALGOSCOPE",
    home: "World map",
    tree: "Skill tree",
    problem: "Quest",
    output: "Battle log",
    trace: "Scope",
    run: "Cast",
    submit: "Challenge",
    xp: "XP",
    watch: "Lore",
    build: "Forge",
    apply: "Trial",
    locked: "sealed",
    hint: "Hint",
};

pub struct Theme {
    pub kind: ThemeKind,
    pub labels: &'static Labels,
    pub celebrate: bool,
    pub fg: Color,
    pub dim: Color,
    pub border: Color,
    pub border_focus: Color,
    pub title: Color,
    pub accent: Color,
    pub accent2: Color,
    pub good: Color,
    pub bad: Color,
    pub warn: Color,
    pub sel_bg: Color,
    pub exec_bg: Color,
    pub kw: Color,
    pub builtin: Color,
    pub string: Color,
    pub number: Color,
    pub comment: Color,
    pub func: Color,
    pub read: Color,
    pub write: Color,
    pub pointer: Color,
    pub window: Color,
}

impl Theme {
    pub fn new(kind: ThemeKind) -> Theme {
        match kind {
            ThemeKind::Stealth => Theme {
                kind,
                labels: &STEALTH,
                celebrate: false,
                fg: Color::Reset,
                dim: Color::Indexed(244),
                border: Color::Indexed(239),
                border_focus: Color::Indexed(248),
                title: Color::Indexed(250),
                accent: Color::Indexed(110),
                accent2: Color::Indexed(109),
                good: Color::Indexed(108),
                bad: Color::Indexed(167),
                warn: Color::Indexed(179),
                sel_bg: Color::Indexed(238),
                exec_bg: Color::Indexed(236),
                kw: Color::Indexed(110),
                builtin: Color::Indexed(139),
                string: Color::Indexed(108),
                number: Color::Indexed(173),
                comment: Color::Indexed(242),
                func: Color::Indexed(180),
                read: Color::Indexed(109),
                write: Color::Indexed(179),
                pointer: Color::Indexed(110),
                window: Color::Indexed(237),
            },
            ThemeKind::Game => Theme {
                kind,
                labels: &GAME,
                celebrate: true,
                fg: Color::Reset,
                dim: Color::Indexed(245),
                border: Color::Indexed(97),
                border_focus: Color::Indexed(213),
                title: Color::Indexed(219),
                accent: Color::Indexed(213),
                accent2: Color::Indexed(51),
                good: Color::Indexed(46),
                bad: Color::Indexed(196),
                warn: Color::Indexed(226),
                sel_bg: Color::Indexed(54),
                exec_bg: Color::Indexed(53),
                kw: Color::Indexed(207),
                builtin: Color::Indexed(81),
                string: Color::Indexed(120),
                number: Color::Indexed(215),
                comment: Color::Indexed(244),
                func: Color::Indexed(229),
                read: Color::Indexed(51),
                write: Color::Indexed(226),
                pointer: Color::Indexed(213),
                window: Color::Indexed(236),
            },
        }
    }

    pub fn is_game(&self) -> bool {
        self.kind == ThemeKind::Game
    }

    pub fn text(&self) -> Style {
        Style::default().fg(self.fg)
    }

    pub fn dim(&self) -> Style {
        Style::default().fg(self.dim)
    }

    pub fn accent(&self) -> Style {
        Style::default().fg(self.accent)
    }

    pub fn bold(&self, c: Color) -> Style {
        Style::default().fg(c).add_modifier(Modifier::BOLD)
    }

    pub fn border(&self, focused: bool) -> Style {
        Style::default().fg(if focused { self.border_focus } else { self.border })
    }

    pub fn title(&self, focused: bool) -> Style {
        let s = Style::default().fg(if focused { self.title } else { self.dim });
        if focused { s.add_modifier(Modifier::BOLD) } else { s }
    }
}
