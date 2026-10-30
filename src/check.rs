//! `algoscope check-content`: verifies every challenge end to end through the real harness.

use std::fmt::Write as _;
use std::sync::Mutex;
use std::sync::atomic::{AtomicBool, Ordering};
use std::thread;

use anyhow::{Result, bail};

use crate::content::{Alternative, Challenge, DiagramStep, Expect, Library, Question, Stage, Track};
use crate::quiz;
use crate::runner::{self, Mode, Outcome};
use crate::scoring::{self, Grade};

/// Expected range of the empirical growth exponent for a declared complexity.
pub fn expected_slope(decl: &str) -> Option<(f64, f64)> {
    let d: String = decl.to_lowercase().chars().filter(|c| !c.is_whitespace()).collect();
    let d = d.trim_start_matches("amortized").to_string();
    Some(match d.as_str() {
        "o(1)" | "o(logn)" | "o(log n)" => (-0.2, 0.4),
        "o(n)" | "o(v+e)" | "o(n+k)" | "o(n+m)" | "o(m+n)" | "o(e)" | "o(l)" | "o(nl)" | "o(n·l)" => (0.75, 1.2),
        "o(nlogn)" | "o(eloge)" | "o(elogv)" | "o((v+e)logv)" | "o(nlogk)" | "o(e·α(v))" | "o(eα(v))" => (0.95, 1.5),
        "o(n^2)" | "o(n²)" | "o(nm)" | "o(n·m)" | "o(n*m)" | "o(nk)" | "o(n·k)" | "o(n*k)" | "o(n·w)" | "o(nw)" => {
            (1.6, 2.4)
        }
        "o(n^3)" => (2.5, 3.4),
        "o(2^n)" | "o(n2^n)" | "o(n·2^n)" | "o(n*2^n)" | "o(n!)" | "o(n·n!)" => (2.5, 100.0),
        _ => return None,
    })
}

/// Answer, tolerance, reject and accept checks for one quiz question.
fn check_question(q: &Question, at: &str) -> Vec<String> {
    let mut problems = Vec::new();
    if q.is_choice() {
        let n = q.choices.len() as f64;
        if q.answer.fract() != 0.0 || q.answer < 1.0 || q.answer > n {
            problems.push(format!("{at}: answer {} is not a choice number from 1 to {n}", q.answer));
        }
        if q.choices.len() < 2 {
            problems.push(format!("{at}: needs at least two choices"));
        }
    } else if !(q.tolerance > 0.0 && q.tolerance <= 1.0) {
        problems.push(format!("{at}: tolerance {} must be in (0, 1]", q.tolerance));
    }
    if q.explanation.trim().is_empty() {
        problems.push(format!("{at}: no explanation"));
    }
    if q.is_choice() && !(q.reject.is_empty() && q.accept.is_empty()) {
        problems.push(format!("{at}: reject and accept are for number questions"));
    }
    for &v in &q.reject {
        if quiz::is_correct(q, quiz::Answer::Number(v)) {
            problems.push(format!("{at}: the wrong answer {v} is accepted; tighten the tolerance"));
        }
    }
    for &v in &q.accept {
        if !quiz::is_correct(q, quiz::Answer::Number(v)) {
            problems.push(format!("{at}: the reasonable answer {v} is rejected; widen the tolerance"));
        }
    }
    problems
}

/// Longest note under a diagram node before it runs into its neighbours.
const LABEL_MAX: usize = 24;
/// Packets beyond this blur into a solid line.
const PACKETS_MAX: u8 = 12;
/// Longest node label that fits a box in a three-column diagram.
const NODE_LABEL_MAX: usize = 16;

/// Static checks for a system design challenge: answers, tolerances, diagram references and explanations.
pub fn check_design(ch: &Challenge) -> Vec<String> {
    let mut problems = Vec::new();
    let m = &ch.meta;
    let nodes: Vec<&str> = m.diagram.iter().flat_map(|d| d.nodes.iter().map(|n| n.id.as_str())).collect();
    let linked = |a: &str, b: &str| {
        m.diagram.iter().any(|d| d.links.iter().any(|[x, y]| (x == a && y == b) || (x == b && y == a)))
    };
    let check_steps = |steps: &[DiagramStep], at: &str, problems: &mut Vec<String>| {
        for (i, s) in steps.iter().enumerate() {
            for pair in s.flow.windows(2) {
                if !linked(&pair[0], &pair[1]) {
                    problems.push(format!("{at} step {}: flow {} -> {} has no link", i + 1, pair[0], pair[1]));
                }
            }
            for (node, label) in &s.labels {
                if label.chars().count() > LABEL_MAX {
                    problems.push(format!("{at} step {}: label on `{node}` is over {LABEL_MAX} characters", i + 1));
                }
            }
            if s.packets > PACKETS_MAX {
                problems.push(format!("{at} step {}: more than {PACKETS_MAX} packets", i + 1));
            }
            for id in s.flow.iter().chain(&s.highlight).chain(&s.down).chain(s.labels.keys()) {
                if !nodes.contains(&id.as_str()) {
                    problems.push(format!("{at} step {}: unknown node `{id}`", i + 1));
                }
            }
            if s.flow.len() == 1 {
                problems.push(format!("{at} step {}: a flow needs at least two nodes", i + 1));
            }
        }
    };
    if let Some(d) = &m.diagram {
        for n in &d.nodes {
            if n.label.chars().count() > NODE_LABEL_MAX {
                problems.push(format!("node `{}` label is over {NODE_LABEL_MAX} characters", n.id));
            }
            if n.at[0] > 2 || n.at[1] > 2 {
                problems.push(format!("node `{}` is outside the 3 x 3 grid", n.id));
            }
        }
        for [a, b] in &d.links {
            for id in [a, b] {
                if !nodes.contains(&id.as_str()) {
                    problems.push(format!("diagram link uses unknown node `{id}`"));
                }
            }
        }
        check_steps(&d.steps, "diagram", &mut problems);
    } else {
        problems.push("no [diagram]".into());
    }
    match m.stage {
        Stage::Watch => {
            if m.diagram.as_ref().is_none_or(|d| d.steps.len() < 3) {
                problems.push("a walkthrough needs at least 3 diagram steps".into());
            }
            if m.diagram.as_ref().is_some_and(|d| d.steps.iter().any(|s| s.caption.trim().is_empty())) {
                problems.push("every walkthrough step needs a caption".into());
            }
            if !m.questions.is_empty() {
                problems.push("a walkthrough has no questions".into());
            }
        }
        Stage::Quiz => {
            if !(2..=6).contains(&m.questions.len()) {
                problems.push(format!("expected 2-6 questions, found {}", m.questions.len()));
            }
            for (i, q) in m.questions.iter().enumerate() {
                let at = format!("question {}", i + 1);
                problems.extend(check_question(q, &at));
                check_steps(&q.steps, &at, &mut problems);
            }
        }
        other => problems.push(format!("stage {other:?} is not used in system design")),
    }
    problems
}

/// Time limit for one alternative's full suite.
const ALTERNATIVE_TIMEOUT: std::time::Duration = std::time::Duration::from_secs(240);

/// Print every alternative's measured outcome, not only the failures.
static VERBOSE: AtomicBool = AtomicBool::new(false);

/// Run an alternative solution and compare its outcome with the one it declares. Returns the problems and
/// a one-line note of what it measured.
fn check_alternative(ch: &Challenge, alt: &Alternative) -> (Vec<String>, String) {
    // slow alternatives run until their step budget; on a busy CI runner that takes longer than a learner waits
    let outcome = match runner::run_with(ch, Mode::Score, &alt.code, &runner::python(), ALTERNATIVE_TIMEOUT) {
        Ok(Outcome::Score(s)) => s,
        Ok(_) => return (vec![format!("{}: wrong outcome kind", alt.name)], String::new()),
        Err(e) => {
            // a timeout or crash is a failure, which is only right for `fail`
            let note = format!("{} expects {:?}: crashed or timed out", short_name(alt), alt.expect);
            return if alt.expect == Expect::Fail {
                (Vec::new(), note)
            } else {
                (vec![format!("{}: {e}", alt.name)], note)
            };
        }
    };
    let passed = outcome.error.is_none() && outcome.total > 0 && outcome.passed == outcome.total;
    let grade =
        outcome.steps.as_ref().filter(|_| passed).map(|st| scoring::grade(st, outcome.step_limit_hit.is_some()));
    let got = match (&grade, passed) {
        (_, false) => "fail".to_string(),
        (Some(r), true) => {
            format!("{:?} (exponent {:.2} vs {:.2}, {:.2}x steps)", r.grade, r.user_slope, r.ref_slope, r.ratio)
                .to_lowercase()
        }
        (None, true) => "pass without a grade".to_string(),
    };
    let ok = match alt.expect {
        Expect::Fail => !passed,
        Expect::Pass => passed,
        Expect::Gold => grade.as_ref().is_some_and(|r| r.grade == Grade::Gold),
        Expect::Silver => grade.as_ref().is_some_and(|r| r.grade == Grade::Silver),
        Expect::Bronze => grade.as_ref().is_some_and(|r| r.grade == Grade::Bronze),
        Expect::Slow => grade.as_ref().is_some_and(|r| r.grade != Grade::Gold),
    };
    let note = format!("{} {} expects {:?}: {got}", if ok { "ok  " } else { "FAIL" }, short_name(alt), alt.expect);
    if ok {
        return (Vec::new(), note);
    }
    let detail = outcome
        .failures
        .first()
        .map(|f| format!(" (first failure: input {} expected {} got {})", f.input, f.expected, f.got));
    let err = outcome
        .error
        .as_ref()
        .map(|e| format!(" (error: {})", e.text.lines().last().unwrap_or("")))
        .unwrap_or_default();
    let problem = format!("{}: expected {:?}, got {got}{}{err}", alt.name, alt.expect, detail.unwrap_or_default());
    (vec![problem], note)
}

fn short_name(alt: &Alternative) -> &str {
    alt.name.rsplit('/').next().unwrap_or(&alt.name)
}

/// Problems with a code challenge, plus notes on what its alternatives measured.
fn check_one(ch: &Challenge) -> (Vec<String>, Vec<String>) {
    let mut problems = Vec::new();
    let mut notes = Vec::new();
    // the reference must trace cleanly on the visual example
    match runner::run(ch, Mode::Visual, &ch.reference) {
        Ok(Outcome::Visual(v)) => {
            if let Some(e) = &v.error {
                problems.push(format!(
                    "visual: reference raised: {} {}",
                    e.text,
                    e.internal.clone().unwrap_or_default()
                ));
            }
            if v.frames.is_empty() {
                problems.push("visual: no frames recorded".into());
            }
            if v.truncated {
                problems.push(format!("visual: trace truncated at {} frames; use a smaller example", v.frames.len()));
            }
            if v.passed == Some(false) {
                problems.push("visual: reference disagrees with itself".into());
            }
            for spec in &ch.meta.view {
                if !v.frames.iter().any(|f| f.var(&spec.var).is_some()) {
                    problems.push(format!("visual: view variable `{}` never appears", spec.var));
                }
            }
            if v.frames.len() > 900 {
                problems.push(format!("visual: {} frames is long to watch; aim for under 900", v.frames.len()));
            }
        }
        Ok(_) => problems.push("visual: wrong outcome kind".into()),
        Err(e) => problems.push(format!("visual: {e}")),
    }
    if ch.meta.stage == Stage::Watch {
        return (problems, notes);
    }
    match runner::run(ch, Mode::Score, &ch.reference) {
        Ok(Outcome::Score(s)) => {
            if let Some(e) = &s.error {
                problems.push(format!(
                    "score: reference raised: {} {}",
                    e.text,
                    e.internal.clone().unwrap_or_default()
                ));
            } else if s.passed != s.total || s.total == 0 {
                problems.push(format!("score: reference passed {}/{}", s.passed, s.total));
            }
            match &s.steps {
                Some(steps) => {
                    let r = scoring::grade(steps, s.step_limit_hit.is_some());
                    if r.grade != Grade::Gold {
                        problems.push(format!("score: reference graded {:?}", r.grade));
                    }
                    if let Some(n) = s.step_limit_hit {
                        problems.push(format!("score: reference hit the step limit at n={n}"));
                    }
                    match expected_slope(&ch.meta.complexity) {
                        Some((lo, hi)) if r.ref_slope < lo || r.ref_slope > hi => problems.push(format!(
                            "score: declared {} but measured exponent {:.2} (steps {:?})",
                            ch.meta.complexity, r.ref_slope, steps.reference
                        )),
                        None => problems.push(format!("score: unknown complexity string {}", ch.meta.complexity)),
                        _ => {}
                    }
                }
                None if s.error.is_none() => problems.push("score: no step measurements".into()),
                None => {}
            }
        }
        Ok(_) => problems.push("score: wrong outcome kind".into()),
        Err(e) => problems.push(format!("score: {e}")),
    }
    for alt in &ch.alternatives {
        let (p, note) = check_alternative(ch, alt);
        problems.extend(p);
        notes.push(note);
    }
    match runner::run(ch, Mode::Score, &ch.starter) {
        Ok(Outcome::Score(s)) => {
            if s.error.is_none() && s.total > 0 && s.passed == s.total {
                problems.push("starter: passes every case; it should not".into());
            }
        }
        Ok(_) => {}
        Err(e) => problems.push(format!("starter: {e}")),
    }
    (problems, notes)
}

pub fn run(lib: &Library, topic_filter: Option<&str>, verbose: bool) -> Result<()> {
    VERBOSE.store(verbose, Ordering::Relaxed);
    runner::check_python()?;
    let jobs: Vec<&Challenge> = lib
        .topics
        .iter()
        .filter(|t| match topic_filter {
            // an exact id wins over substring matches
            Some(f) if lib.topic(f).is_some() => t.meta.id == f,
            Some(f) => t.meta.id.contains(f),
            None => true,
        })
        .flat_map(|t| t.challenges.iter())
        .collect();
    let mut order_problems = Vec::new();
    for t in &lib.topics {
        let stages: Vec<Stage> = t.challenges.iter().map(|c| c.meta.stage).collect();
        if t.meta.track == Track::Design {
            let quizzes = stages.iter().filter(|s| **s == Stage::Quiz).count();
            if stages.first() != Some(&Stage::Watch) || quizzes != stages.len() - 1 || !(2..=4).contains(&quizzes) {
                order_problems
                    .push(format!("topic {}: expected one watch, then 2-4 quizzes; got {:?}", t.meta.id, stages));
            }
            continue;
        }
        let watch = stages.iter().filter(|s| **s == Stage::Watch).count();
        let build = stages.iter().filter(|s| **s == Stage::Build).count();
        let apply = stages.iter().filter(|s| **s == Stage::Apply).count();
        let mut sorted = stages.clone();
        sorted.sort_by_key(|s| *s as u8);
        if watch != 1 || build == 0 || !(1..=4).contains(&apply) || sorted != stages {
            order_problems.push(format!(
                "topic {}: expected one watch, then builds, then 1-4 applies; got {:?}",
                t.meta.id, stages
            ));
        }
    }
    for p in &order_problems {
        println!("FAIL {p}");
    }
    let queue = Mutex::new(jobs.iter().enumerate().collect::<Vec<_>>());
    let results = Mutex::new(vec![Vec::new(); jobs.len()]);
    let workers = thread::available_parallelism().map_or(4, std::num::NonZero::get).min(8);
    thread::scope(|s| {
        for _ in 0..workers {
            s.spawn(|| {
                loop {
                    let next = queue.lock().unwrap().pop();
                    let Some((i, ch)) = next else { break };
                    let design = lib.topic(&ch.topic).is_some_and(|t| t.meta.track == Track::Design);
                    let (problems, notes) = if design { (check_design(ch), Vec::new()) } else { check_one(ch) };
                    let status = if problems.is_empty() { "ok  " } else { "FAIL" };
                    // one print per challenge, so lines from parallel workers never interleave
                    let mut block = format!("{status} {}", ch.key());
                    if VERBOSE.load(Ordering::Relaxed) {
                        for note in &notes {
                            let _ = write!(block, "\n       {note}");
                        }
                    }
                    println!("{block}");
                    results.lock().unwrap()[i] = problems;
                }
            });
        }
    });
    let results = results.into_inner().unwrap();
    let mut failed = 0;
    for (ch, problems) in jobs.iter().zip(&results) {
        if problems.is_empty() {
            continue;
        }
        failed += 1;
        println!("\n{}", ch.key());
        for p in problems {
            println!("  - {p}");
        }
    }
    failed += order_problems.len();
    println!("\n{} challenges checked, {failed} with problems", jobs.len());
    if failed > 0 {
        bail!("{failed} challenges failed the content check");
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn complexity_strings_map_to_ranges() {
        assert!(expected_slope("O(n)").is_some());
        assert!(expected_slope("O(n log n)").is_some());
        assert!(expected_slope("O(n^2)").is_some());
        assert!(expected_slope("amortized O(1)").is_some());
        assert!(expected_slope("O(V + E)").is_some());
        assert!(expected_slope("O(weird)").is_none());
    }
}
