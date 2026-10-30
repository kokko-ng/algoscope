mod app;
mod check;
mod content;
mod progress;
mod runner;
mod scoring;
mod tui;

use anyhow::Result;
use clap::{Parser, Subcommand};

use crate::content::Library;
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
    },
    /// Delete saved progress, drafts and settings.
    Reset,
    /// Print where progress is stored.
    Where,
}

fn main() -> Result<()> {
    let cli = Cli::parse();
    let lib = Library::load()?;
    match cli.command {
        Some(Command::CheckContent { topic }) => check::run(&lib, topic.as_deref()),
        Some(Command::Reset) => {
            Store::new(data_dir()).reset()?;
            println!("progress, drafts and settings deleted from {}", data_dir().display());
            Ok(())
        }
        Some(Command::Where) => {
            println!("{}", data_dir().display());
            Ok(())
        }
        None => {
            runner::check_python()?;
            let app = app::App::new(lib, Store::new(data_dir()));
            tui::run(app)
        }
    }
}
