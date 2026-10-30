//! Harness output types and the playback timeline.

use std::collections::HashMap;

use serde::Deserialize;
use serde_json::Value;

/// A Python value as encoded by the harness.
#[derive(Debug, Clone, PartialEq)]
pub enum V {
    None,
    Bool(bool),
    Int(i64),
    Float(f64),
    Str(String),
    Seq { kind: SeqKind, items: Vec<V>, len: usize },
    Dict { items: Vec<(V, V)>, len: usize },
    Ref(u64),
    Repr(String),
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum SeqKind {
    List,
    Tuple,
    Deque,
    Set,
}

impl V {
    pub fn from_json(v: &Value) -> V {
        match v {
            Value::Null => V::None,
            Value::Bool(b) => V::Bool(*b),
            Value::Number(n) => match n.as_i64() {
                Some(i) => V::Int(i),
                None => V::Float(n.as_f64().unwrap_or(f64::NAN)),
            },
            Value::String(s) => V::Str(s.clone()),
            Value::Array(items) => V::Seq {
                kind: SeqKind::List,
                items: items.iter().map(V::from_json).collect(),
                len: items.len(),
            },
            Value::Object(map) => {
                let kind = map.get("k").and_then(Value::as_str).unwrap_or("");
                let len = map.get("len").and_then(Value::as_u64).unwrap_or(0) as usize;
                let items = || -> Vec<V> {
                    map.get("items")
                        .and_then(Value::as_array)
                        .map(|a| a.iter().map(V::from_json).collect())
                        .unwrap_or_default()
                };
                match kind {
                    "list" => V::Seq { kind: SeqKind::List, items: items(), len },
                    "tuple" => V::Seq { kind: SeqKind::Tuple, items: items(), len },
                    "deque" => V::Seq { kind: SeqKind::Deque, items: items(), len },
                    "set" => V::Seq { kind: SeqKind::Set, items: items(), len },
                    "dict" => {
                        let pairs = map
                            .get("items")
                            .and_then(Value::as_array)
                            .map(|a| {
                                a.iter()
                                    .filter_map(|p| {
                                        let p = p.as_array()?;
                                        Some((V::from_json(p.first()?), V::from_json(p.get(1)?)))
                                    })
                                    .collect()
                            })
                            .unwrap_or_default();
                        V::Dict { items: pairs, len }
                    }
                    "ref" => V::Ref(map.get("id").and_then(Value::as_u64).unwrap_or(0)),
                    "num" | "repr" => V::Repr(map.get("v").and_then(Value::as_str).unwrap_or("?").to_string()),
                    _ => V::Repr(v.to_string()),
                }
            }
        }
    }

    pub fn as_int(&self) -> Option<i64> {
        match self {
            V::Int(i) => Some(*i),
            V::Bool(b) => Some(*b as i64),
            _ => None,
        }
    }

    /// Short text for a cell or label.
    pub fn label(&self) -> String {
        match self {
            V::None => "None".into(),
            V::Bool(b) => if *b { "True" } else { "False" }.into(),
            V::Int(i) => i.to_string(),
            V::Float(f) => {
                if f.fract() == 0.0 && f.abs() < 1e15 {
                    format!("{f:.1}")
                } else {
                    let s = format!("{f:.3}");
                    s.trim_end_matches('0').to_string()
                }
            }
            V::Str(s) => format!("'{s}'"),
            V::Seq { kind, items, len } => {
                let (open, close) = match kind {
                    SeqKind::List => ("[", "]"),
                    SeqKind::Tuple => ("(", ")"),
                    SeqKind::Deque => ("deque[", "]"),
                    SeqKind::Set => ("{", "}"),
                };
                let mut parts: Vec<String> = items.iter().take(8).map(V::label).collect();
                if *len > parts.len() {
                    parts.push("...".into());
                }
                format!("{open}{}{close}", parts.join(", "))
            }
            V::Dict { items, len } => {
                let mut parts: Vec<String> =
                    items.iter().take(6).map(|(k, v)| format!("{}: {}", k.label(), v.label())).collect();
                if *len > parts.len() {
                    parts.push("...".into());
                }
                format!("{{{}}}", parts.join(", "))
            }
            V::Ref(id) => format!("#{id}"),
            V::Repr(s) => s.clone(),
        }
    }

    /// Cell text without quotes for strings, used inside boxes.
    pub fn cell(&self) -> String {
        match self {
            V::Str(s) => s.clone(),
            other => other.label(),
        }
    }
}

#[derive(Debug, Clone, PartialEq)]
pub struct Obj {
    pub cls: String,
    pub fields: Vec<(String, V)>,
}

impl Obj {
    pub fn field(&self, name: &str) -> Option<&V> {
        self.fields.iter().find(|(n, _)| n == name).map(|(_, v)| v)
    }
}

#[derive(Debug, Clone, Deserialize)]
pub struct StackEntry {
    pub func: String,
    pub args: String,
}

#[derive(Debug, Clone)]
pub struct Frame {
    pub ev: String,
    pub line: u32,
    pub prev: Option<u32>,
    pub vars: Vec<(String, V)>,
    pub locals: Vec<(String, V)>,
    pub heap: HashMap<u64, Obj>,
    pub stack: Vec<StackEntry>,
    pub reads: Vec<(String, i64)>,
    pub writes: Vec<(String, i64)>,
    pub op: Option<String>,
    pub ret: Option<V>,
}

impl Frame {
    /// Like `V::label`, but node references show their `val` (or `key`) instead of an id.
    pub fn label(&self, v: &V) -> String {
        self.text(v, false)
    }

    /// Like `V::cell`, resolving node references.
    pub fn cell(&self, v: &V) -> String {
        self.text(v, true)
    }

    fn text(&self, v: &V, bare: bool) -> String {
        match v {
            V::Ref(id) => match self.heap.get(id) {
                Some(o) => match o.field("val").or_else(|| o.field("key")).or_else(|| o.field("value")) {
                    Some(inner @ (V::Int(_) | V::Float(_) | V::Str(_) | V::Bool(_))) => format!("<{}>", inner.cell()),
                    _ => format!("<{}>", o.cls),
                },
                None => v.label(),
            },
            V::Seq { kind, items, len } if items.iter().any(|x| matches!(x, V::Ref(_))) => {
                let (open, close) = match kind {
                    SeqKind::List => ("[", "]"),
                    SeqKind::Tuple => ("(", ")"),
                    SeqKind::Deque => ("deque[", "]"),
                    SeqKind::Set => ("{", "}"),
                };
                let mut parts: Vec<String> = items.iter().take(8).map(|x| self.label(x)).collect();
                if *len > parts.len() {
                    parts.push("...".into());
                }
                format!("{open}{}{close}", parts.join(", "))
            }
            other if bare => other.cell(),
            other => other.label(),
        }
    }

    pub fn var(&self, name: &str) -> Option<&V> {
        self.vars
            .iter()
            .chain(self.locals.iter())
            .find(|(n, _)| n == name)
            .map(|(_, v)| v)
    }

    pub fn from_json(v: &Value) -> Frame {
        let pairs = |key: &str| -> Vec<(String, V)> {
            v.get(key)
                .and_then(Value::as_object)
                .map(|m| m.iter().map(|(k, x)| (k.clone(), V::from_json(x))).collect())
                .unwrap_or_default()
        };
        let access = |key: &str| -> Vec<(String, i64)> {
            v.get(key)
                .and_then(Value::as_array)
                .map(|a| {
                    a.iter()
                        .filter_map(|p| {
                            let p = p.as_array()?;
                            Some((p.first()?.as_str()?.to_string(), p.get(1)?.as_i64()?))
                        })
                        .collect()
                })
                .unwrap_or_default()
        };
        let heap = v
            .get("heap")
            .and_then(Value::as_object)
            .map(|m| {
                m.iter()
                    .filter_map(|(k, o)| {
                        let id = k.parse::<u64>().ok()?;
                        let cls = o.get("cls")?.as_str()?.to_string();
                        let fields = o
                            .get("fields")
                            .and_then(Value::as_object)
                            .map(|f| f.iter().map(|(n, x)| (n.clone(), V::from_json(x))).collect())
                            .unwrap_or_default();
                        Some((id, Obj { cls, fields }))
                    })
                    .collect()
            })
            .unwrap_or_default();
        Frame {
            ev: v.get("ev").and_then(Value::as_str).unwrap_or("line").to_string(),
            line: v.get("line").and_then(Value::as_u64).unwrap_or(0) as u32,
            prev: v.get("prev").and_then(Value::as_u64).map(|x| x as u32),
            vars: pairs("vars"),
            locals: pairs("locals"),
            heap,
            stack: v
                .get("stack")
                .and_then(|s| serde_json::from_value(s.clone()).ok())
                .unwrap_or_default(),
            reads: access("reads"),
            writes: access("writes"),
            op: v.get("op").and_then(Value::as_str).map(str::to_owned),
            ret: v.get("ret").map(V::from_json),
        }
    }
}

#[derive(Debug, Clone, Deserialize, PartialEq)]
pub struct ErrorInfo {
    pub text: String,
    #[serde(default)]
    pub line: Option<u32>,
    #[serde(default)]
    pub input: Option<String>,
    #[serde(default)]
    pub internal: Option<String>,
}

#[derive(Debug, Clone, Default)]
pub struct VisualResult {
    pub frames: Vec<Frame>,
    pub truncated: bool,
    pub stdout: String,
    pub input: String,
    pub expected: String,
    pub got: Option<String>,
    pub passed: Option<bool>,
    pub error: Option<ErrorInfo>,
}

impl VisualResult {
    pub fn from_json(v: &Value) -> VisualResult {
        let s = |k: &str| v.get(k).and_then(Value::as_str).unwrap_or("").to_string();
        VisualResult {
            frames: v
                .get("frames")
                .and_then(Value::as_array)
                .map(|a| a.iter().map(Frame::from_json).collect())
                .unwrap_or_default(),
            truncated: v.get("truncated").and_then(Value::as_bool).unwrap_or(false),
            stdout: s("stdout"),
            input: s("input"),
            expected: s("expected"),
            got: v.get("got").and_then(Value::as_str).map(str::to_owned),
            passed: v.get("passed").and_then(Value::as_bool),
            error: v.get("error").and_then(|e| serde_json::from_value(e.clone()).ok()),
        }
    }
}

#[derive(Debug, Clone, Deserialize, PartialEq)]
pub struct Failure {
    pub input: String,
    pub expected: String,
    pub got: String,
}

#[derive(Debug, Clone, Deserialize, PartialEq, Default)]
pub struct Steps {
    pub user: Vec<(u32, u64)>,
    #[serde(rename = "ref")]
    pub reference: Vec<(u32, u64)>,
}

#[derive(Debug, Clone, Deserialize, Default)]
pub struct ScoreResult {
    #[serde(default)]
    pub passed: u32,
    #[serde(default)]
    pub total: u32,
    #[serde(default)]
    pub failures: Vec<Failure>,
    #[serde(default)]
    pub stdout: String,
    #[serde(default)]
    pub steps: Option<Steps>,
    #[serde(default)]
    pub step_limit_hit: Option<u32>,
    #[serde(default)]
    pub error: Option<ErrorInfo>,
}

/// Playback state over a list of frames.
#[derive(Debug, Clone)]
pub struct Timeline {
    pub len: usize,
    pub pos: usize,
    pub playing: bool,
    /// Index into SPEEDS.
    pub speed: usize,
    acc_ms: u64,
    /// Ticks since the position last changed, for tweening.
    pub since_change: u32,
    pub prev_pos: usize,
}

/// Milliseconds per frame at each speed setting.
pub const SPEEDS: [u64; 7] = [1200, 700, 400, 220, 120, 60, 25];

impl Timeline {
    pub fn new(len: usize, speed: usize) -> Self {
        Timeline {
            len,
            pos: 0,
            playing: len > 1,
            speed: speed.min(SPEEDS.len() - 1),
            acc_ms: 0,
            since_change: u32::MAX,
            prev_pos: 0,
        }
    }

    pub fn at_end(&self) -> bool {
        self.len == 0 || self.pos + 1 >= self.len
    }

    pub fn seek(&mut self, pos: usize) {
        let pos = pos.min(self.len.saturating_sub(1));
        if pos != self.pos {
            self.prev_pos = self.pos;
            self.pos = pos;
            self.since_change = 0;
        }
    }

    pub fn step(&mut self, delta: i64) {
        self.playing = false;
        let target = (self.pos as i64 + delta).clamp(0, self.len.saturating_sub(1) as i64) as usize;
        self.seek(target);
    }

    pub fn toggle(&mut self) {
        if self.at_end() {
            self.seek(0);
            self.playing = true;
        } else {
            self.playing = !self.playing;
        }
        self.acc_ms = 0;
    }

    pub fn faster(&mut self) {
        self.speed = (self.speed + 1).min(SPEEDS.len() - 1);
    }

    pub fn slower(&mut self) {
        self.speed = self.speed.saturating_sub(1);
    }

    /// Advance the clock. Returns true when the position changed.
    pub fn tick(&mut self, elapsed_ms: u64) -> bool {
        self.since_change = self.since_change.saturating_add(1);
        if !self.playing {
            return false;
        }
        self.acc_ms += elapsed_ms;
        let per = SPEEDS[self.speed];
        if self.acc_ms < per {
            return false;
        }
        self.acc_ms -= per;
        if self.at_end() {
            self.playing = false;
            return false;
        }
        self.seek(self.pos + 1);
        if self.at_end() {
            self.playing = false;
        }
        true
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn decodes_tagged_values() {
        let v = V::from_json(&json!({"k": "list", "items": [1, 2.5, "a", null, {"k": "ref", "id": 3}], "len": 9}));
        match v {
            V::Seq { kind, items, len } => {
                assert_eq!(kind, SeqKind::List);
                assert_eq!(len, 9);
                assert_eq!(items[0], V::Int(1));
                assert_eq!(items[1], V::Float(2.5));
                assert_eq!(items[2], V::Str("a".into()));
                assert_eq!(items[3], V::None);
                assert_eq!(items[4], V::Ref(3));
            }
            other => panic!("unexpected {other:?}"),
        }
        let d = V::from_json(&json!({"k": "dict", "items": [["a", 1]], "len": 1}));
        assert_eq!(d.label(), "{'a': 1}");
    }

    #[test]
    fn decodes_frames_with_heap_and_access() {
        let raw = json!({
            "ev": "line", "line": 4, "prev": 3,
            "vars": {"head": {"k": "ref", "id": 1}, "i": 2},
            "locals": {"n": 5},
            "heap": {"1": {"cls": "ListNode", "fields": {"val": 7, "next": null}}},
            "stack": [{"func": "solve", "args": "head=<7>", "line": 4}],
            "reads": [["nums", 1]], "writes": [["nums", 2]]
        });
        let f = Frame::from_json(&raw);
        assert_eq!(f.line, 4);
        assert_eq!(f.prev, Some(3));
        assert_eq!(f.var("head"), Some(&V::Ref(1)));
        assert_eq!(f.heap[&1].field("val"), Some(&V::Int(7)));
        assert_eq!(f.var("n"), Some(&V::Int(5)));
        assert_eq!(f.reads, vec![("nums".to_string(), 1)]);
        assert_eq!(f.writes, vec![("nums".to_string(), 2)]);
    }

    #[test]
    fn timeline_plays_to_end_and_stops() {
        let mut t = Timeline::new(3, 6);
        assert!(t.playing);
        let mut moves = 0;
        for _ in 0..20 {
            if t.tick(33) {
                moves += 1;
            }
        }
        assert_eq!(moves, 2);
        assert!(t.at_end());
        assert!(!t.playing);
        t.toggle();
        assert_eq!(t.pos, 0);
        assert!(t.playing);
    }

    #[test]
    fn timeline_step_clamps() {
        let mut t = Timeline::new(5, 3);
        t.step(-3);
        assert_eq!(t.pos, 0);
        t.step(10);
        assert_eq!(t.pos, 4);
        assert!(!t.playing);
    }
}
