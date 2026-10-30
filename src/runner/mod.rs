//! Runs solutions through the Python harness in a child process.

pub mod trace;

use std::fs;
use std::path::Path;
use std::process::{Command, Stdio};
use std::sync::mpsc::{self, Receiver, Sender};
use std::thread;
use std::time::{Duration, Instant};

use anyhow::{Context, Result, anyhow};
use serde_json::{Value, json};

use crate::content::{Challenge, Kind};
use trace::{ScoreResult, VisualResult};

const HARNESS_FILES: [(&str, &str); 5] = [
    ("harness.py", include_str!("../../harness/harness.py")),
    ("guard.py", include_str!("../../harness/guard.py")),
    ("tracer.py", include_str!("../../harness/tracer.py")),
    ("traced.py", include_str!("../../harness/traced.py")),
    ("algoscope.py", include_str!("../../harness/algoscope.py")),
];

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Mode {
    Visual,
    Score,
}

impl Mode {
    fn arg(self) -> &'static str {
        match self {
            Mode::Visual => "visual",
            Mode::Score => "score",
        }
    }

    fn timeout(self) -> Duration {
        match self {
            Mode::Visual => Duration::from_secs(8),
            Mode::Score => Duration::from_secs(60),
        }
    }
}

#[derive(Debug, Clone)]
pub enum Outcome {
    Visual(VisualResult),
    Score(ScoreResult),
}

#[derive(Debug, Clone)]
pub struct Job {
    pub id: u64,
    pub mode: Mode,
    pub challenge: Challenge,
    pub solution: String,
}

pub struct Done {
    pub id: u64,
    pub key: String,
    pub elapsed: Duration,
    pub result: Result<Outcome, String>,
}

/// Harness configuration for one challenge.
pub fn config(ch: &Challenge, mode: Mode) -> Value {
    let m = &ch.meta;
    let mut cfg = json!({
        "kind": match m.kind { Kind::Function => "function", Kind::Class => "class" },
        "entry": m.entry,
        "output": m.output,
        "watch": ch.watch_names(),
        "forbid": m.forbid,
        "max_frames": if mode == Mode::Visual { 2500 } else { 0 },
    });
    if let Some(s) = &m.sizes {
        cfg["sizes"] = json!(s);
    }
    if let Some(s) = &m.check_sizes {
        cfg["check_sizes"] = json!(s);
    }
    if let Some(s) = m.seeds {
        cfg["seeds"] = json!(s);
    }
    cfg
}

/// Environment variables the harness keeps: enough for Python to start on every platform.
const PASS_ENV: [&str; 8] = ["PATH", "SYSTEMROOT", "WINDIR", "TEMP", "TMP", "TMPDIR", "LANG", "LC_ALL"];

/// Python interpreter to use: $`ALGOSCOPE_PYTHON` or python3.
pub fn python() -> String {
    std::env::var("ALGOSCOPE_PYTHON").unwrap_or_else(|_| if cfg!(windows) { "python" } else { "python3" }.into())
}

/// Returns the Python version, or an error explaining why it cannot be used.
pub fn check_python() -> Result<(u32, u32)> {
    check_python_at(&python())
}

/// Version check for a specific interpreter.
pub fn check_python_at(py: &str) -> Result<(u32, u32)> {
    let py = py.to_string();
    let out = Command::new(&py)
        .args(["-I", "-c", "import sys; print(sys.version_info[0], sys.version_info[1])"])
        .output()
        .with_context(|| format!("could not run `{py}`; install Python 3.10+ or set ALGOSCOPE_PYTHON"))?;
    let text = String::from_utf8_lossy(&out.stdout);
    let mut parts = text.split_whitespace().filter_map(|p| p.parse::<u32>().ok());
    let (major, minor) = (parts.next().unwrap_or(0), parts.next().unwrap_or(0));
    if (major, minor) < (3, 10) {
        return Err(anyhow!("`{py}` is Python {major}.{minor}; algoscope needs 3.10 or newer"));
    }
    Ok((major, minor))
}

fn write_run_dir(dir: &Path, ch: &Challenge, mode: Mode, solution: &str) -> Result<()> {
    let h = dir.join("_harness");
    fs::create_dir_all(&h)?;
    for (name, body) in HARNESS_FILES {
        fs::write(h.join(name), body)?;
    }
    fs::write(dir.join("solution.py"), solution)?;
    fs::write(dir.join("reference.py"), &ch.reference)?;
    fs::write(dir.join("cases.py"), &ch.cases)?;
    fs::write(dir.join("config.json"), serde_json::to_vec(&config(ch, mode))?)?;
    Ok(())
}

/// Run one job synchronously.
pub fn run(ch: &Challenge, mode: Mode, solution: &str) -> Result<Outcome, String> {
    run_with(ch, mode, solution, &python(), mode.timeout())
}

/// Run one job with an explicit interpreter and time limit.
pub fn run_with(
    ch: &Challenge,
    mode: Mode,
    solution: &str,
    python: &str,
    timeout: Duration,
) -> Result<Outcome, String> {
    run_inner(ch, mode, solution, python, timeout).map_err(|e| format!("{e:#}"))
}

fn run_inner(ch: &Challenge, mode: Mode, solution: &str, python: &str, timeout: Duration) -> Result<Outcome> {
    let dir = tempfile::Builder::new().prefix("algoscope-").tempdir()?;
    write_run_dir(dir.path(), ch, mode, solution)?;
    let stderr_path = dir.path().join("stderr.txt");
    let mut child = Command::new(python)
        .arg("-I")
        .arg(dir.path().join("_harness").join("harness.py"))
        .arg(dir.path())
        .arg(mode.arg())
        .current_dir(dir.path())
        // solutions see a minimal environment: no tokens or credentials from the user's shell
        .env_clear()
        .envs(std::env::vars_os().filter(|(k, _)| PASS_ENV.iter().any(|p| k.eq_ignore_ascii_case(p))))
        .stdin(Stdio::null())
        .stdout(Stdio::null())
        .stderr(Stdio::from(fs::File::create(&stderr_path)?))
        .spawn()
        .with_context(|| format!("could not start `{python}`"))?;
    let start = Instant::now();
    let status = loop {
        if let Some(status) = child.try_wait()? {
            break status;
        }
        if start.elapsed() > timeout {
            let _ = child.kill();
            let _ = child.wait();
            return Err(anyhow!(
                "timed out after {}s: look for an infinite loop or a very slow path",
                timeout.as_secs()
            ));
        }
        thread::sleep(Duration::from_millis(10));
    };
    let out_path = dir.path().join("out.json");
    if !out_path.exists() {
        let stderr = fs::read_to_string(&stderr_path).unwrap_or_default();
        let tail: String =
            stderr.lines().rev().take(6).collect::<Vec<_>>().into_iter().rev().collect::<Vec<_>>().join("\n");
        return Err(anyhow!("the harness exited with {status} and no result\n{tail}"));
    }
    let raw: Value = serde_json::from_slice(&fs::read(&out_path)?).context("reading harness output")?;
    Ok(match mode {
        Mode::Visual => Outcome::Visual(VisualResult::from_json(&raw)),
        Mode::Score => Outcome::Score(serde_json::from_value(raw).context("decoding score result")?),
    })
}

/// Background worker that runs jobs one at a time.
pub struct Worker {
    tx: Sender<Job>,
    pub rx: Receiver<Done>,
    next_id: u64,
}

impl Worker {
    pub fn spawn() -> Worker {
        let (tx, job_rx) = mpsc::channel::<Job>();
        let (done_tx, rx) = mpsc::channel::<Done>();
        thread::spawn(move || {
            while let Ok(job) = job_rx.recv() {
                let start = Instant::now();
                let result = run(&job.challenge, job.mode, &job.solution);
                let done = Done { id: job.id, key: job.challenge.key(), elapsed: start.elapsed(), result };
                if done_tx.send(done).is_err() {
                    break;
                }
            }
        });
        Worker { tx, rx, next_id: 1 }
    }

    pub fn submit(&mut self, mode: Mode, challenge: &Challenge, solution: String) -> u64 {
        let id = self.next_id;
        self.next_id += 1;
        let _ = self.tx.send(Job { id, mode, challenge: challenge.clone(), solution });
        id
    }
}
