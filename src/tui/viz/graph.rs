//! Graph view: adjacency dicts or lists, laid out by BFS layers or fixed coordinates.

use std::collections::{HashMap, VecDeque};

use ratatui::buffer::Buffer;
use ratatui::layout::Rect;
use ratatui::style::Modifier;
use unicode_width::UnicodeWidthStr;

use super::{Ctx, header, put};
use crate::content::ViewSpec;
use crate::runner::trace::V;

struct G {
    nodes: Vec<String>,
    edges: Vec<(usize, usize, Option<String>)>,
}

fn neighbour(v: &V) -> (String, Option<String>) {
    match v {
        V::Seq { items, .. } if items.len() == 2 => (items[0].cell(), Some(items[1].cell())),
        other => (other.cell(), None),
    }
}

fn parse(v: &V) -> G {
    let mut nodes: Vec<String> = Vec::new();
    let mut index: HashMap<String, usize> = HashMap::new();
    let mut id = |name: String, nodes: &mut Vec<String>| -> usize {
        *index.entry(name.clone()).or_insert_with(|| {
            nodes.push(name);
            nodes.len() - 1
        })
    };
    let mut edges = Vec::new();
    let adj: Vec<(String, &V)> = match v {
        V::Dict { items, .. } => items.iter().map(|(k, n)| (k.cell(), n)).collect(),
        V::Seq { items, .. } => items.iter().enumerate().map(|(i, n)| (i.to_string(), n)).collect(),
        _ => Vec::new(),
    };
    for (name, _) in &adj {
        id(name.clone(), &mut nodes);
    }
    for (name, ns) in adj {
        let a = id(name, &mut nodes);
        if let V::Seq { items, .. } = ns {
            for n in items {
                let (to, w) = neighbour(n);
                let b = id(to, &mut nodes);
                edges.push((a, b, w));
            }
        } else if let V::Dict { items, .. } = ns {
            for (to, w) in items {
                let b = id(to.cell(), &mut nodes);
                edges.push((a, b, Some(w.cell())));
            }
        }
    }
    G { nodes, edges }
}

/// Grid positions (col, row) for each node.
fn positions(g: &G, spec: &ViewSpec) -> Vec<(usize, usize)> {
    if !spec.layout.is_empty() {
        return g
            .nodes
            .iter()
            .enumerate()
            .map(|(i, n)| spec.layout.get(n).map_or((i % 6, 6 + i / 6), |p| (p[0] as usize, p[1] as usize)))
            .collect();
    }
    let n = g.nodes.len();
    let mut layer = vec![usize::MAX; n];
    let mut adj = vec![Vec::new(); n];
    for (a, b, _) in &g.edges {
        adj[*a].push(*b);
        adj[*b].push(*a);
    }
    for start in 0..n {
        if layer[start] != usize::MAX {
            continue;
        }
        let base = layer.iter().filter(|l| **l != usize::MAX).map(|l| l + 1).max().unwrap_or(0);
        layer[start] = base;
        let mut q = VecDeque::from([start]);
        while let Some(u) = q.pop_front() {
            for &w in &adj[u] {
                if layer[w] == usize::MAX {
                    layer[w] = layer[u] + 1;
                    q.push_back(w);
                }
            }
        }
    }
    let mut seen_in_layer: HashMap<usize, usize> = HashMap::new();
    (0..n)
        .map(|i| {
            let row = seen_in_layer.entry(layer[i]).or_insert(0);
            let pos = (layer[i], *row);
            *row += 1;
            pos
        })
        .collect()
}

pub fn height(spec: &ViewSpec, ctx: &Ctx) -> u16 {
    let Some(v) = ctx.frame.var(&spec.var) else { return 1 };
    let g = parse(v);
    let rows = positions(&g, spec).iter().map(|p| p.1 + 1).max().unwrap_or(1);
    (2 + rows * 2).min(18) as u16
}

fn members(v: Option<&V>) -> Vec<String> {
    match v {
        Some(V::Seq { items, .. }) => items.iter().map(V::cell).collect(),
        Some(V::Dict { items, .. }) => items.iter().map(|(k, _)| k.cell()).collect(),
        _ => Vec::new(),
    }
}

pub fn render(spec: &ViewSpec, ctx: &Ctx, v: &V, area: Rect, buf: &mut Buffer) {
    let t = ctx.theme;
    let g = parse(v);
    // scalar pointers mark the current node, collection pointers mark visited / frontier sets
    let mut current: Vec<String> = Vec::new();
    let mut sets: Vec<(String, Vec<String>)> = Vec::new();
    for name in &spec.pointers {
        match ctx.frame.var(name) {
            Some(x @ (V::Int(_) | V::Str(_))) => current.push(x.cell()),
            Some(x @ (V::Seq { .. } | V::Dict { .. })) => sets.push((name.clone(), members(Some(x)))),
            _ => {}
        }
    }
    let legend: Vec<String> =
        sets.iter().enumerate().map(|(i, (n, _))| format!("{} {n}", if i == 0 { "●" } else { "◆" })).collect();
    header(spec, ctx, area, buf, &format!("{} nodes  {}", g.nodes.len(), legend.join("  ")));
    let pos = positions(&g, spec);
    let cols = pos.iter().map(|p| p.0 + 1).max().unwrap_or(1);
    let lw = g.nodes.iter().map(|n| n.width()).max().unwrap_or(1) + 2;
    let col_w = ((area.width as usize).saturating_sub(lw) / cols.max(1)).clamp(lw + 2, 18);
    let xy = |i: usize| -> (i32, i32) {
        let (c, r) = pos[i];
        (i32::from(area.x) + (c * col_w) as i32 + 1, i32::from(area.y) + 2 + (r * 2) as i32)
    };
    // edges first, nodes drawn over them
    for (a, b, w) in &g.edges {
        let (x0, y0) = xy(*a);
        let (x1, y1) = xy(*b);
        let steps = (x1 - x0).abs().max((y1 - y0).abs()).max(1);
        for s in 1..steps {
            let x = x0 + (x1 - x0) * s / steps;
            let y = y0 + (y1 - y0) * s / steps;
            if x >= 0 && y >= 0 {
                put(buf, area, x as u16, y as u16, "·", t.dim());
            }
        }
        if let Some(w) = w {
            let (mx, my) = (i32::midpoint(x0, x1), i32::midpoint(y0, y1));
            if mx >= 0 && my >= 0 {
                put(buf, area, mx as u16, my as u16, w, t.accent());
            }
        }
    }
    for (i, name) in g.nodes.iter().enumerate() {
        let (x, y) = xy(i);
        if x < 0 || y < 0 {
            continue;
        }
        let mut style = t.text();
        if let Some((_, visited)) = sets.first()
            && visited.contains(name)
        {
            style = t.bold(t.good);
        }
        // the frontier is drawn over visited: queued nodes are usually also marked seen
        if let Some((_, frontier)) = sets.get(1)
            && frontier.contains(name)
        {
            style = t.bold(t.warn);
        }
        if current.contains(name) {
            style = t.bold(t.pointer).add_modifier(Modifier::REVERSED);
        }
        put(buf, area, (x - 1).max(0) as u16, y as u16, &format!("({name})"), style);
    }
}
