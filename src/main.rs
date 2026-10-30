mod app;
mod app_quiz;
mod check;
mod content;
mod progress;
mod quiz;
mod runner;
mod scoring;
mod tui;

use anyhow::Result;
use clap::{Parser, Subcommand};

use crate::content::{Library, Track};
use crate::progress::{Store, data_dir};

/// A terminal workbench for data structures and algorithms: write Python, watch it run, profile it.
#[derive(Parser)]
#[command(version, about)]
struct Cli {
    #[command(subcommand)]
    command: Option<Command>,
}

#[derive(Subcommand)]
enum Command {
    /// Verify every challenge: references pass and grade gold, starters fail, growth matches.
    CheckContent {
        /// Only check topics whose id contains this text.
        #[arg(long)]
        topic: Option<String>,
        /// Check topics in this directory on disk instead of the embedded content.
        #[arg(long)]
        dir: Option<std::path::PathBuf>,
    },
    /// Delete saved progress, drafts and settings.
    Reset,
    /// Print where progress is stored.
    Where,
    /// Start on the data structures and algorithms track.
    Dsa,
    /// Start on the system design track.
    Design,
}

fn main() -> Result<()> {
    let cli = Cli::parse();
    let lib = Library::load()?;
    match cli.command {
        Some(Command::CheckContent { topic, dir }) => {
            let lib = match dir {
                Some(d) => Library::from_fs(&d)?,
                None => lib,
            };
            check::run(&lib, topic.as_deref())
        }
        Some(Command::Reset) => {
            Store::new(data_dir()).reset()?;
            println!("progress, drafts and settings deleted from {}", data_dir().display());
            Ok(())
        }
        Some(Command::Where) => {
            println!("{}", data_dir().display());
            Ok(())
        }
        None | Some(Command::Dsa | Command::Design) => {
            runner::check_python()?;
            let mut app = app::App::new(lib, Store::new(data_dir()));
            match cli.command {
                Some(Command::Dsa) => app.set_track(Track::Dsa),
                Some(Command::Design) => app.set_track(Track::Design),
                _ => {}
            }
            tui::run(app)
        }
    }
}
