//! In-terminal code editor: a line buffer with undo, Python-aware indentation and two keymaps.

pub mod highlight;
mod render;
mod standard;
mod vim;

use ratatui::crossterm::event::KeyEvent;

pub use render::EditorView;
pub use vim::VimMode;

use crate::progress::KeymapKind;

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Default)]
pub struct Pos {
    pub row: usize,
    pub col: usize,
}

impl Pos {
    pub fn new(row: usize, col: usize) -> Pos {
        Pos { row, col }
    }
}

/// What the app should do after a key was handled by the editor.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Action {
    None,
    /// Leave the editor (Esc in standard mode, Esc from vim normal mode).
    Leave,
    Save,
    Run,
    Submit,
    Quit,
    Unhandled,
}

#[derive(Debug, Clone, Default)]
pub struct Register {
    pub text: String,
    pub linewise: bool,
}

#[derive(Debug, Clone)]
struct Snap {
    lines: Vec<String>,
    cur: Pos,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum Group {
    Typing,
    Other,
}

pub const INDENT: usize = 4;

#[derive(Debug, Clone)]
pub struct Editor {
    pub lines: Vec<String>,
    pub cur: Pos,
    /// Selection anchor: shift-selection in standard mode, visual mode in vim.
    pub anchor: Option<Pos>,
    want_col: usize,
    pub scroll_row: usize,
    pub scroll_col: usize,
    undo: Vec<Snap>,
    redo: Vec<Snap>,
    last_group: Option<Group>,
    pub register: Register,
    pub readonly: bool,
    pub dirty: bool,
    pub keymap: KeymapKind,
    pub vim: vim::VimState,
    pub message: Option<String>,
    pub view_height: usize,
}

impl Editor {
    pub fn new(text: &str, keymap: KeymapKind) -> Editor {
        let mut e = Editor {
            lines: vec![String::new()],
            cur: Pos::default(),
            anchor: None,
            want_col: 0,
            scroll_row: 0,
            scroll_col: 0,
            undo: Vec::new(),
            redo: Vec::new(),
            last_group: None,
            register: Register::default(),
            readonly: false,
            dirty: false,
            keymap,
            vim: vim::VimState::default(),
            message: None,
            view_height: 20,
        };
        e.set_text(text);
        e
    }

    pub fn set_text(&mut self, text: &str) {
        let text = text.replace("\r\n", "\n").replace('\t', "    ");
        self.lines = text.split('\n').map(str::to_owned).collect();
        if self.lines.len() > 1 && self.lines.last().is_some_and(String::is_empty) {
            self.lines.pop();
        }
        if self.lines.is_empty() {
            self.lines.push(String::new());
        }
        self.cur = Pos::default();
        self.anchor = None;
        self.scroll_row = 0;
        self.scroll_col = 0;
    }

    pub fn text(&self) -> String {
        let mut s = self.lines.join("\n");
        s.push('\n');
        s
    }

    pub fn set_keymap(&mut self, keymap: KeymapKind) {
        self.keymap = keymap;
        self.anchor = None;
        self.vim = vim::VimState::default();
    }

    /// Handle a key. Returns what the app should do next.
    pub fn handle_key(&mut self, key: KeyEvent) -> Action {
        self.message = None;
        match self.keymap {
            KeymapKind::Standard => standard::handle(self, key),
            KeymapKind::Vim => vim::handle(self, key),
        }
    }

    /// Insert pasted text at the cursor, replacing any selection.
    pub fn paste(&mut self, text: &str) {
        if self.readonly {
            return;
        }
        self.checkpoint(Group::Other);
        self.delete_selection();
        self.insert_str(&text.replace("\r\n", "\n").replace('\r', "\n").replace('\t', "    "));
    }

    pub fn mode_label(&self) -> Option<&'static str> {
        match self.keymap {
            KeymapKind::Standard => None,
            KeymapKind::Vim => Some(match self.vim.mode {
                VimMode::Normal => "NORMAL",
                VimMode::Insert => "INSERT",
                VimMode::Visual => "VISUAL",
                VimMode::VisualLine => "V-LINE",
                VimMode::Command => "COMMAND",
            }),
        }
    }

    // ---- geometry -------------------------------------------------------

    pub fn line_len(&self, row: usize) -> usize {
        self.lines.get(row).map_or(0, |l| l.chars().count())
    }

    fn byte(&self, p: Pos) -> usize {
        let line = &self.lines[p.row];
        line.char_indices().nth(p.col).map_or(line.len(), |(b, _)| b)
    }

    pub fn char_at(&self, p: Pos) -> Option<char> {
        let line = self.lines.get(p.row)?;
        match line.chars().nth(p.col) {
            Some(c) => Some(c),
            None if p.row + 1 < self.lines.len() => Some('\n'),
            None => None,
        }
    }

    fn last_row(&self) -> usize {
        self.lines.len() - 1
    }

    fn clamp(&self, p: Pos) -> Pos {
        let row = p.row.min(self.last_row());
        Pos::new(row, p.col.min(self.line_len(row)))
    }

    pub fn indent_of(&self, row: usize) -> usize {
        self.lines[row].chars().take_while(|c| *c == ' ').count()
    }

    pub fn ensure_visible(&mut self, height: usize, width: usize) {
        self.view_height = height.max(1);
        if self.cur.row < self.scroll_row {
            self.scroll_row = self.cur.row;
        } else if self.cur.row >= self.scroll_row + height {
            self.scroll_row = self.cur.row + 1 - height.max(1);
        }
        let width = width.max(1);
        if self.cur.col < self.scroll_col {
            self.scroll_col = self.cur.col;
        } else if self.cur.col >= self.scroll_col + width {
            self.scroll_col = self.cur.col + 1 - width;
        }
    }

    /// Scroll so a line (1-based, from a trace) is visible without moving the cursor.
    pub fn reveal_line(&mut self, line: usize) {
        let row = line.saturating_sub(1);
        let h = self.view_height.max(1);
        if row < self.scroll_row || row >= self.scroll_row + h {
            self.scroll_row = row.saturating_sub(h / 3);
        }
    }

    // ---- movement -------------------------------------------------------

    pub fn move_to(&mut self, p: Pos) {
        self.cur = self.clamp(p);
        self.want_col = self.cur.col;
    }

    pub fn left(&mut self) {
        if self.cur.col > 0 {
            self.cur.col -= 1;
        } else if self.cur.row > 0 {
            self.cur.row -= 1;
            self.cur.col = self.line_len(self.cur.row);
        }
        self.want_col = self.cur.col;
    }

    pub fn right(&mut self) {
        if self.cur.col < self.line_len(self.cur.row) {
            self.cur.col += 1;
        } else if self.cur.row < self.last_row() {
            self.cur.row += 1;
            self.cur.col = 0;
        }
        self.want_col = self.cur.col;
    }

    pub fn vertical(&mut self, delta: i64) {
        let row = (self.cur.row as i64 + delta).clamp(0, self.last_row() as i64) as usize;
        self.cur.row = row;
        self.cur.col = self.want_col.min(self.line_len(row));
    }

    pub fn home(&mut self) {
        let ind = self.indent_of(self.cur.row);
        self.cur.col = if self.cur.col == ind { 0 } else { ind };
        self.want_col = self.cur.col;
    }

    pub fn end(&mut self) {
        self.cur.col = self.line_len(self.cur.row);
        self.want_col = self.cur.col;
    }

    fn class(c: char) -> u8 {
        if c.is_whitespace() {
            0
        } else if c.is_alphanumeric() || c == '_' {
            1
        } else {
            2
        }
    }

    fn next(&self, p: Pos) -> Option<Pos> {
        if p.col < self.line_len(p.row) {
            Some(Pos::new(p.row, p.col + 1))
        } else if p.row < self.last_row() {
            Some(Pos::new(p.row + 1, 0))
        } else {
            None
        }
    }

    fn prev(&self, p: Pos) -> Option<Pos> {
        if p.col > 0 {
            Some(Pos::new(p.row, p.col - 1))
        } else if p.row > 0 {
            Some(Pos::new(p.row - 1, self.line_len(p.row - 1)))
        } else {
            None
        }
    }

    /// Start of the next word (vim `w`).
    pub fn word_forward(&self, from: Pos) -> Pos {
        let mut p = from;
        let start = self.char_at(p).map(Self::class);
        if let Some(cls) = start.filter(|c| *c != 0) {
            while let Some(c) = self.char_at(p) {
                if Self::class(c) != cls {
                    break;
                }
                match self.next(p) {
                    Some(n) => p = n,
                    None => return Pos::new(p.row, self.line_len(p.row)),
                }
            }
        }
        while let Some(c) = self.char_at(p) {
            if !c.is_whitespace() || (p.col == 0 && self.line_len(p.row) == 0 && p != from) {
                break;
            }
            match self.next(p) {
                Some(n) => p = n,
                None => break,
            }
        }
        p
    }

    /// Start of the current or previous word (vim `b`).
    pub fn word_back(&self, from: Pos) -> Pos {
        let Some(mut p) = self.prev(from) else { return from };
        while self.char_at(p).is_some_and(char::is_whitespace) {
            match self.prev(p) {
                Some(q) => p = q,
                None => return p,
            }
        }
        let cls = self.char_at(p).map(Self::class);
        while let Some(q) = self.prev(p) {
            if q.row != p.row || self.char_at(q).map(Self::class) != cls {
                break;
            }
            p = q;
        }
        p
    }

    /// End of the current or next word (vim `e`).
    pub fn word_end(&self, from: Pos) -> Pos {
        let Some(mut p) = self.next(from) else { return from };
        while self.char_at(p).is_some_and(char::is_whitespace) {
            match self.next(p) {
                Some(q) => p = q,
                None => return p,
            }
        }
        let cls = self.char_at(p).map(Self::class);
        while let Some(q) = self.next(p) {
            if q.row != p.row || self.char_at(q).map(Self::class) != cls {
                break;
            }
            p = q;
        }
        p
    }

    // ---- undo -----------------------------------------------------------

    fn checkpoint(&mut self, group: Group) {
        if group == Group::Typing && self.last_group == Some(Group::Typing) {
            return;
        }
        self.undo.push(Snap { lines: self.lines.clone(), cur: self.cur });
        if self.undo.len() > 500 {
            self.undo.remove(0);
        }
        self.redo.clear();
        self.last_group = Some(group);
        self.dirty = true;
    }

    /// End the current typing group so the next edit starts a new undo step.
    pub fn break_group(&mut self) {
        self.last_group = None;
    }

    pub fn undo(&mut self) {
        if let Some(s) = self.undo.pop() {
            self.redo.push(Snap { lines: std::mem::take(&mut self.lines), cur: self.cur });
            self.lines = s.lines;
            self.cur = self.clamp(s.cur);
            self.anchor = None;
            self.last_group = None;
            self.dirty = true;
        } else {
            self.message = Some("nothing to undo".into());
        }
    }

    pub fn redo(&mut self) {
        if let Some(s) = self.redo.pop() {
            self.undo.push(Snap { lines: std::mem::take(&mut self.lines), cur: self.cur });
            self.lines = s.lines;
            self.cur = self.clamp(s.cur);
            self.anchor = None;
            self.last_group = None;
            self.dirty = true;
        } else {
            self.message = Some("nothing to redo".into());
        }
    }

    // ---- edits (callers checkpoint first) -------------------------------

    pub fn insert_str(&mut self, s: &str) {
        let at = self.byte(self.cur);
        let rest = self.lines[self.cur.row].split_off(at);
        let mut parts = s.split('\n');
        let first = parts.next().unwrap_or("");
        self.lines[self.cur.row].push_str(first);
        let mut row = self.cur.row;
        let mut col = self.cur.col + first.chars().count();
        for part in parts {
            row += 1;
            self.lines.insert(row, part.to_string());
            col = part.chars().count();
        }
        self.lines[row].push_str(&rest);
        self.cur = Pos::new(row, col);
        self.want_col = col;
    }

    pub fn insert_char(&mut self, c: char) {
        self.insert_str(&c.to_string());
    }

    /// Newline that keeps indentation and indents after a trailing colon.
    pub fn newline(&mut self) {
        let row = self.cur.row;
        let before: String = self.lines[row].chars().take(self.cur.col).collect();
        let mut indent = self.indent_of(row).min(self.cur.col);
        if before.trim_end().ends_with(':') {
            indent += INDENT;
        }
        // drop spaces right after the cursor so the new line starts at the indent
        let at = self.byte(self.cur);
        let trailing = self.lines[row][at..].chars().take_while(|c| *c == ' ').count();
        if trailing > 0 {
            let end = self.byte(Pos::new(row, self.cur.col + trailing));
            self.lines[row].replace_range(at..end, "");
        }
        self.insert_str(&format!("\n{}", " ".repeat(indent)));
    }

    /// Delete [a, b) where b may be on a later row.
    pub fn delete_range(&mut self, a: Pos, b: Pos) -> String {
        let (a, b) = if a <= b { (a, b) } else { (b, a) };
        let a = self.clamp(a);
        let b = self.clamp(b);
        let removed = self.text_range(a, b);
        if a.row == b.row {
            let (x, y) = (self.byte(a), self.byte(b));
            self.lines[a.row].replace_range(x..y, "");
        } else {
            let tail = self.lines[b.row][self.byte(b)..].to_string();
            let x = self.byte(a);
            self.lines[a.row].truncate(x);
            self.lines[a.row].push_str(&tail);
            self.lines.drain(a.row + 1..=b.row);
        }
        self.cur = a;
        self.want_col = a.col;
        removed
    }

    pub fn text_range(&self, a: Pos, b: Pos) -> String {
        let (a, b) = if a <= b { (a, b) } else { (b, a) };
        if a.row == b.row {
            return self.lines[a.row].chars().skip(a.col).take(b.col - a.col).collect();
        }
        let mut s: String = self.lines[a.row].chars().skip(a.col).collect();
        for row in a.row + 1..b.row {
            s.push('\n');
            s.push_str(&self.lines[row]);
        }
        s.push('\n');
        s.extend(self.lines[b.row].chars().take(b.col));
        s
    }

    pub fn backspace(&mut self) {
        if self.cur.col == 0 {
            if self.cur.row > 0 {
                let p = Pos::new(self.cur.row - 1, self.line_len(self.cur.row - 1));
                self.delete_range(p, self.cur);
            }
            return;
        }
        let ind = self.indent_of(self.cur.row);
        if self.cur.col <= ind && self.cur.col > 0 {
            let to = (self.cur.col - 1) / INDENT * INDENT;
            self.delete_range(Pos::new(self.cur.row, to), self.cur);
        } else {
            self.delete_range(Pos::new(self.cur.row, self.cur.col - 1), self.cur);
        }
    }

    pub fn delete_forward(&mut self) {
        if let Some(n) = self.next(self.cur) {
            self.delete_range(self.cur, n);
        }
    }

    pub fn selection(&self) -> Option<(Pos, Pos)> {
        let a = self.anchor?;
        Some(if a <= self.cur { (a, self.cur) } else { (self.cur, a) })
    }

    /// Delete the selection if any. Returns whether something was deleted.
    pub fn delete_selection(&mut self) -> bool {
        match self.selection() {
            Some((a, b)) if a != b => {
                self.delete_range(a, b);
                self.anchor = None;
                true
            }
            _ => {
                self.anchor = None;
                false
            }
        }
    }

    /// Remove whole lines r0..=r1 and return their text.
    pub fn delete_lines(&mut self, r0: usize, r1: usize) -> String {
        let r1 = r1.min(self.last_row());
        let text = self.lines[r0..=r1].join("\n");
        self.lines.drain(r0..=r1);
        if self.lines.is_empty() {
            self.lines.push(String::new());
        }
        let row = r0.min(self.last_row());
        self.cur = Pos::new(row, self.indent_of(row));
        self.want_col = self.cur.col;
        text
    }

    pub fn indent_lines(&mut self, r0: usize, r1: usize, by: i64) {
        for row in r0..=r1.min(self.last_row()) {
            if by > 0 {
                if !self.lines[row].is_empty() {
                    self.lines[row].insert_str(0, &" ".repeat(INDENT));
                }
            } else {
                let n = self.indent_of(row).min(INDENT);
                self.lines[row].replace_range(..n, "");
            }
        }
        self.cur = self.clamp(self.cur);
    }

    /// Put register contents after (or before) the cursor.
    pub fn put(&mut self, after: bool) {
        let reg = self.register.clone();
        if reg.text.is_empty() {
            return;
        }
        if reg.linewise {
            let row = if after { self.cur.row + 1 } else { self.cur.row };
            for (i, l) in reg.text.split('\n').enumerate() {
                self.lines.insert(row + i, l.to_string());
            }
            self.cur = Pos::new(row, self.indent_of(row));
        } else {
            if after && self.line_len(self.cur.row) > 0 {
                self.cur.col = (self.cur.col + 1).min(self.line_len(self.cur.row));
            }
            self.insert_str(&reg.text);
            self.cur.col = self.cur.col.saturating_sub(1);
        }
        self.want_col = self.cur.col;
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn insert_and_newline_auto_indent() {
        let mut e = Editor::new("", KeymapKind::Standard);
        e.insert_str("def f(x):");
        e.newline();
        e.insert_str("return x");
        assert_eq!(e.text(), "def f(x):\n    return x\n");
        e.newline();
        assert_eq!(e.cur, Pos::new(2, 4));
    }

    #[test]
    fn backspace_dedents_by_indent_width() {
        let mut e = Editor::new("        x", KeymapKind::Standard);
        e.move_to(Pos::new(0, 8));
        e.backspace();
        assert_eq!(e.lines[0], "    x");
        e.backspace();
        assert_eq!(e.lines[0], "x");
    }

    #[test]
    fn delete_range_across_lines_and_undo() {
        let mut e = Editor::new("abc\ndef\nghi", KeymapKind::Standard);
        e.checkpoint(Group::Other);
        let removed = e.delete_range(Pos::new(0, 1), Pos::new(2, 1));
        assert_eq!(removed, "bc\ndef\ng");
        assert_eq!(e.text(), "ahi\n");
        e.undo();
        assert_eq!(e.text(), "abc\ndef\nghi\n");
        e.redo();
        assert_eq!(e.text(), "ahi\n");
    }

    #[test]
    fn word_motions() {
        let e = Editor::new("foo.bar  baz\nqux", KeymapKind::Vim);
        assert_eq!(e.word_forward(Pos::new(0, 0)), Pos::new(0, 3));
        assert_eq!(e.word_forward(Pos::new(0, 3)), Pos::new(0, 4));
        assert_eq!(e.word_forward(Pos::new(0, 4)), Pos::new(0, 9));
        assert_eq!(e.word_forward(Pos::new(0, 9)), Pos::new(1, 0));
        assert_eq!(e.word_end(Pos::new(0, 0)), Pos::new(0, 2));
        assert_eq!(e.word_back(Pos::new(0, 9)), Pos::new(0, 4));
        assert_eq!(e.word_back(Pos::new(1, 0)), Pos::new(0, 9));
    }
}
