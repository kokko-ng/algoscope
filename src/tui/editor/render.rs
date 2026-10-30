//! Draws the editor: gutter with trace markers, highlighted code, selection and cursor.

use ratatui::buffer::Buffer;
use ratatui::layout::Rect;
use ratatui::style::{Modifier, Style};
use ratatui::text::{Line, Span};
use ratatui::widgets::{Block, Borders, Widget};
use unicode_width::UnicodeWidthChar;

use super::highlight::{Tok, highlight};
use super::{Editor, Pos, VimMode};
use crate::tui::theme::Theme;

pub struct EditorView<'a> {
    pub ed: &'a Editor,
    pub theme: &'a Theme,
    pub focused: bool,
    pub title: String,
    /// Line about to execute in the current trace frame (1-based).
    pub exec_line: Option<u32>,
    /// Line that just executed (1-based).
    pub prev_line: Option<u32>,
    pub error_line: Option<u32>,
}

impl EditorView<'_> {
    /// Inner text area (excluding border and gutter) for a given outer area.
    pub fn text_area(area: Rect, lines: usize) -> (u16, u16) {
        let gutter = gutter_width(lines);
        (area.width.saturating_sub(2 + gutter), area.height.saturating_sub(2))
    }
}

fn gutter_width(lines: usize) -> u16 {
    lines.max(1).to_string().len().max(2) as u16 + 3
}

impl Widget for EditorView<'_> {
    fn render(self, area: Rect, buf: &mut Buffer) {
        let t = self.theme;
        let ed = self.ed;
        let mut block = Block::default()
            .borders(Borders::ALL)
            .border_style(t.border(self.focused))
            .title(Span::styled(format!(" {} ", self.title), t.title(self.focused)));
        let mut status = Vec::new();
        if let Some(mode) = ed.mode_label() {
            let style = match ed.vim.mode {
                VimMode::Insert => t.bold(t.good),
                VimMode::Visual | VimMode::VisualLine => t.bold(t.warn),
                _ => t.bold(t.accent),
            };
            status.push(Span::styled(format!(" {mode} "), style));
        }
        if ed.vim.mode == VimMode::Command {
            status.push(Span::styled(format!(":{}", ed.vim.cmdline), t.text()));
        } else if let Some(msg) = &ed.message {
            status.push(Span::styled(format!(" {msg} "), t.dim()));
        }
        if ed.readonly {
            status.push(Span::styled(" read-only ", t.dim()));
        }
        status.push(Span::styled(format!(" {}:{} ", ed.cur.row + 1, ed.cur.col + 1), t.dim()));
        block = block.title_bottom(Line::from(status));
        let inner = block.inner(area);
        block.render(area, buf);

        let gw = gutter_width(ed.lines.len());
        let toks = highlight(&ed.lines);
        let sel = if ed.vim.mode == VimMode::VisualLine {
            ed.anchor.map(|a| {
                let (r0, r1) = if a.row <= ed.cur.row { (a.row, ed.cur.row) } else { (ed.cur.row, a.row) };
                (Pos::new(r0, 0), Pos::new(r1, usize::MAX))
            })
        } else {
            ed.selection().map(|(a, b)| {
                // vim visual mode is inclusive of the cursor char
                if ed.keymap == crate::progress::KeymapKind::Vim { (a, Pos::new(b.row, b.col + 1)) } else { (a, b) }
            })
        };

        for screen_row in 0..inner.height as usize {
            let row = ed.scroll_row + screen_row;
            let y = inner.y + screen_row as u16;
            if row >= ed.lines.len() {
                buf.set_string(inner.x, y, format!("{:>w$}", "~", w = gw as usize - 2), t.dim());
                continue;
            }
            let line_no = row as u32 + 1;
            let is_exec = self.exec_line == Some(line_no);
            let is_prev = self.prev_line == Some(line_no) && !is_exec;
            let is_err = self.error_line == Some(line_no);
            let marker = if is_err {
                Span::styled("!", t.bold(t.bad))
            } else if is_exec {
                Span::styled(if t.is_game() { "▶" } else { ">" }, t.bold(t.accent))
            } else if is_prev {
                Span::styled("·", t.dim())
            } else {
                Span::raw(" ")
            };
            buf.set_span(inner.x, y, &marker, 1);
            let num_style = if is_exec || row == ed.cur.row { t.text() } else { t.dim() };
            buf.set_string(inner.x + 1, y, format!("{:>w$} ", line_no, w = gw as usize - 3), num_style);

            let line_bg = if is_exec {
                Some(t.exec_bg)
            } else if is_err {
                Some(ratatui::style::Color::Indexed(52))
            } else {
                None
            };
            let text_x = inner.x + gw;
            let text_w = inner.width.saturating_sub(gw) as usize;
            if let Some(bg) = line_bg {
                for x in text_x..inner.x + inner.width {
                    buf[(x, y)].set_bg(bg);
                }
            }
            let mut x = 0usize;
            for (col, ch) in ed.lines[row].chars().enumerate().skip(ed.scroll_col) {
                let w = ch.width().unwrap_or(1);
                if x + w > text_w {
                    break;
                }
                let tok = toks[row].get(col).copied().unwrap_or(Tok::Text);
                let mut style = Style::default().fg(match tok {
                    Tok::Keyword => t.kw,
                    Tok::Builtin => t.builtin,
                    Tok::Str => t.string,
                    Tok::Number => t.number,
                    Tok::Comment => t.comment,
                    Tok::Func => t.func,
                    Tok::Decorator => t.func,
                    Tok::Text => t.fg,
                });
                if tok == Tok::Keyword {
                    style = style.add_modifier(Modifier::BOLD);
                }
                if let Some(bg) = line_bg {
                    style = style.bg(bg);
                }
                let p = Pos::new(row, col);
                if sel.is_some_and(|(a, b)| p >= a && p < b) {
                    style = style.bg(t.sel_bg);
                }
                buf.set_string(text_x + x as u16, y, ch.to_string(), style);
                x += w;
            }
            if self.focused && row == ed.cur.row && ed.cur.col >= ed.scroll_col {
                let cx = ed.lines[row]
                    .chars()
                    .skip(ed.scroll_col)
                    .take(ed.cur.col - ed.scroll_col)
                    .map(|c| c.width().unwrap_or(1))
                    .sum::<usize>();
                if cx < text_w {
                    let cell = &mut buf[(text_x + cx as u16, y)];
                    let insertish = ed.keymap == crate::progress::KeymapKind::Standard || ed.vim.mode == VimMode::Insert;
                    if insertish {
                        cell.set_style(Style::default().add_modifier(Modifier::REVERSED | Modifier::SLOW_BLINK));
                    } else {
                        cell.set_style(Style::default().add_modifier(Modifier::REVERSED));
                    }
                    if cell.symbol() == " " || cell.symbol().is_empty() {
                        cell.set_symbol(" ");
                    }
                }
            }
        }
    }
}
