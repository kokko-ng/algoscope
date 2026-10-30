//! Renders trace frames: one block per declared view, plus op/return line, locals and call stack.

pub mod diagram;
mod graph;
mod nodes;

use ratatui::buffer::Buffer;
use ratatui::layout::Rect;
use ratatui::style::{Modifier, Style};
use ratatui::text::{Line, Span};
use unicode_width::UnicodeWidthStr;

use crate::content::{ViewKind, ViewSpec};
use crate::runner::trace::{Frame, SeqKind, V};
use crate::tui::theme::Theme;

/// Everything a view needs to draw one frame.
pub struct Ctx<'a> {
    pub theme: &'a Theme,
    pub frame: &'a Frame,
    pub prev: Option<&'a Frame>,
    /// Tween progress 0.0..=1.0 since the frame changed.
    pub tween: f64,
}

impl Ctx<'_> {
    fn reads(&self, name: &str) -> Vec<i64> {
        self.frame.reads.iter().filter(|(n, _)| n == name).map(|(_, i)| *i).collect()
    }

    fn writes(&self, name: &str) -> Vec<i64> {
        self.frame.writes.iter().filter(|(n, _)| n == name).map(|(_, i)| *i).collect()
    }

    fn prev_var(&self, name: &str) -> Option<&V> {
        self.prev.and_then(|p| p.var(name))
    }

    fn int(&self, name: &str) -> Option<i64> {
        self.frame.var(name).and_then(V::as_int)
    }

    fn prev_int(&self, name: &str) -> Option<i64> {
        self.prev_var(name).and_then(V::as_int)
    }
}

pub fn put(buf: &mut Buffer, area: Rect, x: u16, y: u16, s: &str, style: Style) {
    if y < area.y || y >= area.bottom() || x >= area.right() {
        return;
    }
    let max = (area.right() - x) as usize;
    let mut text = String::new();
    let mut w = 0;
    for ch in s.chars() {
        let cw = unicode_width::UnicodeWidthChar::width(ch).unwrap_or(1);
        if w + cw > max {
            break;
        }
        text.push(ch);
        w += cw;
    }
    buf.set_string(x, y, text, style);
}

fn items(v: &V) -> Option<&[V]> {
    match v {
        V::Seq { items, .. } => Some(items),
        _ => None,
    }
}

/// Height a view wants for a frame at a given width.
fn view_height(spec: &ViewSpec, ctx: &Ctx, width: u16) -> u16 {
    let v = ctx.frame.var(&spec.var);
    let Some(v) = v else { return 1 };
    match spec.kind {
        ViewKind::Value | ViewKind::Set => 1,
        ViewKind::Array => 5 + pointer_rows(spec, ctx),
        ViewKind::Bars => 10 + pointer_rows(spec, ctx),
        ViewKind::Grid => 2 + items(v).map_or(0, |r| r.len().min(14) as u16),
        ViewKind::Map => 1 + map_len(v).min(10) as u16,
        ViewKind::Buckets => 1 + items(v).map_or(0, |r| r.len().min(16) as u16),
        ViewKind::Stack => 2 + items(v).map_or(0, |r| r.len().min(12) as u16),
        ViewKind::Queue => 4,
        ViewKind::Linked => 5,
        ViewKind::Tree | ViewKind::Heap => nodes::tree_height(spec, ctx, width),
        ViewKind::Trie => nodes::trie_height(spec, ctx),
        ViewKind::Graph => graph::height(spec, ctx),
    }
}

fn map_len(v: &V) -> usize {
    match v {
        V::Dict { items, .. } => items.len(),
        _ => 0,
    }
}

fn pointer_rows(spec: &ViewSpec, ctx: &Ctx) -> u16 {
    let present = spec.pointers.iter().filter(|p| ctx.int(p).is_some()).count() as u16;
    present.clamp(1, 3)
}

pub struct VizView<'a> {
    pub ctx: Ctx<'a>,
    pub views: &'a [ViewSpec],
    pub caption: Option<&'a str>,
}

impl VizView<'_> {
    pub fn render(&self, area: Rect, buf: &mut Buffer) {
        let ctx = &self.ctx;
        let t = ctx.theme;
        let f = ctx.frame;
        let mut y = area.y;
        let stack_w = if f.stack.len() > 1 && area.width > 70 { 30.min(area.width / 3) } else { 0 };
        let main = Rect { width: area.width - stack_w, ..area };

        if let Some(cap) = self.caption {
            for line in wrap(cap, main.width.saturating_sub(2) as usize).into_iter().take(3) {
                put(buf, main, main.x + 1, y, &line, t.bold(t.accent2));
                y += 1;
            }
        }
        let mut status: Vec<Span> = Vec::new();
        if let Some(op) = &f.op {
            status.push(Span::styled(format!("op {op}  "), t.bold(t.warn)));
        }
        if f.ev == "return" {
            let ret = f.ret.as_ref().map_or_else(|| "None".into(), |r| f.label(r));
            let func = f.stack.last().map_or("?", |s| s.func.as_str());
            status.push(Span::styled(format!("{func} returns {ret}"), t.bold(t.good)));
        }
        if !status.is_empty() {
            buf.set_line(main.x + 1, y, &Line::from(status), main.width.saturating_sub(1));
            y += 1;
        }

        let locals_h = 1;
        for spec in self.views {
            if y + 1 >= main.bottom().saturating_sub(locals_h) {
                break;
            }
            let h = view_height(spec, ctx, main.width).min(main.bottom().saturating_sub(locals_h) - y);
            let r = Rect { x: main.x + 1, y, width: main.width.saturating_sub(2), height: h };
            render_view(spec, ctx, r, buf);
            y += h + u16::from(h > 1);
        }

        // locals strip on the last line
        let ly = main.bottom().saturating_sub(1);
        if ly > area.y {
            let mut spans = vec![Span::styled("locals ", t.dim())];
            for (name, v) in &f.locals {
                if self.views.iter().any(|s| s.var == *name) {
                    continue;
                }
                let changed = ctx.prev.is_some_and(|p| p.var(name) != Some(v));
                let style = if changed { t.bold(t.write) } else { t.text() };
                spans.push(Span::styled(format!("{name}="), t.dim()));
                spans.push(Span::styled(format!("{}  ", f.label(v)), style));
            }
            buf.set_line(main.x + 1, ly, &Line::from(spans), main.width.saturating_sub(2));
        }

        if stack_w > 0 {
            let sx = area.right() - stack_w;
            put(buf, area, sx, area.y, "call stack", t.dim());
            let rows = area.height.saturating_sub(1) as usize;
            let skip = f.stack.len().saturating_sub(rows);
            for (i, s) in f.stack.iter().skip(skip).enumerate() {
                let top = skip + i + 1 == f.stack.len();
                let style = if top { t.bold(t.accent) } else { t.dim() };
                let text = format!("{}{}({})", if top { "> " } else { "  " }, s.func, s.args);
                put(buf, area, sx, area.y + 1 + i as u16, &text, style);
            }
        }
    }
}

pub fn wrap(text: &str, width: usize) -> Vec<String> {
    let width = width.max(8);
    let mut out = Vec::new();
    for para in text.split('\n') {
        let mut line = String::new();
        for word in para.split_whitespace() {
            if !line.is_empty() && line.width() + 1 + word.width() > width {
                out.push(std::mem::take(&mut line));
            }
            if !line.is_empty() {
                line.push(' ');
            }
            line.push_str(word);
        }
        out.push(line);
    }
    out
}

fn header(spec: &ViewSpec, ctx: &Ctx, area: Rect, buf: &mut Buffer, extra: &str) {
    let t = ctx.theme;
    let name = spec.label.as_deref().unwrap_or(&spec.var);
    let changed = ctx.prev.is_some() && ctx.prev_var(&spec.var) != ctx.frame.var(&spec.var);
    let style = if changed { t.bold(t.write) } else { t.bold(t.title) };
    put(buf, area, area.x, area.y, name, style);
    if !extra.is_empty() {
        put(buf, area, area.x + name.width() as u16 + 2, area.y, extra, t.dim());
    }
}

fn render_view(spec: &ViewSpec, ctx: &Ctx, area: Rect, buf: &mut Buffer) {
    let t = ctx.theme;
    let Some(v) = ctx.frame.var(&spec.var) else {
        header(spec, ctx, area, buf, "(not assigned yet)");
        return;
    };
    match spec.kind {
        ViewKind::Value => {
            header(spec, ctx, area, buf, "");
            let name_w = spec.label.as_deref().unwrap_or(&spec.var).width() as u16;
            let changed = ctx.prev.is_some() && ctx.prev_var(&spec.var) != Some(v);
            let style = if changed { t.bold(t.write) } else { t.text() };
            put(buf, area, area.x + name_w, area.y, &format!(" = {}", ctx.frame.label(v)), style);
        }
        ViewKind::Set => {
            header(spec, ctx, area, buf, "");
            let name_w = spec.label.as_deref().unwrap_or(&spec.var).width() as u16;
            put(buf, area, area.x + name_w, area.y, &format!(" = {}", ctx.frame.label(v)), t.text());
        }
        ViewKind::Array => array(spec, ctx, v, area, buf),
        ViewKind::Bars => bars(spec, ctx, v, area, buf),
        ViewKind::Grid => grid(spec, ctx, v, area, buf),
        ViewKind::Map => map(spec, ctx, v, area, buf),
        ViewKind::Buckets => buckets(spec, ctx, v, area, buf),
        ViewKind::Stack => stack(spec, ctx, v, area, buf),
        ViewKind::Queue => queue(spec, ctx, v, area, buf),
        ViewKind::Linked => nodes::linked(spec, ctx, v, area, buf),
        ViewKind::Tree => nodes::tree(spec, ctx, v, area, buf),
        ViewKind::Heap => nodes::heap(spec, ctx, v, area, buf),
        ViewKind::Trie => nodes::trie(spec, ctx, v, area, buf),
        ViewKind::Graph => graph::render(spec, ctx, v, area, buf),
    }
}

/// Index pair exchanged between the previous and current frame, if exactly one swap happened.
fn swapped(prev: &[V], cur: &[V]) -> Option<(usize, usize)> {
    if prev.len() != cur.len() {
        return None;
    }
    let diff: Vec<usize> = (0..cur.len()).filter(|&i| prev[i] != cur[i]).collect();
    match diff.as_slice() {
        [a, b] if prev[*a] == cur[*b] && prev[*b] == cur[*a] => Some((*a, *b)),
        _ => None,
    }
}

/// First visible index so that the interesting cells fit in `fit` cells.
fn window_start(len: usize, fit: usize, focus: &[i64]) -> usize {
    if len <= fit {
        return 0;
    }
    let lo = focus.iter().copied().filter(|i| *i >= 0).min().unwrap_or(0) as usize;
    let hi = focus.iter().copied().filter(|i| *i >= 0).max().unwrap_or(0) as usize;
    let mid = usize::midpoint(lo, hi);
    mid.saturating_sub(fit / 2).min(len - fit)
}

fn lerp(a: f64, b: f64, t: f64) -> f64 {
    a + (b - a) * t.clamp(0.0, 1.0)
}

#[expect(clippy::too_many_lines, reason = "cells, swap animation and pointers share the same geometry")]
fn array(spec: &ViewSpec, ctx: &Ctx, v: &V, area: Rect, buf: &mut Buffer) {
    let t = ctx.theme;
    // strings are drawn as one cell per character
    let chars;
    let v = if let V::Str(s) = v {
        let items: Vec<V> = s.chars().map(|c| V::Str(c.to_string())).collect();
        chars = V::Seq { kind: SeqKind::List, len: items.len(), items };
        &chars
    } else {
        v
    };
    let Some(vals) = items(v) else {
        header(spec, ctx, area, buf, &v.label());
        return;
    };
    let len = match v {
        V::Seq { len, .. } => *len,
        _ => vals.len(),
    };
    header(spec, ctx, area, buf, &format!("len {len}"));
    let labels: Vec<String> = vals.iter().map(|x| ctx.frame.cell(x)).collect();
    let cw = labels.iter().map(|l| l.width()).max().unwrap_or(1).clamp(1, 8) + 2;
    let fit = ((area.width as usize).saturating_sub(4) / (cw + 1)).max(1);
    let reads = ctx.reads(&spec.var);
    let writes = ctx.writes(&spec.var);
    let mut focus: Vec<i64> = spec.pointers.iter().filter_map(|p| ctx.int(p)).collect();
    focus.extend(&reads);
    focus.extend(&writes);
    let start = window_start(vals.len(), fit, &focus);
    let end = (start + fit).min(vals.len());
    let x0 = area.x + if start > 0 { 2 } else { 0 };
    if start > 0 {
        put(buf, area, area.x, area.y + 2, "..", t.dim());
    }
    let win = spec.window.as_ref().and_then(|[a, b]| Some((ctx.int(a)?, ctx.int(b)?)));
    let swap = ctx.prev_var(&spec.var).and_then(items).and_then(|p| swapped(p, vals)).filter(|_| ctx.tween < 1.0);
    let cell_x = |i: usize| x0 + ((i - start) * (cw + 1)) as u16;

    let top = area.y + 1;
    for (i, label) in labels.iter().enumerate().take(end).skip(start) {
        let x = cell_x(i);
        let ii = i as i64;
        let in_win = win.is_some_and(|(a, b)| ii >= a.min(b) && ii <= a.max(b));
        let mut style = t.text();
        let mut border = t.dim();
        if in_win {
            style = style.bg(t.window);
            border = border.fg(t.accent2);
        }
        if reads.contains(&ii) {
            style = t.bold(t.read);
            border = Style::default().fg(t.read);
        }
        if writes.contains(&ii) {
            style = t.bold(t.write).add_modifier(Modifier::REVERSED);
            border = Style::default().fg(t.write);
        }
        let bar = "─".repeat(cw);
        let (tl, bl) = if i == start { ("┌", "└") } else { ("┬", "┴") };
        put(buf, area, x, top, &format!("{tl}{bar}"), border);
        put(buf, area, x, top + 2, &format!("{bl}{bar}"), border);
        put(buf, area, x, top + 1, "│", border);
        if i + 1 == end {
            let rx = x + cw as u16 + 1;
            put(buf, area, rx, top, "┐", border);
            put(buf, area, rx, top + 1, "│", border);
            put(buf, area, rx, top + 2, "┘", border);
        }
        let hidden = swap.is_some_and(|(a, b)| i == a || i == b);
        if !hidden {
            put(buf, area, x + 1, top + 1, &format!("{label:^cw$}"), style);
        }
        let idx = i.to_string();
        put(buf, area, x + 1 + ((cw - idx.len().min(cw)) / 2) as u16, top + 3, &idx, t.dim());
    }
    if end < vals.len() {
        put(buf, area, cell_x(end) + 1, top + 1, "..", t.dim());
    }
    // swap animation: the two values travel along the top border
    if let Some((a, b)) = swap {
        for (from, to) in [(a, b), (b, a)] {
            if from < start || from >= end || to < start || to >= end {
                continue;
            }
            let x = lerp(f64::from(cell_x(from)), f64::from(cell_x(to)), ctx.tween).round() as u16;
            let row = if ctx.tween < 0.85 { top } else { top + 1 };
            put(buf, area, x + 1, row, &format!("{:^cw$}", labels[to]), t.bold(t.write));
        }
    }
    // pointers, stacked on rows when they collide
    let mut rows: Vec<Vec<(u16, u16)>> = Vec::new();
    for name in &spec.pointers {
        let Some(i) = ctx.int(name) else { continue };
        let target = |i: i64| -> f64 {
            let i = i.clamp(start as i64 - 1, end as i64) as f64;
            f64::from(x0) + (i - start as f64) * (cw + 1) as f64 + (cw / 2 + 1) as f64
        };
        let mut x = target(i);
        if let Some(pi) = ctx.prev_int(name).filter(|p| *p != i) {
            x = lerp(target(pi), x, ctx.tween);
        }
        let x = (x.round().max(f64::from(area.x))) as u16;
        let label = format!("↑{name}");
        let w = label.width() as u16;
        let row = rows.iter().position(|r| r.iter().all(|(a, b)| x + w < *a || x > *b)).unwrap_or_else(|| {
            rows.push(Vec::new());
            rows.len() - 1
        });
        if row >= 3 {
            continue;
        }
        rows[row].push((x, x + w));
        let out_of_range = i < 0 || i >= vals.len() as i64;
        let style = if out_of_range { t.dim() } else { t.bold(t.pointer) };
        put(buf, area, x, top + 4 + row as u16, &label, style);
    }
}

fn bars(spec: &ViewSpec, ctx: &Ctx, v: &V, area: Rect, buf: &mut Buffer) {
    let t = ctx.theme;
    let Some(vals) = items(v) else { return };
    header(spec, ctx, area, buf, &format!("len {}", vals.len()));
    let nums: Vec<f64> = vals
        .iter()
        .map(|x| match x {
            V::Int(i) => *i as f64,
            V::Float(f) => *f,
            _ => 0.0,
        })
        .collect();
    let max = nums.iter().copied().fold(1.0f64, |a, b| a.max(b.abs()));
    let h = 7.0;
    let bw: usize = if vals.len() * 4 <= area.width as usize { 3 } else { 2 };
    let fit = (area.width as usize / (bw + 1)).max(1);
    let reads = ctx.reads(&spec.var);
    let writes = ctx.writes(&spec.var);
    let mut focus: Vec<i64> = spec.pointers.iter().filter_map(|p| ctx.int(p)).collect();
    focus.extend(&writes);
    let start = window_start(vals.len(), fit, &focus);
    let end = (start + fit).min(vals.len());
    let base = area.y + 8;
    let win = spec.window.as_ref().and_then(|[a, b]| Some((ctx.int(a)?, ctx.int(b)?)));
    for i in start..end {
        let x = area.x + ((i - start) * (bw + 1)) as u16;
        let ii = i as i64;
        let units = (nums[i].abs() / max * h * 8.0).round() as usize;
        let mut color = t.accent2;
        if win.is_some_and(|(a, b)| ii >= a.min(b) && ii <= a.max(b)) {
            color = t.accent;
        }
        if reads.contains(&ii) {
            color = t.read;
        }
        if writes.contains(&ii) {
            color = t.write;
        }
        for row in 0..h as usize {
            let fill = units.saturating_sub(row * 8).min(8);
            let ch = [" ", "▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"][fill];
            put(buf, area, x, base - 1 - row as u16, &ch.repeat(bw), Style::default().fg(color));
        }
        let label = ctx.frame.cell(&vals[i]);
        let label: String = label.chars().take(bw).collect();
        put(buf, area, x, base, &format!("{label:^bw$}"), t.dim());
    }
    let mut row = 0;
    for name in &spec.pointers {
        let Some(i) = ctx.int(name) else { continue };
        if i < start as i64 || i >= end as i64 || row >= 3 {
            continue;
        }
        let x = area.x + ((i as usize - start) * (bw + 1)) as u16;
        put(buf, area, x, base + 1 + row, &format!("↑{name}"), t.bold(t.pointer));
        row += 1;
    }
}

fn grid(spec: &ViewSpec, ctx: &Ctx, v: &V, area: Rect, buf: &mut Buffer) {
    let t = ctx.theme;
    let Some(rows) = items(v) else { return };
    let ncols = rows.iter().filter_map(items).map(<[V]>::len).max().unwrap_or(0);
    header(spec, ctx, area, buf, &format!("{}x{}", rows.len(), ncols));
    let cw =
        rows.iter().filter_map(items).flat_map(|r| r.iter().map(|c| c.cell().width())).max().unwrap_or(1).clamp(1, 6)
            + 1;
    let focus = match spec.pointers.as_slice() {
        [a, b, ..] => ctx.int(a).zip(ctx.int(b)),
        _ => None,
    };
    let x0 = area.x + 4;
    for c in 0..ncols {
        let x = x0 + (c * (cw + 1)) as u16;
        if x + cw as u16 > area.right() {
            break;
        }
        put(buf, area, x, area.y + 1, &format!("{c:>cw$}"), t.dim());
    }
    for (r, row) in rows.iter().enumerate().take(area.height.saturating_sub(2) as usize) {
        let y = area.y + 2 + r as u16;
        put(buf, area, area.x, y, &format!("{r:>3}"), t.dim());
        let Some(cells) = items(row) else { continue };
        let rname = format!("{}[{r}]", spec.var);
        let reads = ctx.reads(&rname);
        let writes = ctx.writes(&rname);
        let prev_row = ctx.prev_var(&spec.var).and_then(items).and_then(|p| p.get(r)).and_then(items);
        for (c, cell) in cells.iter().enumerate() {
            let x = x0 + (c * (cw + 1)) as u16;
            if x + cw as u16 > area.right() {
                break;
            }
            let ci = c as i64;
            let mut style = t.text();
            if prev_row.and_then(|p| p.get(c)).is_some_and(|p| p != cell) || writes.contains(&ci) {
                style = t.bold(t.write).add_modifier(Modifier::REVERSED);
            } else if reads.contains(&ci) {
                style = t.bold(t.read);
            }
            if focus == Some((r as i64, ci)) {
                style = style.add_modifier(Modifier::UNDERLINED).fg(t.pointer);
            }
            put(buf, area, x, y, &format!("{:>cw$}", ctx.frame.cell(cell)), style);
        }
    }
}

fn map(spec: &ViewSpec, ctx: &Ctx, v: &V, area: Rect, buf: &mut Buffer) {
    let t = ctx.theme;
    let V::Dict { items: pairs, len } = v else {
        header(spec, ctx, area, buf, &v.label());
        return;
    };
    header(spec, ctx, area, buf, &format!("{len} keys"));
    let prev: Vec<(V, V)> = match ctx.prev_var(&spec.var) {
        Some(V::Dict { items, .. }) => items.clone(),
        _ => Vec::new(),
    };
    let kw = pairs.iter().map(|(k, _)| k.label().width()).max().unwrap_or(1).min(16);
    let cols = ((area.width as usize) / (kw + 14)).max(1);
    let per_col = area.height.saturating_sub(1).max(1) as usize;
    for (i, (k, val)) in pairs.iter().enumerate().take(per_col * cols) {
        let x = area.x + ((i / per_col) * (kw + 14)) as u16;
        let y = area.y + 1 + (i % per_col) as u16;
        let old = prev.iter().find(|(pk, _)| pk == k).map(|(_, pv)| pv);
        let style = match old {
            None if ctx.prev.is_some() => t.bold(t.good),
            Some(o) if o != val => t.bold(t.write),
            _ => t.text(),
        };
        put(buf, area, x, y, &format!("{:>kw$} → {}", ctx.frame.label(k), ctx.frame.label(val)), style);
    }
}

fn buckets(spec: &ViewSpec, ctx: &Ctx, v: &V, area: Rect, buf: &mut Buffer) {
    let t = ctx.theme;
    let Some(rows) = items(v) else { return };
    header(spec, ctx, area, buf, &format!("{} buckets", rows.len()));
    let writes = ctx.writes(&spec.var);
    let reads = ctx.reads(&spec.var);
    for (i, b) in rows.iter().enumerate().take(area.height.saturating_sub(1) as usize) {
        let y = area.y + 1 + i as u16;
        let ii = i as i64;
        let idx_style = if writes.contains(&ii) {
            t.bold(t.write)
        } else if reads.contains(&ii) {
            t.bold(t.read)
        } else {
            t.dim()
        };
        put(buf, area, area.x, y, &format!("{i:>3} │"), idx_style);
        let text = match b {
            V::Seq { items, .. } if items.is_empty() => "·".to_string(),
            V::Seq { items, .. } => items.iter().map(|x| ctx.frame.label(x)).collect::<Vec<_>>().join(" → "),
            V::None => "·".to_string(),
            other => ctx.frame.label(other),
        };
        put(buf, area, area.x + 6, y, &text, t.text());
    }
}

fn stack(spec: &ViewSpec, ctx: &Ctx, v: &V, area: Rect, buf: &mut Buffer) {
    let t = ctx.theme;
    let Some(vals) = items(v) else { return };
    header(spec, ctx, area, buf, &format!("size {}", vals.len()));
    let cw = vals.iter().map(|x| ctx.frame.label(x).width()).max().unwrap_or(1).clamp(3, 14) + 2;
    let grew = ctx.prev_var(&spec.var).and_then(items).is_some_and(|p| p.len() < vals.len());
    let rows = area.height.saturating_sub(2) as usize;
    for (i, val) in vals.iter().rev().take(rows).enumerate() {
        let y = area.y + 1 + i as u16;
        let style = if i == 0 && grew { t.bold(t.write) } else { t.text() };
        put(buf, area, area.x, y, "│", t.dim());
        put(buf, area, area.x + 1, y, &format!("{:^cw$}", ctx.frame.label(val)), style);
        put(buf, area, area.x + 1 + cw as u16, y, "│", t.dim());
        if i == 0 {
            put(buf, area, area.x + 3 + cw as u16, y, "← top", t.accent());
        }
    }
    let y = area.y + 1 + vals.len().min(rows) as u16;
    put(buf, area, area.x, y, &format!("└{}┘", "─".repeat(cw)), t.dim());
}

fn queue(spec: &ViewSpec, ctx: &Ctx, v: &V, area: Rect, buf: &mut Buffer) {
    let t = ctx.theme;
    let Some(vals) = items(v) else { return };
    let kind = match v {
        V::Seq { kind: SeqKind::Deque, .. } => "deque",
        _ => "queue",
    };
    header(spec, ctx, area, buf, &format!("{kind} size {}", vals.len()));
    let mut x = area.x + 7;
    put(buf, area, area.x, area.y + 2, "front", t.accent());
    for (i, val) in vals.iter().enumerate() {
        let label = format!(" {} ", ctx.frame.label(val));
        let w = label.width() as u16;
        if x + w + 8 > area.right() {
            put(buf, area, x, area.y + 2, "..", t.dim());
            break;
        }
        let style = if i == 0 { t.bold(t.read) } else { t.text() };
        put(buf, area, x, area.y + 1, &format!("┌{}┐", "─".repeat(w as usize)), t.dim());
        put(buf, area, x, area.y + 2, &format!("│{label}│"), t.dim());
        put(buf, area, x + 1, area.y + 2, &label, style);
        put(buf, area, x, area.y + 3, &format!("└{}┘", "─".repeat(w as usize)), t.dim());
        x += w + 2;
    }
    put(buf, area, x + 1, area.y + 2, "back", t.accent());
}

#[cfg(test)]
mod tests;
