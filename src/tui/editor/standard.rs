//! Standard (non-modal) keymap: arrows, shift-select, Ctrl+C/X/V/Z/Y.

use ratatui::crossterm::event::{KeyCode, KeyEvent, KeyModifiers};

use super::{Action, Editor, Group, INDENT, Pos};

#[expect(clippy::too_many_lines, reason = "a flat key table reads better than split handlers")]
pub fn handle(e: &mut Editor, key: KeyEvent) -> Action {
    let ctrl = key.modifiers.contains(KeyModifiers::CONTROL);
    let shift = key.modifiers.contains(KeyModifiers::SHIFT);
    let alt = key.modifiers.contains(KeyModifiers::ALT);

    // movement, optionally extending the selection
    let moved = match key.code {
        KeyCode::Left
        | KeyCode::Right
        | KeyCode::Up
        | KeyCode::Down
        | KeyCode::Home
        | KeyCode::End
        | KeyCode::PageUp
        | KeyCode::PageDown => {
            if shift {
                if e.anchor.is_none() {
                    e.anchor = Some(e.cur);
                }
            } else if let (Some((a, b)), KeyCode::Left | KeyCode::Right) = (e.selection(), key.code) {
                e.anchor = None;
                e.move_to(if key.code == KeyCode::Left { a } else { b });
                return Action::None;
            } else {
                e.anchor = None;
            }
            let page = e.view_height.saturating_sub(1).max(1) as i64;
            match key.code {
                KeyCode::Left if ctrl || alt => e.move_to(e.word_back(e.cur)),
                KeyCode::Right if ctrl || alt => e.move_to(e.word_forward(e.cur)),
                KeyCode::Left => e.left(),
                KeyCode::Right => e.right(),
                KeyCode::Up => e.vertical(-1),
                KeyCode::Down => e.vertical(1),
                KeyCode::Home if ctrl => e.move_to(Pos::new(0, 0)),
                KeyCode::End if ctrl => e.move_to(Pos::new(usize::MAX, usize::MAX)),
                KeyCode::Home => e.home(),
                KeyCode::End => e.end(),
                KeyCode::PageUp => e.vertical(-page),
                KeyCode::PageDown => e.vertical(page),
                _ => {}
            }
            e.break_group();
            true
        }
        _ => false,
    };
    if moved {
        return Action::None;
    }

    if ctrl {
        return match key.code {
            KeyCode::Char('e') => Action::Run,
            KeyCode::Char('t') => Action::Submit,
            KeyCode::Char('s') => Action::Save,
            KeyCode::Char('q') => Action::Quit,
            KeyCode::Char('a') => {
                e.anchor = Some(Pos::new(0, 0));
                e.move_to(Pos::new(usize::MAX, usize::MAX));
                Action::None
            }
            KeyCode::Char('c') => {
                copy(e, false);
                Action::None
            }
            KeyCode::Char('x') if !e.readonly => {
                copy(e, true);
                Action::None
            }
            KeyCode::Char('v') if !e.readonly => {
                let reg = e.register.clone();
                e.checkpoint(Group::Other);
                e.delete_selection();
                if reg.linewise {
                    e.cur.col = 0;
                    e.insert_str(&format!("{}\n", reg.text));
                } else {
                    e.insert_str(&reg.text);
                }
                Action::None
            }
            KeyCode::Char('z') if !e.readonly => {
                e.undo();
                Action::None
            }
            KeyCode::Char('y') if !e.readonly => {
                e.redo();
                Action::None
            }
            KeyCode::Char('d') if !e.readonly => {
                e.checkpoint(Group::Other);
                let line = e.lines[e.cur.row].clone();
                e.lines.insert(e.cur.row + 1, line);
                e.cur.row += 1;
                Action::None
            }
            _ => Action::Unhandled,
        };
    }

    if key.code == KeyCode::Esc {
        if e.anchor.take().is_some() {
            return Action::None;
        }
        return Action::Leave;
    }

    if e.readonly {
        return Action::Unhandled;
    }

    match key.code {
        KeyCode::Char(c) => {
            if e.selection().is_some_and(|(a, b)| a != b) {
                e.checkpoint(Group::Other);
                e.delete_selection();
            } else {
                e.anchor = None;
                e.checkpoint(Group::Typing);
            }
            e.insert_char(c);
            if c == ' ' || c == '(' {
                e.break_group();
            }
        }
        KeyCode::Enter => {
            e.checkpoint(Group::Other);
            e.delete_selection();
            e.newline();
        }
        KeyCode::Backspace => {
            e.checkpoint(Group::Other);
            if !e.delete_selection() {
                e.backspace();
            }
        }
        KeyCode::Delete => {
            e.checkpoint(Group::Other);
            if !e.delete_selection() {
                e.delete_forward();
            }
        }
        KeyCode::Tab => {
            e.checkpoint(Group::Other);
            if let Some((a, b)) = e.selection().filter(|(a, b)| a.row != b.row) {
                e.indent_lines(a.row, b.row, 1);
            } else {
                e.anchor = None;
                let n = INDENT - e.cur.col % INDENT;
                e.insert_str(&" ".repeat(n));
            }
        }
        KeyCode::BackTab => {
            e.checkpoint(Group::Other);
            let (r0, r1) = e.selection().map_or((e.cur.row, e.cur.row), |(a, b)| (a.row, b.row));
            e.indent_lines(r0, r1, -1);
        }
        _ => return Action::Unhandled,
    }
    Action::None
}

fn copy(e: &mut Editor, cut: bool) {
    if let Some((a, b)) = e.selection().filter(|(a, b)| a != b) {
        e.register.text = e.text_range(a, b);
        e.register.linewise = false;
        if cut {
            e.checkpoint(Group::Other);
            e.delete_range(a, b);
            e.anchor = None;
        }
    } else {
        e.register.text = e.lines[e.cur.row].clone();
        e.register.linewise = true;
        if cut {
            e.checkpoint(Group::Other);
            e.delete_lines(e.cur.row, e.cur.row);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::progress::KeymapKind;
    use ratatui::crossterm::event::KeyEvent;

    fn press(e: &mut Editor, code: KeyCode, mods: KeyModifiers) -> Action {
        e.handle_key(KeyEvent::new(code, mods))
    }

    fn typ(e: &mut Editor, s: &str) {
        for c in s.chars() {
            if c == '\n' {
                press(e, KeyCode::Enter, KeyModifiers::NONE);
            } else {
                press(e, KeyCode::Char(c), KeyModifiers::NONE);
            }
        }
    }

    #[test]
    fn typing_with_auto_indent_and_undo() {
        let mut e = Editor::new("", KeymapKind::Standard);
        typ(&mut e, "def f():\nreturn 1");
        assert_eq!(e.text(), "def f():\n    return 1\n");
        press(&mut e, KeyCode::Char('z'), KeyModifiers::CONTROL);
        assert_eq!(e.text(), "def f():\n    return \n");
    }

    #[test]
    fn shift_select_cut_paste() {
        let mut e = Editor::new("hello world", KeymapKind::Standard);
        for _ in 0..5 {
            press(&mut e, KeyCode::Right, KeyModifiers::SHIFT);
        }
        press(&mut e, KeyCode::Char('x'), KeyModifiers::CONTROL);
        assert_eq!(e.text(), " world\n");
        press(&mut e, KeyCode::End, KeyModifiers::NONE);
        press(&mut e, KeyCode::Char('v'), KeyModifiers::CONTROL);
        assert_eq!(e.text(), " worldhello\n");
    }

    #[test]
    fn global_actions_and_escape() {
        let mut e = Editor::new("x", KeymapKind::Standard);
        assert_eq!(press(&mut e, KeyCode::Char('e'), KeyModifiers::CONTROL), Action::Run);
        assert_eq!(press(&mut e, KeyCode::Char('t'), KeyModifiers::CONTROL), Action::Submit);
        assert_eq!(press(&mut e, KeyCode::Esc, KeyModifiers::NONE), Action::Leave);
    }

    #[test]
    fn tab_indents_selected_lines() {
        let mut e = Editor::new("a\nb", KeymapKind::Standard);
        press(&mut e, KeyCode::Down, KeyModifiers::SHIFT);
        press(&mut e, KeyCode::Tab, KeyModifiers::NONE);
        assert_eq!(e.text(), "    a\n    b\n");
        press(&mut e, KeyCode::BackTab, KeyModifiers::SHIFT);
        assert_eq!(e.text(), "a\nb\n");
    }
}
