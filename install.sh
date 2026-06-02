#!/bin/bash
#
# CCFBar one-click installer.
#
# Usage (recommended):
#   curl -fsSL https://github.com/superpung/swiftbar-ccfddl/releases/latest/download/install.sh | bash
#
# Re-running upgrades the plugin in place and never overwrites an existing
# ~/.config/ccfbar/config.json.
#
# Optional environment overrides:
#   CCFBAR_REFRESH       refresh interval baked into the plugin filename (default: 1h)
#   CCFBAR_PLUGIN_URL    override the plugin download URL (advanced / testing)
#   CCFBAR_CONFIG        override the config path (default: ~/.config/ccfbar/config.json)
#   CCFBAR_DATA_DIR      override the conference YAML directory
#   CCFBAR_CONFERENCES   space-separated initial ccfddl files to download
#
set -euo pipefail

REPO="superpung/swiftbar-ccfddl"
APP_NAME="CCFBar"
REFRESH="${CCFBAR_REFRESH:-1h}"
PLUGIN_SOURCE="plugin/ccfbar.1h.py"
PLUGIN_ASSET="ccfbar.1h.py"
PLUGIN_NAME="ccfbar.${REFRESH}.py"
PLUGIN_URL="${CCFBAR_PLUGIN_URL:-https://github.com/${REPO}/releases/latest/download/${PLUGIN_ASSET}}"
SWIFTBAR_BUNDLE_ID="com.ameba.SwiftBar"
CCF_DEADLINES_RAW_BASE="https://raw.githubusercontent.com/ccfddl/ccf-deadlines/refs/heads/main/conference"
DEFAULT_CONFERENCES="SE/icse.yml"

info() { printf '\033[1;34m==>\033[0m %s\n' "$1"; }
die()  { printf '\033[1;31merror:\033[0m %s\n' "$1" >&2; exit 1; }

has_yaml_files() {
  for yaml_file in "$1"/*.yml "$1"/*.yaml; do
    if [ -f "$yaml_file" ]; then
      return 0
    fi
  done
  return 1
}

# 1. Sanity checks ----------------------------------------------------------
[ "$(uname -s)" = "Darwin" ] || die "$APP_NAME runs on macOS only."
command -v curl >/dev/null 2>&1 || die "curl is required but was not found."
command -v python3 >/dev/null 2>&1 || \
  die "python3 is required. Install the Xcode Command Line Tools: xcode-select --install"

# 2. Ensure SwiftBar is installed -------------------------------------------
if [ ! -d "/Applications/SwiftBar.app" ] && ! osascript -e 'id of app "SwiftBar"' >/dev/null 2>&1; then
  if command -v brew >/dev/null 2>&1; then
    info "SwiftBar not found - installing it with Homebrew..."
    brew install --cask swiftbar
  else
    die "SwiftBar is not installed. Get it from https://github.com/swiftbar/SwiftBar or install Homebrew and re-run."
  fi
fi

# 3. Resolve the SwiftBar plugin directory ----------------------------------
plugin_dir="$(defaults read "$SWIFTBAR_BUNDLE_ID" PluginDirectory 2>/dev/null || true)"
configured_dir=1
if [ -z "$plugin_dir" ]; then
  plugin_dir="$HOME/Library/Application Support/SwiftBar/Plugins"
  info "No SwiftBar plugin folder is set yet - using $plugin_dir"
  defaults write "$SWIFTBAR_BUNDLE_ID" PluginDirectory "$plugin_dir"
  configured_dir=0
fi
mkdir -p "$plugin_dir"

# 4. Install and validate the plugin ----------------------------------------
tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT

script_path="${BASH_SOURCE[0]:-$0}"
script_dir="$(CDPATH= cd "$(dirname "$script_path")" 2>/dev/null && pwd || pwd)"
if [ -f "$script_dir/$PLUGIN_SOURCE" ]; then
  info "Using local plugin file..."
  cp "$script_dir/$PLUGIN_SOURCE" "$tmp"
elif [ -f "$script_dir/$PLUGIN_ASSET" ]; then
  info "Using local plugin file..."
  cp "$script_dir/$PLUGIN_ASSET" "$tmp"
else
  info "Downloading the latest $APP_NAME plugin..."
  curl -fsSL "$PLUGIN_URL" -o "$tmp" || die "Could not download the plugin from $PLUGIN_URL"
fi

python3 -c "import ast,sys; ast.parse(open(sys.argv[1], encoding='utf-8').read())" "$tmp" \
  || die "The plugin file is not valid Python - aborting."

find "$plugin_dir" -maxdepth 1 -name 'ccfbar.*.py' -delete 2>/dev/null || true

dest="$plugin_dir/$PLUGIN_NAME"
mv "$tmp" "$dest"
trap - EXIT
chmod +x "$dest"
info "Installed the plugin -> $dest"

# 5. Scaffold config and initial data (never overwrites config) -------------
config="${CCFBAR_CONFIG:-${XDG_CONFIG_HOME:-$HOME/.config}/ccfbar/config.json}"
if [ -f "$config" ]; then
  info "Kept your existing config -> $config"
  fresh_config=0
else
  CCFBAR_CONFIG="$config" python3 "$dest" --init >/dev/null
  info "Created a starter config -> $config"
  fresh_config=1
fi

data_dir="$(CCFBAR_CONFIG="$config" python3 - "$config" <<'PY'
import json
import os
import sys

env = os.environ.get("CCFBAR_DATA_DIR")
if env:
    print(os.path.expandvars(os.path.expanduser(env)))
    raise SystemExit

with open(sys.argv[1], "r", encoding="utf-8") as handle:
    config = json.load(handle)

data_dir = config.get("data_dir") or "${HOME}/.config/ccfbar/conferences"
print(os.path.expandvars(os.path.expanduser(str(data_dir))))
PY
)"
mkdir -p "$data_dir"

conference_files="${CCFBAR_CONFERENCES:-}"
if [ -z "$conference_files" ]; then
conference_files="$(DEFAULT_CONFERENCES="$DEFAULT_CONFERENCES" python3 - "$config" <<'PY'
import json
import os
import sys

with open(sys.argv[1], "r", encoding="utf-8") as handle:
    config = json.load(handle)

print(" ".join(config.get("conferences") or os.environ["DEFAULT_CONFERENCES"].split()))
PY
)"
fi

raw_base="$(python3 - "$config" "$CCF_DEADLINES_RAW_BASE" <<'PY'
import json
import sys

with open(sys.argv[1], "r", encoding="utf-8") as handle:
    config = json.load(handle)

print((config.get("sources") or {}).get("raw_base_url") or sys.argv[2])
PY
)"

if ! has_yaml_files "$data_dir"; then
  for conference_file in $conference_files; do
    destination="$data_dir/$(basename "$conference_file")"
    info "Downloading $conference_file -> $destination"
    curl -fsSL "${raw_base%/}/$conference_file" -o "$destination" \
      || die "Could not download $conference_file"
  done
fi

# 6. (Re)launch and refresh SwiftBar ----------------------------------------
if [ "$configured_dir" -eq 0 ] && pgrep -x SwiftBar >/dev/null 2>&1; then
  osascript -e 'quit app "SwiftBar"' >/dev/null 2>&1 || true
  sleep 1
fi
open -a SwiftBar >/dev/null 2>&1 || true
sleep 1
open "swiftbar://refreshallplugins" >/dev/null 2>&1 || true

# 7. Done -------------------------------------------------------------------
echo
info "$APP_NAME is installed."
cat <<EOF

Plugin: $dest
Config: $config
Data:   $data_dir
EOF

if [ "$fresh_config" -eq 1 ]; then
  cat <<EOF

Opening the config now. Edit it to add more conferences or change data_dir.
EOF
  open -t "$config" >/dev/null 2>&1 || true
else
  echo
  echo "Edit the config any time from the menu: $APP_NAME -> Config -> Edit config."
fi
