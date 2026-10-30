#!/usr/bin/env bash
# Cut a release: bump the version and changelog with commitizen, push the tag, wait for the release
# workflow to publish binaries, then update the Homebrew formula.
#   scripts/release.sh            # version from the commit history
#   scripts/release.sh 0.3.0      # explicit version
set -euo pipefail
cd "$(dirname "$0")/.."

if [ -n "$(git status --porcelain)" ]; then
    echo "the working tree is not clean" >&2
    exit 1
fi
if [ "$(git symbolic-ref --short HEAD)" != "main" ]; then
    echo "release from main" >&2
    exit 1
fi
git pull -q --ff-only

if [ $# -gt 0 ]; then cz bump --yes "$1"; else cz bump --yes; fi
version="$(cz version --project)"
git push -q --follow-tags

echo "waiting for the release workflow for v$version"
sleep 10
run="$(gh run list --workflow release.yml --branch "v$version" --limit 1 --json databaseId -q '.[0].databaseId')"
gh run watch "$run" --exit-status --interval 30 > /dev/null
gh release view "v$version" --json url -q .url

scripts/update-tap.sh "$version"
