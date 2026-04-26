#!/usr/bin/env bash
# scripts/release.sh — cut a Sillok release.
#
# Usage:
#   bash scripts/release.sh patch                # 0.1.0 → 0.1.1
#   bash scripts/release.sh minor                # 0.1.x → 0.2.0
#   bash scripts/release.sh major                # 0.x.y → 1.0.0
#   bash scripts/release.sh exact 0.1.0a2        # explicit version
#
# Prerequisites:
#   - clean working tree on `main`
#   - gh CLI authenticated with repo write access
#   - uv installed (or twine + build)
#   - PyPI publishing handled by the maintainer separately
#     (this script does NOT publish to PyPI to prevent accidental ships)
#
# Steps performed:
#   1. compute next version
#   2. bump pyproject.toml [project] version
#   3. update CHANGELOG.md (move [Unreleased] → [<version>])
#   4. commit + tag v<version>
#   5. push branch and tag
#   6. open a draft GitHub Release with auto-generated notes
#
# After this script, the maintainer:
#   - reviews the draft release
#   - publishes the release (auto-builds the wheel via GH Actions)
#   - runs `uv publish` from a project-scoped PyPI token environment
#   - flips the release from draft → published

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

usage() {
  cat >&2 <<USAGE
Usage:
  bash scripts/release.sh patch | minor | major
  bash scripts/release.sh exact <version>

Examples:
  bash scripts/release.sh minor
  bash scripts/release.sh exact 0.1.0a2
USAGE
  exit 64
}

[[ $# -ge 1 ]] || usage

current_version() {
  awk -F\" '/^version *=/{print $2; exit}' pyproject.toml
}

bump_version() {
  local cur="$1" kind="$2"
  python3 - "$cur" "$kind" <<'PY'
import re
import sys

cur, kind = sys.argv[1], sys.argv[2]

m = re.match(r"^(\d+)\.(\d+)\.(\d+)([a-z][0-9a-z]*)?$", cur)
if not m:
    sys.exit(f"unrecognized version: {cur}")
major, minor, patch = int(m.group(1)), int(m.group(2)), int(m.group(3))

if kind == "major":
    major += 1
    minor = patch = 0
elif kind == "minor":
    minor += 1
    patch = 0
elif kind == "patch":
    patch += 1
else:
    sys.exit(f"unknown kind: {kind}")

print(f"{major}.{minor}.{patch}")
PY
}

case "$1" in
  patch|minor|major)
    cur="$(current_version)"
    next="$(bump_version "$cur" "$1")"
    ;;
  exact)
    [[ $# -eq 2 ]] || usage
    next="$2"
    cur="$(current_version)"
    ;;
  *)
    usage
    ;;
esac

echo "current: $cur"
echo "next:    $next"
read -rp "Proceed? [y/N] " ok
[[ "$ok" =~ ^[Yy]$ ]] || { echo "aborted"; exit 1; }

# 1. clean tree check
if ! git diff-index --quiet HEAD --; then
  echo "error: working tree not clean" >&2
  exit 2
fi

# 2. bump pyproject.toml
sed -E -i.bak "s/^version *= *\"[^\"]*\"/version = \"$next\"/" pyproject.toml
rm -f pyproject.toml.bak

# 3. CHANGELOG: Unreleased → [<next>] — <date>
today="$(date -u +%F)"
python3 - "$next" "$today" <<'PY'
import sys
from pathlib import Path

next_version, today = sys.argv[1], sys.argv[2]
path = Path("CHANGELOG.md")
text = path.read_text(encoding="utf-8")

needle = "## [Unreleased]"
if needle not in text:
    sys.exit("CHANGELOG.md missing [Unreleased] header")

new_section = f"## [Unreleased]\n\n### Added\n- (none yet)\n\n## [{next_version}] — {today}"
text = text.replace(needle, new_section, 1)

path.write_text(text, encoding="utf-8")
print(f"CHANGELOG.md updated for {next_version}")
PY

# 4. commit + tag
git add pyproject.toml CHANGELOG.md
git commit -m "[release] $next"
git tag -a "v$next" -m "v$next"

# 5. push
git push origin main
git push origin "v$next"

# 6. draft release
gh release create "v$next" \
  --draft \
  --generate-notes \
  --title "v$next" || {
  echo "warn: gh release create failed; create the release manually." >&2
}

cat <<DONE

Release draft created. Next steps for the maintainer:

  1. Review the draft at: gh release view v$next --web
  2. Edit notes if needed
  3. Publish the release (gh release edit v$next --draft=false)
  4. Build and publish the wheel:
       uv build
       uv publish --token <project-scoped PyPI token>
  5. Yank the previous placeholder if applicable:
       (manual via PyPI web UI or twine)

DONE
