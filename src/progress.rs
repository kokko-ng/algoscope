//! Saved progress, drafts and settings under the platform data directory.

use std::collections::HashMap;
use std::fs;
use std::path::PathBuf;

use anyhow::{Context, Result};
use serde::{Deserialize, Serialize};

use crate::content::{Challenge, Library, Stage, Topic};
use crate::scoring::Grade;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize, Default)]
#[serde(rename_all = "lowercase")]
pub enum ThemeKind {
    #[default]
    Stealth,
    Game,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize, Default)]
#[serde(rename_all = "lowercase")]
pub enum KeymapKind {
    #[default]
    Standard,
    Vim,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(default)]
pub struct Settings {
    pub theme: ThemeKind,
    pub keymap: KeymapKind,
    /// Playback speed index, see `trace::SPEEDS`.
    pub speed: usize,
}

impl Default for Settings {
    fn default() -> Self {
        Settings { theme: ThemeKind::Stealth, keymap: KeymapKind::Standard, speed: 3 }
    }
}

#[derive(Debug, Clone, Default, Serialize, Deserialize, PartialEq)]
#[serde(default)]
pub struct ChallengeProgress {
    pub done: bool,
    pub grade: Option<Grade>,
    pub xp_awarded: u32,
    pub hints_used: u32,
    pub best_ratio: Option<f64>,
}

#[derive(Debug, Clone, Default, Serialize, Deserialize)]
#[serde(default)]
pub struct Progress {
    pub xp: u64,
    pub challenges: HashMap<String, ChallengeProgress>,
    pub drafts: HashMap<String, String>,
    pub last_challenge: Option<String>,
    pub seconds_practised: u64,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum TopicState {
    Locked,
    Open,
    /// Every challenge done.
    Done,
    /// Every challenge done, graded ones at silver or better.
    Mastered,
}

impl Progress {
    pub fn get(&self, key: &str) -> ChallengeProgress {
        self.challenges.get(key).cloned().unwrap_or_default()
    }

    pub fn is_done(&self, key: &str) -> bool {
        self.challenges.get(key).is_some_and(|c| c.done)
    }

    /// Record a completed challenge. Returns the XP newly awarded (the difference over previous awards).
    pub fn complete(&mut self, key: &str, earned: u32, grade: Option<Grade>, ratio: Option<f64>) -> u32 {
        let entry = self.challenges.entry(key.to_string()).or_default();
        entry.done = true;
        if let Some(g) = grade {
            entry.grade = Some(entry.grade.map_or(g, |old| old.max(g)));
        }
        if let Some(r) = ratio {
            entry.best_ratio = Some(entry.best_ratio.map_or(r, |old| old.min(r)));
        }
        let delta = earned.saturating_sub(entry.xp_awarded);
        entry.xp_awarded += delta;
        self.xp += u64::from(delta);
        delta
    }

    pub fn use_hint(&mut self, key: &str) {
        self.challenges.entry(key.to_string()).or_default().hints_used += 1;
    }

    /// Whether a topic's gate is done: its build stages, or, for a topic without any (system design), its first
    /// challenge after the walkthrough.
    fn builds_done(&self, topic: &Topic) -> bool {
        let builds: Vec<&Challenge> = topic.challenges.iter().filter(|c| c.meta.stage == Stage::Build).collect();
        if builds.is_empty() {
            return topic
                .challenges
                .iter()
                .find(|c| c.meta.stage != Stage::Watch)
                .is_none_or(|c| self.is_done(&c.key()));
        }
        builds.iter().all(|c| self.is_done(&c.key()))
    }

    pub fn topic_state(&self, lib: &Library, topic: &Topic) -> TopicState {
        let unlocked = topic.meta.prereqs.iter().all(|p| lib.topic(p).is_some_and(|t| self.builds_done(t)));
        if !unlocked {
            return TopicState::Locked;
        }
        let all_done = topic.challenges.iter().all(|c| self.is_done(&c.key()));
        if !all_done {
            return TopicState::Open;
        }
        let mastered = topic
            .challenges
            .iter()
            .all(|c| c.meta.stage == Stage::Watch || self.get(&c.key()).grade.is_some_and(|g| g >= Grade::Silver));
        if mastered { TopicState::Mastered } else { TopicState::Done }
    }

    pub fn topic_fraction(&self, topic: &Topic) -> f64 {
        if topic.challenges.is_empty() {
            return 0.0;
        }
        let done = topic.challenges.iter().filter(|c| self.is_done(&c.key())).count();
        done as f64 / topic.challenges.len() as f64
    }

    /// The first unfinished challenge of a topic, or its first challenge.
    pub fn next_in_topic(&self, topic: &Topic) -> Option<String> {
        topic
            .challenges
            .iter()
            .find(|c| !self.is_done(&c.key()))
            .or_else(|| topic.challenges.first())
            .map(Challenge::key)
    }
}

/// Where progress and settings live. $`ALGOSCOPE_HOME` overrides the platform data dir.
pub fn data_dir() -> PathBuf {
    if let Ok(dir) = std::env::var("ALGOSCOPE_HOME") {
        return PathBuf::from(dir);
    }
    dirs::data_dir().unwrap_or_else(|| PathBuf::from(".")).join("algoscope")
}

pub struct Store {
    dir: PathBuf,
}

impl Store {
    pub fn new(dir: PathBuf) -> Store {
        Store { dir }
    }

    fn read<T: for<'de> Deserialize<'de> + Default>(&self, name: &str, parse: fn(&str) -> Result<T>) -> T {
        fs::read_to_string(self.dir.join(name)).ok().and_then(|raw| parse(&raw).ok()).unwrap_or_default()
    }

    pub fn load_progress(&self) -> Progress {
        self.read("progress.json", |raw| Ok(serde_json::from_str(raw)?))
    }

    pub fn load_settings(&self) -> Settings {
        self.read("settings.toml", |raw| Ok(toml::from_str(raw)?))
    }

    fn write_atomic(&self, name: &str, body: &[u8]) -> Result<()> {
        fs::create_dir_all(&self.dir).with_context(|| format!("creating {}", self.dir.display()))?;
        let tmp = self.dir.join(format!(".{name}.tmp"));
        fs::write(&tmp, body)?;
        fs::rename(&tmp, self.dir.join(name))?;
        Ok(())
    }

    pub fn save_progress(&self, p: &Progress) -> Result<()> {
        self.write_atomic("progress.json", &serde_json::to_vec_pretty(p)?)
    }

    pub fn save_settings(&self, s: &Settings) -> Result<()> {
        self.write_atomic("settings.toml", toml::to_string(s)?.as_bytes())
    }

    pub fn reset(&self) -> Result<()> {
        for name in ["progress.json", "settings.toml"] {
            let p = self.dir.join(name);
            if p.exists() {
                fs::remove_file(p)?;
            }
        }
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn progress_round_trips() {
        let dir = tempfile::tempdir().unwrap();
        let store = Store::new(dir.path().to_path_buf());
        let mut p = Progress::default();
        assert_eq!(p.complete("t/a", 120, Some(Grade::Silver), Some(1.8)), 120);
        p.drafts.insert("t/a".into(), "def solve():\n    pass\n".into());
        store.save_progress(&p).unwrap();
        let back = store.load_progress();
        assert_eq!(back.xp, 120);
        assert_eq!(back.get("t/a").grade, Some(Grade::Silver));
        assert_eq!(back.drafts["t/a"], "def solve():\n    pass\n");

        let s = Settings { theme: ThemeKind::Game, keymap: KeymapKind::Vim, speed: 5 };
        store.save_settings(&s).unwrap();
        let s2 = store.load_settings();
        assert_eq!(s2.theme, ThemeKind::Game);
        assert_eq!(s2.keymap, KeymapKind::Vim);
        assert_eq!(s2.speed, 5);
    }

    #[test]
    fn resubmitting_awards_only_the_difference() {
        let mut p = Progress::default();
        assert_eq!(p.complete("t/a", 100, Some(Grade::Bronze), None), 100);
        assert_eq!(p.complete("t/a", 90, Some(Grade::Bronze), None), 0);
        assert_eq!(p.complete("t/a", 150, Some(Grade::Gold), None), 50);
        assert_eq!(p.xp, 150);
        assert_eq!(p.complete("t/a", 100, Some(Grade::Bronze), None), 0);
        assert_eq!(p.get("t/a").grade, Some(Grade::Gold));
    }

    #[test]
    fn topics_unlock_after_prerequisite_builds_and_master_at_silver() {
        let lib = Library::load().unwrap();
        let mut p = Progress::default();
        let foundations = lib.topic("foundations").unwrap();
        let two = lib.topic("two-pointers").unwrap();
        assert_eq!(p.topic_state(&lib, foundations), TopicState::Open);
        assert_eq!(p.topic_state(&lib, two), TopicState::Locked);
        for c in foundations.challenges.iter().filter(|c| c.meta.stage == Stage::Build) {
            p.complete(&c.key(), 10, Some(Grade::Bronze), None);
        }
        assert_eq!(p.topic_state(&lib, two), TopicState::Open);
        for c in &foundations.challenges {
            p.complete(&c.key(), 10, (c.meta.stage != Stage::Watch).then_some(Grade::Bronze), None);
        }
        assert_eq!(p.topic_state(&lib, foundations), TopicState::Done);
        for c in &foundations.challenges {
            p.complete(&c.key(), 20, (c.meta.stage != Stage::Watch).then_some(Grade::Silver), None);
        }
        assert_eq!(p.topic_state(&lib, foundations), TopicState::Mastered);
        // a system design topic unlocks once the first quiz of its prerequisite is done
        let estimation = lib.topic("estimation").unwrap();
        let first_quiz = estimation.challenges.iter().find(|c| c.meta.stage == Stage::Quiz).unwrap();
        if let Some(next) =
            lib.track_topics(crate::content::Track::Design).find(|t| t.meta.prereqs.contains(&"estimation".to_string()))
        {
            assert_eq!(p.topic_state(&lib, next), TopicState::Locked);
            p.complete(&first_quiz.key(), 10, Some(Grade::Bronze), None);
            assert_eq!(p.topic_state(&lib, next), TopicState::Open);
        }
        // a topic with two prerequisites needs both
        let trees = lib.topic("trees").unwrap();
        assert_eq!(p.topic_state(&lib, trees), TopicState::Locked);
    }

    #[test]
    fn missing_files_give_defaults() {
        let dir = tempfile::tempdir().unwrap();
        let store = Store::new(dir.path().join("nope"));
        assert_eq!(store.load_progress().xp, 0);
        assert_eq!(store.load_settings().theme, ThemeKind::Stealth);
    }
}
