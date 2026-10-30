#!/usr/bin/env bash
# Run cargo from git hooks, which may not inherit an interactive shell's PATH.
# Falls back to the usual rustup locations, including Homebrew's keg-only rustup.
set -euo pipefail
if ! command -v cargo >/dev/null 2>&1; then
    for dir in "$HOME/.cargo/bin" /opt/homebrew/opt/rustup/bin /usr/local/opt/rustup/bin; do
        if [ -x "$dir/cargo" ]; then
            PATH="$dir:$PATH"
            break
        fi
    done
fi
exec cargo "$@"
