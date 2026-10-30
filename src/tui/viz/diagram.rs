//! System design diagrams: boxes on a grid, links between them, and packets that travel along a flow.

use std::collections::HashMap;

use ratatui::buffer::Buffer;
use ratatui::layout::Rect;
use ratatui::style::{Modifier, Style};
use unicode_width::UnicodeWidthStr;

use super::{put, wrap};
use crate::content::{Diagram, DiagramStep};
use crate::tui::theme::Theme;

/// Frames per animation step: packets move for the first MOVE frames, then hold.
pub const FRAMES_PER_STEP: usize = 20;
const MOVE: usize = 14;

/// Screen geometry of one node box.
#[derive(Debug, Clone, Copy)]
struct Placed {
    x: u16,
    y: u16,
    w: u16,
}

impl Placed {
    fn cx(self) -> u16 {
        self.x + self.w / 2
    }

    fn cy(self) -> u16 {
        self.y + 1
    }
}

fn place(diagram: &Diagram, area: Rect) -> HashMap<String, Placed> {
    let cols = diagram.nodes.iter().map(|n| n.at[0] + 1).max().unwrap_or(1);
    let rows = diagram.nodes.iter().map(|n| n.at[1] + 1).max().unwrap_or(1);
    let cell_w = (area.width / cols).max(6);
    let cell_h = (area.height / rows).clamp(4, 6);
    diagram
        .nodes
        .iter()
        .map(|n| {
            let w = (n.label.width() as u16 + 4).min(cell_w.saturating_sub(1)).max(5);
            let x = area.x + n.at[0] * cell_w + (cell_w.saturating_sub(w)) / 2;
            let y = area.y + n.at[1] * cell_h;
            (n.id.clone(), Placed { x, y, w })
        })
        .collect()
}

/// Cells of the route between two nodes: an L shape that avoids the other boxes when it can.
fn route_avoiding(a: Placed, b: Placed, others: &[Placed]) -> Vec<(u16, u16)> {
    let clear = |cells: &[(u16, u16)]| !cells.iter().any(|c| others.iter().any(|o| inside(*o, *c)));
    let first = route(a, b);
    if clear(&first) {
        return first;
    }
    // go vertical first: the reverse of b -> a, which starts horizontal from b
    let mut second = route(b, a);
    second.reverse();
    if clear(&second) { second } else { first }
}

/// Cells of the route between two nodes: horizontal from `a`, then vertical into `b`.
fn route(a: Placed, b: Placed) -> Vec<(u16, u16)> {
    let mut cells = Vec::new();
    let (ax, ay, bx, by) = (a.cx(), a.cy(), b.cx(), b.cy());
    if ax == bx || ay == by {
        let (x0, x1, y0, y1) = (ax, bx, ay, by);
        let steps = x0.abs_diff(x1).max(y0.abs_diff(y1));
        for s in 0..=steps {
            let x = if x1 >= x0 { x0 + s.min(x1 - x0) } else { x0 - s.min(x0 - x1) };
            let y = if y1 >= y0 { y0 + s.min(y1 - y0) } else { y0 - s.min(y0 - y1) };
            cells.push((x, y));
        }
        return cells;
    }
    let mut x = ax;
    while x != bx {
        cells.push((x, ay));
        x = if bx > ax { x + 1 } else { x - 1 };
    }
    let mut y = ay;
    while y != by {
        cells.push((bx, y));
        y = if by > ay { y + 1 } else { y - 1 };
    }
    cells.push((bx, by));
    cells
}

fn inside(p: Placed, (x, y): (u16, u16)) -> bool {
    x >= p.x && x < p.x + p.w && y >= p.y && y < p.y + 3
}

/// Draw the diagram for one step, `frame_in_step` frames into it (see `FRAMES_PER_STEP`).
pub fn render(
    diagram: &Diagram,
    step: Option<&DiagramStep>,
    frame_in_step: usize,
    theme: &Theme,
    area: Rect,
    buf: &mut Buffer,
) {
    let t = theme;
    let caption_rows = step.map_or(0, |s| wrap(&s.caption, area.width.saturating_sub(2) as usize).len().min(3)) as u16;
    let body = Rect { height: area.height.saturating_sub(caption_rows + 1), ..area };
    let placed = place(diagram, body);
    // links
    let routes = |a: &str, b: &str| -> Option<Vec<(u16, u16)>> {
        let (pa, pb) = (placed.get(a)?, placed.get(b)?);
        let others: Vec<Placed> = placed.iter().filter(|(id, _)| *id != a && *id != b).map(|(_, p)| *p).collect();
        Some(route_avoiding(*pa, *pb, &others))
    };
    for [a, b] in &diagram.links {
        let (Some(pa), Some(pb)) = (placed.get(a), placed.get(b)) else { continue };
        let Some(cells) = routes(a, b) else { continue };
        for (i, &(x, y)) in cells.iter().enumerate() {
            if inside(*pa, (x, y)) || inside(*pb, (x, y)) {
                continue;
            }
            let prev = i.checked_sub(1).map(|j| cells[j]);
            let next = cells.get(i + 1).copied();
            let turn = matches!((prev, next), (Some((px, _)), Some((_, ny))) if px != x && ny != y);
            let glyph = if turn {
                let (px, _) = prev.unwrap_or((x, y));
                let (_, ny) = next.unwrap_or((x, y));
                match (px < x, ny > y) {
                    (true, true) => "┐",
                    (true, false) => "┘",
                    (false, true) => "┌",
                    (false, false) => "└",
                }
            } else if next.or(prev).is_some_and(|(_, ny)| ny != y) {
                "│"
            } else {
                "─"
            };
            put(buf, area, x, y, glyph, t.dim());
        }
    }
    // nodes
    let highlight = step.map(|s| s.highlight.as_slice()).unwrap_or_default();
    let down = step.map(|s| s.down.as_slice()).unwrap_or_default();
    for node in &diagram.nodes {
        let Some(p) = placed.get(&node.id) else { continue };
        let is_down = down.contains(&node.id);
        let border = if is_down {
            t.bold(t.bad)
        } else if highlight.contains(&node.id) {
            t.bold(t.accent)
        } else {
            Style::default().fg(t.border_focus)
        };
        let inner = (p.w - 2) as usize;
        put(buf, area, p.x, p.y, &format!("┌{}┐", "─".repeat(inner)), border);
        put(buf, area, p.x, p.y + 2, &format!("└{}┘", "─".repeat(inner)), border);
        put(buf, area, p.x, p.y + 1, "│", border);
        put(buf, area, p.x + p.w - 1, p.y + 1, "│", border);
        let label: String = node.label.chars().take(inner).collect();
        let mut style = if is_down { t.dim().add_modifier(Modifier::CROSSED_OUT) } else { t.text() };
        if highlight.contains(&node.id) {
            style = t.bold(t.accent);
        }
        put(buf, area, p.x + 1, p.y + 1, &format!("{label:^inner$}"), style);
        if let Some(note) = step.and_then(|s| s.labels.get(&node.id)) {
            let w = note.width() as u16;
            let x = p.cx().saturating_sub(w / 2).max(area.x);
            put(buf, area, x, p.y + 3, note, t.bold(t.warn));
        }
    }
    // packets along the flow
    if let Some(s) = step {
        let mut path: Vec<(u16, u16)> = Vec::new();
        for pair in s.flow.windows(2) {
            if let (Some(a), Some(b), Some(cells)) =
                (placed.get(&pair[0]), placed.get(&pair[1]), routes(&pair[0], &pair[1]))
            {
                path.extend(cells.into_iter().filter(|c| !inside(*a, *c) && !inside(*b, *c)));
            }
        }
        if !path.is_empty() {
            let progress = (frame_in_step as f64 / MOVE as f64).min(1.0);
            for k in 0..s.packets.max(1) {
                let p = progress - f64::from(k) * 0.18;
                if (0.0..1.0).contains(&p) || (p >= 1.0 && k == 0 && frame_in_step < MOVE) {
                    let idx = ((p.clamp(0.0, 1.0)) * (path.len() - 1) as f64).round() as usize;
                    let (x, y) = path[idx];
                    put(buf, area, x, y, "●", t.bold(t.accent2));
                }
            }
        }
        // caption under the diagram
        let top = area.bottom().saturating_sub(caption_rows);
        for (i, line) in wrap(&s.caption, area.width.saturating_sub(2) as usize).into_iter().take(3).enumerate() {
            put(buf, area, area.x + 1, top + i as u16, &line, t.bold(t.accent2));
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::progress::ThemeKind;
    use crate::tui::viz::tests::buffer_text;

    fn diagram() -> Diagram {
        toml::from_str(
            r#"
            nodes = [
              { id = "client", label = "Client", at = [0, 0] },
              { id = "lb", label = "Load balancer", at = [1, 0] },
              { id = "app", label = "App", at = [2, 0] },
              { id = "db", label = "Database", at = [2, 1] },
            ]
            links = [["client", "lb"], ["lb", "app"], ["app", "db"]]
            [[steps]]
            flow = ["client", "lb", "app", "db"]
            highlight = ["lb"]
            labels = { db = "1 write" }
            caption = "The request goes through the load balancer to one app server."
            "#,
        )
        .unwrap()
    }

    #[test]
    fn draws_boxes_links_packet_and_caption() {
        let d = diagram();
        let theme = Theme::new(ThemeKind::Stealth);
        let mut buf = Buffer::empty(Rect::new(0, 0, 66, 14));
        render(&d, d.steps.first(), 6, &theme, buf.area, &mut buf);
        let text = buffer_text(&buf);
        insta::assert_snapshot!(text);
        assert!(text.contains("Load balancer"));
        assert!(text.contains('●'));
        assert!(text.contains("1 write"));
    }
}
