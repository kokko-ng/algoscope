//! Vim keymap: normal, insert, visual, visual-line and a small command line.

use ratatui::crossterm::event::{KeyCode, KeyEvent, KeyModifiers};

use super::{Action, Editor, Group, INDENT, Pos};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub enum VimMode {
    #[default]
    Normal,
    Insert,
    Visual,
    VisualLine,
    Command,
}

#[derive(Debug, Clone, Default)]
pub struct VimState {
    pub mode: VimMode,
    pub cmdline: String,
    op: Option<char>,
    g: bool,
    replace: bool,
    count: usize,
}

impl VimState {
    fn take_count(&mut self) -> usize {
        let n = self.count.max(1);
        self.count = 0;
        n
    }

    fn reset_pending(&mut self) {
        self.op = None;
        self.g = false;
        self.replace = false;
        self.count = 0;
    }
}

/// A motion's target and how an operator should treat it.
struct Motion {
    to: Pos,
    linewise: bool,
    inclusive: bool,
}

pub fn handle(e: &mut Editor, key: KeyEvent) -> Action {
    if key.modifiers.contains(KeyModifiers::CONTROL) {
        match key.code {
            KeyCode::Char('e') => return Action::Run,
            KeyCode::Char('t') => return Action::Submit,
            KeyCode::Char('q') => return Action::Quit,
            _ => {}
        }
    }
    match e.vim.mode {
        VimMode::Insert => insert(e, key),
        VimMode::Command => command(e, key),
        VimMode::Normal | VimMode::Visual | VimMode::VisualLine => normal(e, key),
    }
}

fn insert(e: &mut Editor, key: KeyEvent) -> Action {
    match key.code {
        KeyCode::Esc => {
            e.vim.mode = VimMode::Normal;
            e.break_group();
            if e.cur.col > 0 {
                e.cur.col -= 1;
            }
        }
        KeyCode::Char(c) if !key.modifiers.contains(KeyModifiers::CONTROL) => {
            e.checkpoint(Group::Typing);
            e.insert_char(c);
        }
        KeyCode::Enter => {
            e.checkpoint(Group::Typing);
            e.newline();
        }
        KeyCode::Backspace => {
            e.checkpoint(Group::Typing);
            e.backspace();
        }
        KeyCode::Delete => {
            e.checkpoint(Group::Typing);
            e.delete_forward();
        }
        KeyCode::Tab => {
            e.checkpoint(Group::Typing);
            let n = INDENT - e.cur.col % INDENT;
            e.insert_str(&" ".repeat(n));
        }
        KeyCode::Left => e.left(),
        KeyCode::Right => e.right(),
        KeyCode::Up => e.vertical(-1),
        KeyCode::Down => e.vertical(1),
        KeyCode::Home => e.home(),
        KeyCode::End => e.end(),
        _ => return Action::Unhandled,
    }
    Action::None
}

fn command(e: &mut Editor, key: KeyEvent) -> Action {
    match key.code {
        KeyCode::Esc => {
            e.vim.cmdline.clear();
            e.vim.mode = VimMode::Normal;
        }
        KeyCode::Backspace => {
            if e.vim.cmdline.pop().is_none() {
                e.vim.mode = VimMode::Normal;
            }
        }
        KeyCode::Char(c) => e.vim.cmdline.push(c),
        KeyCode::Enter => {
            let cmd = std::mem::take(&mut e.vim.cmdline);
            e.vim.mode = VimMode::Normal;
            return match cmd.trim() {
                "w" => Action::Save,
                "q" | "q!" | "wq" | "x" => Action::Quit,
                "run" | "r" => Action::Run,
                "submit" | "s" => Action::Submit,
                n if n.parse::<usize>().is_ok() => {
                    let row = n.parse::<usize>().unwrap_or(1).saturating_sub(1);
                    e.move_to(Pos::new(row, 0));
                    e.home_indent();
                    Action::None
                }
                other => {
                    e.message = Some(format!("unknown command :{other}  (try :w :q :run :submit)"));
                    Action::None
                }
            };
        }
        _ => {}
    }
    Action::None
}

impl Editor {
    fn home_indent(&mut self) {
        self.cur.col = self.indent_of(self.cur.row);
        self.want_col = self.cur.col;
    }

    /// In normal mode the cursor sits on a character, never past the end.
    fn normal_clamp(&mut self) {
        let len = self.line_len(self.cur.row);
        if len > 0 && self.cur.col >= len {
            self.cur.col = len - 1;
        }
    }
}

fn motion(e: &Editor, code: KeyCode, count: usize, g: bool) -> Option<Motion> {
    let cur = e.cur;
    let rows = e.lines.len();
    let charwise = |to: Pos, inclusive: bool| Some(Motion { to, linewise: false, inclusive });
    match code {
        KeyCode::Char('h') | KeyCode::Left | KeyCode::Backspace => {
            charwise(Pos::new(cur.row, cur.col.saturating_sub(count)), false)
        }
        KeyCode::Char('l' | ' ') | KeyCode::Right => {
            charwise(Pos::new(cur.row, (cur.col + count).min(e.line_len(cur.row))), false)
        }
        KeyCode::Char('j') | KeyCode::Down | KeyCode::Enter => {
            Some(Motion { to: Pos::new((cur.row + count).min(rows - 1), cur.col), linewise: true, inclusive: true })
        }
        KeyCode::Char('k') | KeyCode::Up => {
            Some(Motion { to: Pos::new(cur.row.saturating_sub(count), cur.col), linewise: true, inclusive: true })
        }
        KeyCode::Char('w') => {
            let mut p = cur;
            for _ in 0..count {
                p = e.word_forward(p);
            }
            charwise(p, false)
        }
        KeyCode::Char('b') => {
            let mut p = cur;
            for _ in 0..count {
                p = e.word_back(p);
            }
            charwise(p, false)
        }
        KeyCode::Char('e') => {
            let mut p = cur;
            for _ in 0..count {
                p = e.word_end(p);
            }
            charwise(p, true)
        }
        KeyCode::Char('0') | KeyCode::Home => charwise(Pos::new(cur.row, 0), false),
        KeyCode::Char('^') => charwise(Pos::new(cur.row, e.indent_of(cur.row)), false),
        KeyCode::Char('$') | KeyCode::End => charwise(Pos::new(cur.row, e.line_len(cur.row).saturating_sub(1)), true),
        KeyCode::Char('g') if g => Some(Motion { to: Pos::new(0, 0), linewise: true, inclusive: true }),
        KeyCode::Char('G') => Some(Motion { to: Pos::new(rows - 1, 0), linewise: true, inclusive: true }),
        _ => None,
    }
}

#[expect(clippy::too_many_lines, reason = "a flat key table reads better than split handlers")]
fn normal(e: &mut Editor, key: KeyEvent) -> Action {
    let visual = matches!(e.vim.mode, VimMode::Visual | VimMode::VisualLine);
    let ctrl = key.modifiers.contains(KeyModifiers::CONTROL);

    if e.vim.replace {
        e.vim.replace = false;
        if let KeyCode::Char(c) = key.code
            && !e.readonly
            && e.cur.col < e.line_len(e.cur.row)
        {
            e.checkpoint(Group::Other);
            let p = e.cur;
            e.delete_range(p, Pos::new(p.row, p.col + 1));
            e.insert_char(c);
            e.cur = p;
        }
        return Action::None;
    }

    if ctrl {
        match key.code {
            KeyCode::Char('r') if !e.readonly => e.redo(),
            KeyCode::Char('d') => e.vertical((e.view_height / 2).max(1) as i64),
            KeyCode::Char('u') => e.vertical(-((e.view_height / 2).max(1) as i64)),
            _ => return Action::Unhandled,
        }
        e.normal_clamp();
        return Action::None;
    }

    if let KeyCode::Char(c @ '0'..='9') = key.code
        && (c != '0' || e.vim.count > 0)
    {
        e.vim.count = e.vim.count * 10 + c.to_digit(10).unwrap_or(0) as usize;
        return Action::None;
    }

    if key.code == KeyCode::Esc {
        let had_pending = e.vim.op.is_some() || e.vim.g || e.vim.count > 0;
        e.vim.reset_pending();
        if visual {
            e.vim.mode = VimMode::Normal;
            e.anchor = None;
            return Action::None;
        }
        return if had_pending { Action::None } else { Action::Leave };
    }

    let g = std::mem::take(&mut e.vim.g);
    if key.code == KeyCode::Char('g') && !g {
        e.vim.g = true;
        return Action::None;
    }

    let count = e.vim.take_count();

    // pending operator: d, c, y, >, <
    if let Some(op) = e.vim.op {
        e.vim.op = None;
        if key.code == KeyCode::Char(op) {
            let r1 = (e.cur.row + count - 1).min(e.lines.len() - 1);
            apply_lines(e, op, e.cur.row, r1);
            return Action::None;
        }
        let code = match (op, key.code) {
            ('c', KeyCode::Char('w')) => KeyCode::Char('e'),
            (_, code) => code,
        };
        if let Some(mut m) = motion(e, code, count, g) {
            if op == 'd' && key.code == KeyCode::Char('w') && m.to.row > e.cur.row {
                m.to = Pos::new(e.cur.row, e.line_len(e.cur.row));
            }
            if m.linewise {
                let (a, b) = if m.to.row < e.cur.row { (m.to.row, e.cur.row) } else { (e.cur.row, m.to.row) };
                apply_lines(e, op, a, b);
            } else {
                let (a, mut b) = if m.to < e.cur { (m.to, e.cur) } else { (e.cur, m.to) };
                if m.inclusive {
                    b.col = (b.col + 1).min(e.line_len(b.row));
                }
                apply_chars(e, op, a, b);
            }
        }
        return Action::None;
    }

    if let Some(m) = motion(e, key.code, count, g) {
        e.cur = m.to;
        if m.linewise && !matches!(key.code, KeyCode::Char('g' | 'G')) {
            e.cur.col = e.want_col.min(e.line_len(e.cur.row));
        } else if matches!(key.code, KeyCode::Char('g' | 'G')) {
            e.home_indent();
        } else {
            e.want_col = e.cur.col;
        }
        if matches!(key.code, KeyCode::Char('$') | KeyCode::End) {
            e.want_col = usize::MAX;
        }
        e.normal_clamp();
        return Action::None;
    }

    if visual {
        return visual_key(e, key);
    }

    let ro = e.readonly;
    match key.code {
        KeyCode::Char(':') => {
            e.vim.mode = VimMode::Command;
            e.vim.cmdline.clear();
        }
        KeyCode::Char('v') => {
            e.vim.mode = VimMode::Visual;
            e.anchor = Some(e.cur);
        }
        KeyCode::Char('V') => {
            e.vim.mode = VimMode::VisualLine;
            e.anchor = Some(e.cur);
        }
        KeyCode::Char('y') => e.vim.op = Some('y'),
        KeyCode::Char(c @ ('d' | 'c' | '>' | '<')) if !ro => e.vim.op = Some(c),
        KeyCode::Char('i') if !ro => enter_insert(e),
        KeyCode::Char('a') if !ro => {
            e.cur.col = (e.cur.col + 1).min(e.line_len(e.cur.row));
            enter_insert(e);
        }
        KeyCode::Char('I') if !ro => {
            e.home_indent();
            enter_insert(e);
        }
        KeyCode::Char('A') if !ro => {
            e.end();
            enter_insert(e);
        }
        KeyCode::Char('o') if !ro => {
            e.checkpoint(Group::Other);
            e.end();
            e.newline();
            enter_insert(e);
        }
        KeyCode::Char('O') if !ro => {
            e.checkpoint(Group::Other);
            let indent = e.indent_of(e.cur.row);
            e.lines.insert(e.cur.row, " ".repeat(indent));
            e.cur.col = indent;
            enter_insert(e);
        }
        KeyCode::Char('x') | KeyCode::Delete if !ro => {
            if e.line_len(e.cur.row) > 0 {
                e.checkpoint(Group::Other);
                let end = (e.cur.col + count).min(e.line_len(e.cur.row));
                e.register.text = e.delete_range(e.cur, Pos::new(e.cur.row, end));
                e.register.linewise = false;
                e.normal_clamp();
            }
        }
        KeyCode::Char('D' | 'C') if !ro => {
            e.checkpoint(Group::Other);
            let end = Pos::new(e.cur.row, e.line_len(e.cur.row));
            e.register.text = e.delete_range(e.cur, end);
            e.register.linewise = false;
            if key.code == KeyCode::Char('C') {
                enter_insert(e);
            } else {
                e.normal_clamp();
            }
        }
        KeyCode::Char('p' | 'P') if !ro => {
            e.checkpoint(Group::Other);
            for _ in 0..count {
                e.put(key.code == KeyCode::Char('p'));
            }
        }
        KeyCode::Char('u') if !ro => e.undo(),
        KeyCode::Char('r') if !ro => e.vim.replace = true,
        KeyCode::Char('J') if !ro => {
            if e.cur.row + 1 < e.lines.len() {
                e.checkpoint(Group::Other);
                let next = e.lines.remove(e.cur.row + 1);
                let row = e.cur.row;
                let trimmed = e.lines[row].trim_end().to_string();
                e.lines[row] = trimmed;
                e.cur.col = e.line_len(row);
                let next = next.trim_start();
                if !next.is_empty() {
                    e.lines[row].push(' ');
                    e.lines[row].push_str(next);
                }
            }
        }
        _ => return Action::Unhandled,
    }
    Action::None
}

fn enter_insert(e: &mut Editor) {
    e.vim.mode = VimMode::Insert;
    e.break_group();
}

fn visual_key(e: &mut Editor, key: KeyEvent) -> Action {
    let Some(anchor) = e.anchor else {
        e.vim.mode = VimMode::Normal;
        return Action::None;
    };
    let linewise = e.vim.mode == VimMode::VisualLine;
    let (a, b) = if anchor <= e.cur { (anchor, e.cur) } else { (e.cur, anchor) };
    let op = match key.code {
        KeyCode::Char('d' | 'x') if !e.readonly => 'd',
        KeyCode::Char('c' | 's') if !e.readonly => 'c',
        KeyCode::Char('y') => 'y',
        KeyCode::Char('>') if !e.readonly => '>',
        KeyCode::Char('<') if !e.readonly => '<',
        KeyCode::Char('v') if !linewise => {
            e.vim.mode = VimMode::Normal;
            e.anchor = None;
            return Action::None;
        }
        KeyCode::Char('V') if linewise => {
            e.vim.mode = VimMode::Normal;
            e.anchor = None;
            return Action::None;
        }
        KeyCode::Char('v') => {
            e.vim.mode = VimMode::Visual;
            return Action::None;
        }
        KeyCode::Char('V') => {
            e.vim.mode = VimMode::VisualLine;
            return Action::None;
        }
        _ => return Action::Unhandled,
    };
    e.anchor = None;
    e.vim.mode = VimMode::Normal;
    if linewise || op == '>' || op == '<' {
        apply_lines(e, op, a.row, b.row);
    } else {
        let end = Pos::new(b.row, (b.col + 1).min(e.line_len(b.row)));
        apply_chars(e, op, a, end);
    }
    Action::None
}

fn apply_lines(e: &mut Editor, op: char, r0: usize, r1: usize) {
    match op {
        'y' => {
            e.register.text = e.lines[r0..=r1].join("\n");
            e.register.linewise = true;
            e.cur = Pos::new(r0, e.cur.col.min(e.line_len(r0)));
        }
        'd' => {
            e.checkpoint(Group::Other);
            e.register.text = e.delete_lines(r0, r1);
            e.register.linewise = true;
        }
        'c' => {
            e.checkpoint(Group::Other);
            let indent = e.indent_of(r0);
            e.register.text = e.lines[r0..=r1].join("\n");
            e.register.linewise = true;
            e.lines.drain(r0..=r1);
            e.lines.insert(r0, " ".repeat(indent));
            e.cur = Pos::new(r0, indent);
            enter_insert(e);
        }
        '>' | '<' => {
            e.checkpoint(Group::Other);
            e.indent_lines(r0, r1, if op == '>' { 1 } else { -1 });
            e.cur = Pos::new(r0, e.indent_of(r0));
        }
        _ => {}
    }
    if e.vim.mode != VimMode::Insert {
        e.normal_clamp();
    }
}

fn apply_chars(e: &mut Editor, op: char, a: Pos, b: Pos) {
    match op {
        'y' => {
            e.register.text = e.text_range(a, b);
            e.register.linewise = false;
            e.cur = a;
        }
        'd' | 'c' => {
            e.checkpoint(Group::Other);
            e.register.text = e.delete_range(a, b);
            e.register.linewise = false;
            if op == 'c' {
                enter_insert(e);
                return;
            }
        }
        '>' | '<' => apply_lines(e, op, a.row, b.row),
        _ => {}
    }
    e.normal_clamp();
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::progress::KeymapKind;

    fn keys(e: &mut Editor, s: &str) {
        for c in s.chars() {
            let code = match c {
                '\x1b' => KeyCode::Esc,
                '\n' => KeyCode::Enter,
                c => KeyCode::Char(c),
            };
            e.handle_key(KeyEvent::new(code, KeyModifiers::NONE));
        }
    }

    #[test]
    fn insert_and_escape() {
        let mut e = Editor::new("", KeymapKind::Vim);
        keys(&mut e, "idef f():\nreturn 1\x1b");
        assert_eq!(e.text(), "def f():\n    return 1\n");
        assert_eq!(e.vim.mode, VimMode::Normal);
        assert_eq!(e.cur, Pos::new(1, 11));
    }

    #[test]
    fn dd_yy_p_and_undo() {
        let mut e = Editor::new("a\nb\nc", KeymapKind::Vim);
        keys(&mut e, "dd");
        assert_eq!(e.text(), "b\nc\n");
        keys(&mut e, "p");
        assert_eq!(e.text(), "b\na\nc\n");
        keys(&mut e, "u");
        assert_eq!(e.text(), "b\nc\n");
        keys(&mut e, "yyP");
        assert_eq!(e.text(), "b\nb\nc\n");
        keys(&mut e, "G2dd");
        assert_eq!(e.text(), "b\nb\n");
    }

    #[test]
    fn word_operators() {
        let mut e = Editor::new("left = right + 1", KeymapKind::Vim);
        keys(&mut e, "dw");
        assert_eq!(e.text(), "= right + 1\n");
        keys(&mut e, "wcwmid\x1b");
        assert_eq!(e.text(), "= mid + 1\n");
        keys(&mut e, "d$");
        assert_eq!(e.text(), "= mi\n");
    }

    #[test]
    fn visual_line_indent_and_delete() {
        let mut e = Editor::new("a\nb\nc", KeymapKind::Vim);
        keys(&mut e, "Vj>");
        assert_eq!(e.text(), "    a\n    b\nc\n");
        keys(&mut e, "0vld");
        assert_eq!(e.text(), "  a\n    b\nc\n");
    }

    #[test]
    fn escape_from_normal_leaves_and_commands_map_to_actions() {
        let mut e = Editor::new("x", KeymapKind::Vim);
        assert_eq!(e.handle_key(KeyEvent::new(KeyCode::Esc, KeyModifiers::NONE)), Action::Leave);
        keys(&mut e, ":run");
        assert_eq!(e.handle_key(KeyEvent::new(KeyCode::Enter, KeyModifiers::NONE)), Action::Run);
        assert_eq!(e.handle_key(KeyEvent::new(KeyCode::Char('r'), KeyModifiers::CONTROL)), Action::None);
    }
}
