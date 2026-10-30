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
# push the tag by name: --follow-tags skips lightweight tags
git push -q origin main "v$version"

echo "waiting for the release workflow for v$version"
run=""
for _ in $(seq 1 30); do
    run="$(gh run list --workflow release.yml --limit 10 --json databaseId,headBranch \
        -q ".[] | select(.headBranch == \"v$version\") | .databaseId" | head -1)"
    [ -n "$run" ] && break
    sleep 10
done
if [ -z "$run" ]; then
    echo "no release workflow run found for v$version" >&2
    exit 1
fi
gh run watch "$run" --exit-status --interval 30 > /dev/null
gh release view "v$version" --json url -q .url

scripts/update-tap.sh "$version"
