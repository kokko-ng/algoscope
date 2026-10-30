//! Terminal setup and the event loop.

pub mod editor;
pub mod theme;
pub mod ui;
pub mod viz;

use std::io::stdout;
use std::time::{Duration, Instant};

use anyhow::Result;
use ratatui::crossterm::event::{self, DisableBracketedPaste, EnableBracketedPaste, Event, KeyEventKind};
use ratatui::crossterm::execute;

use crate::app::App;

const TICK: Duration = Duration::from_millis(33);

pub fn run(mut app: App) -> Result<()> {
    let mut terminal = ratatui::init();
    let _ = execute!(stdout(), EnableBracketedPaste);
    let result = event_loop(&mut terminal, &mut app);
    let _ = execute!(stdout(), DisableBracketedPaste);
    ratatui::restore();
    result
}

fn event_loop(terminal: &mut ratatui::DefaultTerminal, app: &mut App) -> Result<()> {
    let mut last = Instant::now();
    while !app.quit {
        terminal.draw(|f| ui::draw(f, app))?;
        let timeout = TICK.saturating_sub(last.elapsed());
        if event::poll(timeout)? {
            match event::read()? {
                Event::Key(key) if key.kind == KeyEventKind::Press || key.kind == KeyEventKind::Repeat => {
                    app.on_key(key);
                }
                Event::Paste(text) => app.on_paste(&text),
                _ => {}
            }
        }
        if last.elapsed() >= TICK {
            let elapsed = last.elapsed();
            last = Instant::now();
            app.tick(elapsed);
        }
    }
    Ok(())
}
