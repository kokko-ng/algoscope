//! Node-based views: linked lists, binary trees, array-backed heaps and tries.

use std::collections::{HashMap, HashSet};

use ratatui::buffer::Buffer;
use ratatui::layout::Rect;
use unicode_width::UnicodeWidthStr;

use super::{Ctx, header, items, put};
use crate::content::ViewSpec;
use crate::runner::trace::{Frame, V};

const MAX_DEPTH: usize = 7;
const MAX_NODES: usize = 80;

fn node_val(frame: &Frame, id: u64) -> String {
    frame
        .heap
        .get(&id)
        .and_then(|o| o.field("val").or_else(|| o.field("key")).or_else(|| o.field("value")))
        .map_or("?".into(), V::cell)
}

/// Pointer variables that hold node references: node id -> names.
fn ref_pointers(spec: &ViewSpec, ctx: &Ctx) -> HashMap<u64, Vec<String>> {
    let mut out: HashMap<u64, Vec<String>> = HashMap::new();
    for name in &spec.pointers {
        if let Some(V::Ref(id)) = ctx.frame.var(name) {
            out.entry(*id).or_default().push(name.clone());
        }
    }
    out
}

pub fn linked(spec: &ViewSpec, ctx: &Ctx, v: &V, area: Rect, buf: &mut Buffer) {
    let t = ctx.theme;
    let ptrs = ref_pointers(spec, ctx);
    let mut x = area.x;
    let y = area.y + 2;
    let mut seen = HashSet::new();
    let mut cur = v.clone();
    let mut count = 0;
    let prev_ids: HashSet<u64> = ctx
        .prev
        .map(|p| p.heap.keys().copied().collect())
        .unwrap_or_default();
    loop {
        match cur {
            V::Ref(id) => {
                if !seen.insert(id) {
                    put(buf, area, x, y, &format!("↺ back to {}", node_val(ctx.frame, id)), t.bold(t.warn));
                    break;
                }
                let label = format!("[{}]", node_val(ctx.frame, id));
                let w = label.width() as u16;
                if x + w + 3 > area.right() {
                    put(buf, area, x, y, "...", t.dim());
                    break;
                }
                let names = ptrs.get(&id);
                let new = ctx.prev.is_some() && !prev_ids.contains(&id);
                let style = if names.is_some() {
                    t.bold(t.pointer)
                } else if new {
                    t.bold(t.good)
                } else {
                    t.text()
                };
                put(buf, area, x, y, &label, style);
                if let Some(names) = names {
                    put(buf, area, x, y - 1, &format!("↓{}", names.join(",")), t.bold(t.pointer));
                }
                x += w;
                let next = ctx
                    .frame
                    .heap
                    .get(&id)
                    .and_then(|o| o.field("next"))
                    .cloned()
                    .unwrap_or(V::None);
                put(buf, area, x, y, "─▶", t.dim());
                x += 2;
                cur = next;
                count += 1;
                if count > 40 {
                    put(buf, area, x, y, "...", t.dim());
                    break;
                }
            }
            _ => {
                put(buf, area, x, y, "None", t.dim());
                break;
            }
        }
    }
    let dangling: Vec<String> = spec
        .pointers
        .iter()
        .filter(|n| matches!(ctx.frame.var(n), Some(V::None)))
        .cloned()
        .collect();
    let mut extra = String::new();
    if !dangling.is_empty() {
        extra = format!("{} = None", dangling.join(", "));
    }
    header(spec, ctx, area, buf, &extra);
    // pointers to nodes that are no longer reachable from the head
    let off: Vec<String> = ptrs
        .iter()
        .filter(|(id, _)| !seen.contains(id))
        .map(|(id, n)| format!("{} → [{}]", n.join(","), node_val(ctx.frame, *id)))
        .collect();
    if !off.is_empty() {
        put(buf, area, area.x, y + 1, &off.join("   "), t.dim());
    }
}

/// A laid-out binary tree node.
struct TNode {
    label: String,
    depth: usize,
    x: usize,
    left: Option<usize>,
    right: Option<usize>,
    /// Ref id or array index used to match pointers and reads.
    key: i64,
}

fn build_ref_tree(frame: &Frame, root: &V) -> Vec<TNode> {
    fn go(frame: &Frame, v: &V, depth: usize, nodes: &mut Vec<TNode>, seen: &mut HashSet<u64>) -> Option<usize> {
        let V::Ref(id) = v else { return None };
        if depth > MAX_DEPTH || nodes.len() >= MAX_NODES || !seen.insert(*id) {
            return None;
        }
        let obj = frame.heap.get(id)?;
        let idx = nodes.len();
        nodes.push(TNode { label: node_val(frame, *id), depth, x: 0, left: None, right: None, key: *id as i64 });
        let l = obj.field("left").cloned().unwrap_or(V::None);
        let r = obj.field("right").cloned().unwrap_or(V::None);
        nodes[idx].left = go(frame, &l, depth + 1, nodes, seen);
        nodes[idx].right = go(frame, &r, depth + 1, nodes, seen);
        Some(idx)
    }
    let mut nodes = Vec::new();
    go(frame, root, 0, &mut nodes, &mut HashSet::new());
    nodes
}

fn build_array_tree(vals: &[V]) -> Vec<TNode> {
    let n = vals.len().min(63);
    let mut nodes: Vec<TNode> = (0..n)
        .map(|i| TNode {
            label: vals[i].cell(),
            depth: (usize::BITS - (i + 1).leading_zeros() - 1) as usize,
            x: 0,
            left: (2 * i + 1 < n).then_some(2 * i + 1),
            right: (2 * i + 2 < n).then_some(2 * i + 2),
            key: i as i64,
        })
        .collect();
    nodes.truncate(n);
    nodes
}

/// Assign x positions by in-order rank so subtrees never overlap.
fn layout(nodes: &mut [TNode]) -> usize {
    fn go(nodes: &mut [TNode], i: usize, next: &mut usize) {
        if let Some(l) = nodes[i].left {
            go(nodes, l, next);
        }
        nodes[i].x = *next;
        *next += 1;
        if let Some(r) = nodes[i].right {
            go(nodes, r, next);
        }
    }
    let mut next = 0;
    if !nodes.is_empty() {
        go(nodes, 0, &mut next);
    }
    next
}

fn depth_of(nodes: &[TNode]) -> usize {
    nodes.iter().map(|n| n.depth + 1).max().unwrap_or(0)
}

pub fn tree_height(spec: &ViewSpec, ctx: &Ctx, _width: u16) -> u16 {
    let Some(v) = ctx.frame.var(&spec.var) else { return 1 };
    let (d, extra) = match spec.kind {
        crate::content::ViewKind::Heap => (depth_of(&build_array_tree(items(v).unwrap_or(&[]))), 3),
        _ => (depth_of(&build_ref_tree(ctx.frame, v)), 0),
    };
    (1 + d.max(1) * 2 + extra) as u16
}

fn draw_tree(nodes: &mut [TNode], ctx: &Ctx, area: Rect, buf: &mut Buffer, hot: &HashMap<i64, Style2>) {
    let t = ctx.theme;
    if nodes.is_empty() {
        put(buf, area, area.x, area.y, "(empty)", t.dim());
        return;
    }
    let count = layout(nodes);
    let lw = nodes.iter().map(|n| n.label.width()).max().unwrap_or(1);
    let cw = ((area.width as usize) / count.max(1)).clamp(1, lw.max(2) + 2).max(lw.min(4));
    let col = |n: &TNode| area.x as usize + n.x * cw + cw / 2;
    for n in nodes.iter() {
        let y = area.y + (n.depth * 2) as u16;
        let cx = col(n);
        // connector row below the node
        let kids: Vec<usize> = [n.left, n.right].into_iter().flatten().map(|k| col(&nodes[k])).collect();
        if !kids.is_empty() {
            let lo = kids.iter().copied().min().unwrap_or(cx).min(cx);
            let hi = kids.iter().copied().max().unwrap_or(cx).max(cx);
            for x in lo..=hi {
                put(buf, area, x as u16, y + 1, "─", t.dim());
            }
            if let Some(l) = n.left {
                put(buf, area, col(&nodes[l]) as u16, y + 1, "┌", t.dim());
            }
            if let Some(r) = n.right {
                put(buf, area, col(&nodes[r]) as u16, y + 1, "┐", t.dim());
            }
            let joint = match (n.left.is_some(), n.right.is_some()) {
                (true, true) => "┴",
                (true, false) => "┘",
                _ => "└",
            };
            put(buf, area, cx as u16, y + 1, joint, t.dim());
        }
        let w = n.label.width();
        let x = cx.saturating_sub((w.saturating_sub(1)) / 2).max(area.x as usize) as u16;
        let style = match hot.get(&n.key) {
            Some(Style2::Pointer) => t.bold(t.pointer).add_modifier(ratatui::style::Modifier::REVERSED),
            Some(Style2::Write) => t.bold(t.write),
            Some(Style2::Read) => t.bold(t.read),
            Some(Style2::New) => t.bold(t.good),
            None => t.text(),
        };
        put(buf, area, x, y, &n.label, style);
    }
}

#[derive(Clone, Copy)]
enum Style2 {
    Pointer,
    Write,
    Read,
    New,
}

pub fn tree(spec: &ViewSpec, ctx: &Ctx, v: &V, area: Rect, buf: &mut Buffer) {
    let ptrs = ref_pointers(spec, ctx);
    let tags: Vec<String> = spec
        .pointers
        .iter()
        .filter_map(|n| match ctx.frame.var(n) {
            Some(V::Ref(id)) => Some(format!("{n}={}", node_val(ctx.frame, *id))),
            Some(V::None) => Some(format!("{n}=None")),
            _ => None,
        })
        .collect();
    header(spec, ctx, area, buf, &tags.join("  "));
    let mut nodes = build_ref_tree(ctx.frame, v);
    let prev_ids: HashSet<u64> = ctx.prev.map(|p| p.heap.keys().copied().collect()).unwrap_or_default();
    let mut hot = HashMap::new();
    for n in &nodes {
        if ctx.prev.is_some() && !prev_ids.contains(&(n.key as u64)) {
            hot.insert(n.key, Style2::New);
        }
    }
    for id in ptrs.keys() {
        hot.insert(*id as i64, Style2::Pointer);
    }
    let body = Rect { y: area.y + 1, height: area.height.saturating_sub(1), ..area };
    draw_tree(&mut nodes, ctx, body, buf, &hot);
}

pub fn heap(spec: &ViewSpec, ctx: &Ctx, v: &V, area: Rect, buf: &mut Buffer) {
    let t = ctx.theme;
    let vals = items(v).unwrap_or(&[]);
    header(spec, ctx, area, buf, &format!("size {}", vals.len()));
    let mut nodes = build_array_tree(vals);
    let mut hot = HashMap::new();
    for i in ctx.reads(&spec.var) {
        hot.insert(i, Style2::Read);
    }
    for i in ctx.writes(&spec.var) {
        hot.insert(i, Style2::Write);
    }
    if let (Some(p), Some(V::Seq { items: old, .. })) = (Some(vals), ctx.prev_var(&spec.var)) {
        for (i, x) in p.iter().enumerate() {
            if old.get(i) != Some(x) {
                hot.insert(i as i64, Style2::Write);
            }
        }
    }
    for name in &spec.pointers {
        if let Some(i) = ctx.int(name) {
            hot.insert(i, Style2::Pointer);
        }
    }
    let d = depth_of(&nodes) as u16;
    let tree_area = Rect { y: area.y + 1, height: (d * 2).min(area.height.saturating_sub(4)), ..area };
    draw_tree(&mut nodes, ctx, tree_area, buf, &hot);
    // array form underneath
    let y = area.y + 1 + d * 2;
    let mut x = area.x;
    for (i, val) in vals.iter().enumerate() {
        let label = format!("{}", val.cell());
        let w = label.width().max(2) as u16 + 1;
        if x + w > area.right() {
            put(buf, area, x, y, "..", t.dim());
            break;
        }
        let style = match hot.get(&(i as i64)) {
            Some(Style2::Write) => t.bold(t.write),
            Some(Style2::Read) => t.bold(t.read),
            Some(Style2::Pointer) => t.bold(t.pointer),
            _ => t.text(),
        };
        put(buf, area, x, y, &label, style);
        put(buf, area, x, y + 1, &i.to_string(), t.dim());
        x += w;
    }
}

fn trie_lines(frame: &Frame, v: &V) -> Vec<(String, String, bool, u64)> {
    fn end_flag(o: &crate::runner::trace::Obj) -> bool {
        ["end", "is_end", "is_word", "terminal", "word"].iter().any(|f| match o.field(f) {
            Some(V::Bool(b)) => *b,
            Some(V::None) | None => false,
            Some(V::Str(s)) => !s.is_empty(),
            Some(V::Int(i)) => *i != 0,
            Some(_) => true,
        })
    }
    fn go(frame: &Frame, id: u64, prefix: &str, out: &mut Vec<(String, String, bool, u64)>, seen: &mut HashSet<u64>) {
        if !seen.insert(id) || out.len() > 60 {
            return;
        }
        let Some(obj) = frame.heap.get(&id) else { return };
        let kids: Vec<(String, u64)> = match obj.field("children") {
            Some(V::Dict { items, .. }) => items
                .iter()
                .filter_map(|(k, v)| match v {
                    V::Ref(c) => Some((k.cell(), *c)),
                    _ => None,
                })
                .collect(),
            Some(V::Seq { items, .. }) => items
                .iter()
                .enumerate()
                .filter_map(|(i, v)| match v {
                    V::Ref(c) => Some((((b'a' + i as u8) as char).to_string(), *c)),
                    _ => None,
                })
                .collect(),
            _ => Vec::new(),
        };
        let n = kids.len();
        for (i, (label, child)) in kids.into_iter().enumerate() {
            let last = i + 1 == n;
            let end = frame.heap.get(&child).is_some_and(end_flag);
            out.push((format!("{prefix}{}", if last { "└─ " } else { "├─ " }), label, end, child));
            let next_prefix = format!("{prefix}{}", if last { "   " } else { "│  " });
            go(frame, child, &next_prefix, out, seen);
        }
    }
    let mut out = Vec::new();
    if let V::Ref(id) = v {
        go(frame, *id, "", &mut out, &mut HashSet::new());
    }
    out
}

pub fn trie_height(spec: &ViewSpec, ctx: &Ctx) -> u16 {
    ctx.frame.var(&spec.var).map_or(1, |v| 2 + trie_lines(ctx.frame, v).len().min(18) as u16)
}

pub fn trie(spec: &ViewSpec, ctx: &Ctx, v: &V, area: Rect, buf: &mut Buffer) {
    let t = ctx.theme;
    let ptrs = ref_pointers(spec, ctx);
    header(spec, ctx, area, buf, "");
    put(buf, area, area.x, area.y + 1, "(root)", if matches!(v, V::Ref(id) if ptrs.contains_key(id)) { t.bold(t.pointer) } else { t.dim() });
    let prev_ids: HashSet<u64> = ctx.prev.map(|p| p.heap.keys().copied().collect()).unwrap_or_default();
    let rows = area.height.saturating_sub(2) as usize;
    let lines = trie_lines(ctx.frame, v);
    // two columns when the trie is taller than the area
    let col_w = if lines.len() > rows { area.width / 2 } else { area.width };
    for (i, (prefix, label, end, id)) in lines.iter().enumerate().take(rows * 2) {
        let x = area.x + if i >= rows { col_w } else { 0 };
        let y = area.y + 2 + (i % rows) as u16;
        put(buf, area, x, y, prefix, t.dim());
        let style = if ptrs.contains_key(id) {
            t.bold(t.pointer).add_modifier(ratatui::style::Modifier::REVERSED)
        } else if ctx.prev.is_some() && !prev_ids.contains(id) {
            t.bold(t.good)
        } else {
            t.text()
        };
        let px = x + prefix.width() as u16;
        put(buf, area, px, y, label, style);
        if *end {
            put(buf, area, px + label.width() as u16, y, " *", t.accent());
        }
    }
}
