#!/usr/bin/env bash
# Render the Homebrew formula for a published release and push it to kokko-ng/homebrew-tap.
#   scripts/update-tap.sh 0.2.0
set -euo pipefail
version="${1:?usage: scripts/update-tap.sh VERSION}"
root="$(cd "$(dirname "$0")/.." && pwd)"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

gh release download "v$version" --repo kokko-ng/algoscope --pattern '*.tar.gz.sha256' --dir "$work/sums"
formula="$(sed "s/@VERSION@/$version/g" "$root/packaging/algoscope.rb.template")"
for target in aarch64-apple-darwin x86_64-apple-darwin aarch64-unknown-linux-gnu x86_64-unknown-linux-gnu; do
    sum="$(cut -d' ' -f1 "$work/sums/algoscope-v$version-$target.tar.gz.sha256")"
    formula="${formula//@SHA_$target@/$sum}"
done
if grep -q '@SHA_' <<<"$formula"; then
    echo "a checksum is missing from the release" >&2
    exit 1
fi

gh repo clone kokko-ng/homebrew-tap "$work/tap" -- --quiet
mkdir -p "$work/tap/Formula"
printf '%s\n' "$formula" > "$work/tap/Formula/algoscope.rb"
cd "$work/tap"
git add Formula/algoscope.rb
if git diff --cached --quiet; then
    echo "formula already at $version"
    exit 0
fi
git commit -q -m "feat(algoscope): $version"
git push -q
echo "kokko-ng/homebrew-tap: algoscope $version"
