//! Curriculum content embedded at build time from `content/`.

use std::collections::HashMap;
use std::path::Path;

use anyhow::{Context, Result, anyhow, bail};
use include_dir::{Dir, include_dir};
use serde::{Deserialize, Serialize};

static CONTENT: Dir = include_dir!("$CARGO_MANIFEST_DIR/content");

#[derive(Debug, Clone, Copy, PartialEq, Eq, Deserialize, Serialize)]
#[serde(rename_all = "lowercase")]
pub enum Stage {
    Watch,
    Build,
    Apply,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Deserialize, Default)]
#[serde(rename_all = "lowercase")]
pub enum Kind {
    #[default]
    Function,
    Class,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum ViewKind {
    Array,
    Bars,
    Grid,
    Linked,
    Tree,
    Graph,
    Map,
    Buckets,
    Stack,
    Queue,
    Heap,
    Trie,
    Set,
    Value,
}

#[derive(Debug, Clone, Deserialize)]
pub struct ViewSpec {
    pub var: String,
    #[serde(rename = "as")]
    pub kind: ViewKind,
    #[serde(default)]
    pub label: Option<String>,
    /// Index variables drawn as arrows under an array, or as highlighted nodes.
    #[serde(default)]
    pub pointers: Vec<String>,
    /// Two index variables bounding a highlighted window, inclusive on both ends.
    #[serde(default)]
    pub window: Option<[String; 2]>,
    /// Optional fixed node coordinates for graph views: node label -> [col, row].
    #[serde(default)]
    pub layout: HashMap<String, [u16; 2]>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct Caption {
    pub line: u32,
    pub text: String,
}

fn default_entry() -> String {
    "solve".into()
}

fn default_output() -> String {
    "return".into()
}

#[derive(Debug, Clone, Deserialize)]
pub struct ChallengeMeta {
    pub id: String,
    pub title: String,
    pub stage: Stage,
    pub xp: u32,
    #[serde(default)]
    pub kind: Kind,
    #[serde(default = "default_entry")]
    pub entry: String,
    #[serde(default = "default_output")]
    pub output: String,
    /// Declared complexity of the reference, e.g. "O(n log n)".
    pub complexity: String,
    pub statement: String,
    #[serde(default)]
    pub hints: Vec<String>,
    #[serde(default)]
    pub forbid: Vec<String>,
    #[serde(default)]
    pub sizes: Option<Vec<u32>>,
    #[serde(default)]
    pub check_sizes: Option<Vec<u32>>,
    #[serde(default)]
    pub seeds: Option<u32>,
    #[serde(default)]
    pub view: Vec<ViewSpec>,
    #[serde(default)]
    pub captions: Vec<Caption>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct TopicMeta {
    pub id: String,
    pub title: String,
    /// Name used by the game theme.
    pub zone: String,
    pub summary: String,
    #[serde(default)]
    pub prereqs: Vec<String>,
    pub order: u32,
    pub challenges: Vec<String>,
}

#[derive(Debug, Clone)]
pub struct Challenge {
    pub meta: ChallengeMeta,
    pub topic: String,
    pub starter: String,
    pub reference: String,
    pub cases: String,
}

impl Challenge {
    /// Stable key used for progress and drafts.
    pub fn key(&self) -> String {
        format!("{}/{}", self.topic, self.meta.id)
    }

    /// Every variable the harness should snapshot for this challenge's views.
    pub fn watch_names(&self) -> Vec<String> {
        let mut names: Vec<String> = Vec::new();
        let mut push = |n: &str| {
            if !names.iter().any(|x| x == n) {
                names.push(n.to_string());
            }
        };
        for v in &self.meta.view {
            push(&v.var);
            for p in &v.pointers {
                push(p);
            }
            if let Some([a, b]) = &v.window {
                push(a);
                push(b);
            }
        }
        names
    }
}

#[derive(Debug, Clone)]
pub struct Topic {
    pub meta: TopicMeta,
    pub challenges: Vec<Challenge>,
}

#[derive(Debug, Clone)]
pub struct Library {
    pub topics: Vec<Topic>,
}

fn read_text(dir: &Dir, rel: &str) -> Option<String> {
    dir.get_file(dir.path().join(rel)).and_then(|f| f.contents_utf8()).map(str::to_owned)
}

/// Parse one topic directory. `read` returns a file's text by path relative to the topic directory.
fn parse_topic(path: &str, read: impl Fn(&str) -> Option<String>) -> Result<Topic> {
    let raw = read("topic.toml").ok_or_else(|| anyhow!("{path} has no topic.toml"))?;
    let meta: TopicMeta = toml::from_str(&raw).with_context(|| format!("parsing {path}/topic.toml"))?;
    let mut challenges = Vec::new();
    for cid in &meta.challenges {
        let file = |name: &str| read(&format!("{cid}/{name}"));
        let at = format!("{path}/{cid}");
        let raw = file("challenge.toml").ok_or_else(|| anyhow!("{at} has no challenge.toml"))?;
        let cm: ChallengeMeta = toml::from_str(&raw).with_context(|| format!("parsing {at}/challenge.toml"))?;
        if cm.id != *cid {
            bail!("{at}: id {} does not match its directory", cm.id);
        }
        let reference = file("reference.py").ok_or_else(|| anyhow!("{at} has no reference.py"))?;
        let cases = file("cases.py").ok_or_else(|| anyhow!("{at} has no cases.py"))?;
        let starter = match cm.stage {
            Stage::Watch => reference.clone(),
            _ => file("starter.py").ok_or_else(|| anyhow!("{at} has no starter.py"))?,
        };
        challenges.push(Challenge { meta: cm, topic: meta.id.clone(), starter, reference, cases });
    }
    Ok(Topic { meta, challenges })
}

impl Library {
    pub fn load() -> Result<Self> {
        Self::from_dir(&CONTENT)
    }

    pub fn from_dir(root: &Dir) -> Result<Self> {
        let mut topics = Vec::new();
        for topic_dir in root.dirs() {
            let read = |rel: &str| read_text(topic_dir, rel);
            topics.push(parse_topic(&topic_dir.path().display().to_string(), read)?);
        }
        let lib = Library::assemble(topics);
        lib.validate()?;
        Ok(lib)
    }

    /// Load topics from a directory on disk (for authoring). Prerequisites outside it are not checked.
    pub fn from_fs(root: &Path) -> Result<Self> {
        let mut topics = Vec::new();
        for entry in std::fs::read_dir(root).with_context(|| format!("reading {}", root.display()))? {
            let dir = entry?.path();
            if !dir.join("topic.toml").exists() {
                continue;
            }
            let read = |rel: &str| std::fs::read_to_string(dir.join(rel)).ok();
            topics.push(parse_topic(&dir.display().to_string(), read)?);
        }
        Ok(Library::assemble(topics))
    }

    fn assemble(mut topics: Vec<Topic>) -> Library {
        topics.sort_by_key(|t| t.meta.order);
        Library { topics }
    }

    fn validate(&self) -> Result<()> {
        for t in &self.topics {
            for p in &t.meta.prereqs {
                if self.topic(p).is_none() {
                    bail!("topic {} has unknown prerequisite {p}", t.meta.id);
                }
            }
        }
        Ok(())
    }

    pub fn topic(&self, id: &str) -> Option<&Topic> {
        self.topics.iter().find(|t| t.meta.id == id)
    }

    pub fn challenge(&self, key: &str) -> Option<&Challenge> {
        let (topic, id) = key.split_once('/')?;
        self.topic(topic)?.challenges.iter().find(|c| c.meta.id == id)
    }

    /// Topic indices in display order, each with its tree prefix: topics hang under their deepest prerequisite.
    pub fn tree_order(&self) -> Vec<(usize, String)> {
        let n = self.topics.len();
        let idx = |id: &str| self.topics.iter().position(|t| t.meta.id == id);
        let mut depth = vec![0usize; n];
        for i in 0..n {
            // topics are sorted by order, so prerequisites come first
            depth[i] = self.topics[i].meta.prereqs.iter().filter_map(|p| idx(p)).map(|p| depth[p] + 1).max().unwrap_or(0);
        }
        let parent: Vec<Option<usize>> = (0..n)
            .map(|i| self.topics[i].meta.prereqs.iter().filter_map(|p| idx(p)).max_by_key(|p| (depth[*p], *p)))
            .collect();
        fn go(i: usize, prefix: &str, last: bool, root: bool, parent: &[Option<usize>], out: &mut Vec<(usize, String)>) {
            let branch = if root { "" } else if last { "└─ " } else { "├─ " };
            out.push((i, format!("{prefix}{branch}")));
            let kids: Vec<usize> = (0..parent.len()).filter(|k| parent[*k] == Some(i)).collect();
            let next = if root { String::new() } else { format!("{prefix}{}", if last { "   " } else { "│  " }) };
            for (j, k) in kids.iter().enumerate() {
                go(*k, &next, j + 1 == kids.len(), false, parent, out);
            }
        }
        let mut out = Vec::new();
        for root in (0..n).filter(|i| parent[*i].is_none()) {
            go(root, "", true, true, &parent, &mut out);
        }
        out
    }

    pub fn total_challenges(&self) -> usize {
        self.topics.iter().map(|t| t.challenges.len()).sum()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn embedded_content_loads() {
        let lib = Library::load().expect("content loads");
        assert!(!lib.topics.is_empty());
        for t in &lib.topics {
            assert!(!t.challenges.is_empty(), "topic {} has no challenges", t.meta.id);
        }
    }
}
