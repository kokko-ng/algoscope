//! `algoscope check-content`: verifies every challenge end to end through the real harness.

use std::sync::Mutex;
use std::thread;

use anyhow::{Result, bail};

use crate::content::{Challenge, Library, Stage};
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
        "o(n^2)" | "o(n²)" | "o(nm)" | "o(n·m)" | "o(n*m)" | "o(nk)" | "o(n·w)" | "o(nw)" => (1.6, 2.4),
        "o(n^3)" => (2.5, 3.4),
        _ => return None,
    })
}

fn check_one(ch: &Challenge) -> Vec<String> {
    let mut problems = Vec::new();
    // the reference must trace cleanly on the visual example
    match runner::run(ch, Mode::Visual, &ch.reference) {
        Ok(Outcome::Visual(v)) => {
            if let Some(e) = &v.error {
                problems.push(format!("visual: reference raised: {} {}", e.text, e.internal.clone().unwrap_or_default()));
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
        return problems;
    }
    match runner::run(ch, Mode::Score, &ch.reference) {
        Ok(Outcome::Score(s)) => {
            if let Some(e) = &s.error {
                problems.push(format!("score: reference raised: {} {}", e.text, e.internal.clone().unwrap_or_default()));
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
    match runner::run(ch, Mode::Score, &ch.starter) {
        Ok(Outcome::Score(s)) => {
            if s.error.is_none() && s.total > 0 && s.passed == s.total {
                problems.push("starter: passes every case; it should not".into());
            }
        }
        Ok(_) => {}
        Err(e) => problems.push(format!("starter: {e}")),
    }
    problems
}

pub fn run(lib: &Library, topic_filter: Option<&str>) -> Result<()> {
    runner::check_python()?;
    let jobs: Vec<&Challenge> = lib
        .topics
        .iter()
        .filter(|t| topic_filter.is_none_or(|f| t.meta.id.contains(f)))
        .flat_map(|t| t.challenges.iter())
        .collect();
    let queue = Mutex::new(jobs.iter().enumerate().collect::<Vec<_>>());
    let results = Mutex::new(vec![Vec::new(); jobs.len()]);
    let workers = thread::available_parallelism().map_or(4, |n| n.get()).min(8);
    thread::scope(|s| {
        for _ in 0..workers {
            s.spawn(|| {
                loop {
                    let next = queue.lock().unwrap().pop();
                    let Some((i, ch)) = next else { break };
                    let problems = check_one(ch);
                    let status = if problems.is_empty() { "ok  " } else { "FAIL" };
                    println!("{status} {}", ch.key());
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
