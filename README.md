# CCFBar

English | [简体中文](README.zh-CN.md)

Your ddl-tracker for CCF conferences, now in your menu bar!

![preview](docs/preview.gif)

## Features

- ⏱️ Shows the next upcoming deadline in the menu bar
- 📋 Lists all future deadlines with countdown timers
- 🌎 Displays deadline times in both conference timezone and your local timezone
- 🔄 Automatically updates every hour
- 🛠️ Easy to manage your favorite conferences
- 🔗 Links to conference websites

![preview edit](docs/preview-edit.png)

## Install

### Quick install

```bash
curl -fsSL https://github.com/superpung/swiftbar-ccfddl/releases/latest/download/install.sh | bash
```

### Manual install

```bash
brew install --cask swiftbar
git clone https://github.com/superpung/swiftbar-ccfddl.git
cd swiftbar-ccfddl
chmod +x plugin/ccfbar.1h.py
python3 plugin/ccfbar.1h.py --init   # writes ~/.config/ccfbar/config.json
# then symlink it into your SwiftBar plugin folder and SwiftBar -> Refresh All:
ln -s "$(pwd)/plugin/ccfbar.1h.py" "$HOME/<your-SwiftBar-plugin-folder>/ccfbar.1h.py"
```

Then add conference YAML files to the configured `data_dir`, or run `bash install.sh` from the local checkout.

## Configuration

CCFBar reads configuration from:

```text
~/.config/ccfbar/config.json
```

Set `CCFBAR_CONFIG` to use a different config path. See [config.example.json](config.example.json).

```json
{
  "data_dir": "~/.config/ccfbar/conferences",
  "display": {
    "within_days": 365,
    "show_remaining_after_within_days": true
  },
  "sources": {
    "raw_base_url": "https://raw.githubusercontent.com/ccfddl/ccf-deadlines/refs/heads/main/conference",
    "conference_url": "https://github.com/ccfddl/ccf-deadlines/tree/main/conference"
  },
  "conferences": [
    "SE/icse.yml"
  ]
}
```

Important fields:

- `data_dir`: local directory containing ccfddl `.yml` / `.yaml` files
- `display.within_days`: show deadlines within this many days before grouping the rest under `More`
- `sources.raw_base_url`: base URL used by the menu's `Sync` action
- `conferences`: initial files the installer downloads when the data directory is empty

Add more conference files from [ccfddl/ccf-deadlines](https://github.com/ccfddl/ccf-deadlines/tree/main/conference), then refresh SwiftBar.

The `1h` in `ccfbar.1h.py` is SwiftBar's refresh interval. With the quick installer, set `CCFBAR_REFRESH=10m` to install as `ccfbar.10m.py`.

## Installer Options

- `CCFBAR_REFRESH`: installed plugin refresh interval, default `1h`
- `CCFBAR_PLUGIN_URL`: override plugin download URL for testing
- `CCFBAR_CONFIG`: config path, default `~/.config/ccfbar/config.json`
- `CCFBAR_DATA_DIR`: data directory override
- `CCFBAR_CONFERENCES`: space-separated initial conference files, such as `SE/icse.yml DB/sigmod.yml CV/cvpr.yml`

Example:

```bash
curl -fsSL https://github.com/superpung/swiftbar-ccfddl/releases/latest/download/install.sh \
  | CCFBAR_CONFERENCES="SE/icse.yml DB/sigmod.yml CV/cvpr.yml" bash
```

## Requirements

- macOS
- [SwiftBar](https://github.com/swiftbar/SwiftBar)
- `python3` from the standard macOS developer tools or newer

## Credits

- Data sourced from [CCF Deadlines](https://github.com/ccfddl/ccf-deadlines)
- Plugin built for [SwiftBar](https://github.com/swiftbar/SwiftBar)

## License

[MIT](./LICENSE) License © 2025 [Super Lee](https://github.com/superpung)
