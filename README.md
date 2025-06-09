# [CCF-Deadlines](https://github.com/ccfddl/ccf-deadlines) x [SwiftBar](https://github.com/swiftbar/SwiftBar)

Your ddl-tracker for CCF conferences, now in your menu bar!

![preview](docs/preview.gif)

## Features

- ⏱️ Shows the next upcoming deadline in the menu bar
- 📋 Lists all future deadlines with countdown timers
- 🌎 Displays deadline times in both conference timezone and your local timezone
- 🔄 Automatically updates every hour
- 🔗 Links to conference websites

## Installation

1. Install [SwiftBar](https://github.com/swiftbar/SwiftBar) and set `Plugin Folder` (e.g., `~/swiftbar/`)
2. Clone this repository to a different directory (e.g., `~/i/swiftbar-ccfddl/`) and install dependencies:

   ```bash
   mkdir -p ~/i/swiftbar-ccfddl/
   git clone https://github.com/superpung/swiftbar-ccfddl.git ~/i/swiftbar-ccfddl/
   cd ~/i/swiftbar-ccfddl/
   uv sync
   # if you don't have `uv` installed, use pip:
   pip install .
   ```

3. Create the assets directory and download CCF deadline YAML files from [ccfddl/ccf-deadlines](https://github.com/ccfddl/ccf-deadlines):

   ```bash
   mkdir -p ~/i/swiftbar-ccfddl/assets
   cd ~/i/swiftbar-ccfddl/assets
   wget https://raw.githubusercontent.com/ccfddl/ccf-deadlines/refs/heads/main/conference/SE/icse.yml
   # or download specific conference files as needed
   ```

4. Edit the [`ccfddl.1h.py`](ccfddl.1h.py) script to set the correct path for the python environment (use `which python3`) and CCF deadline YAML files assets:

   ```diff
   - #!/Users/super/i/swiftbar/.venv/bin/python3
   + #!/Users/yourname/i/swiftbar-ccfddl/.venv/bin/python3
   ...
   - CCFDDL_DIR = os.path.expanduser("~/i/swiftbar/assets/ccfddl")
   + CCFDDL_DIR = os.path.expanduser("~/i/swiftbar-ccfddl/assets")
   ```

5. Make the script executable and create a symbolic link to the script in your SwiftBar plugins directory:

   ```bash
   chmod +x ~/i/swiftbar-ccfddl/ccfddl.1h.py
   ln -s ~/i/swiftbar-ccfddl/ccfddl.1h.py ~/swiftbar/ccfddl.1h.py
   ```

6. Refresh SwiftBar to see the plugin in action!

## Configuration

You can change the filename of the script in the SwiftBar plugin directory to change the update frequency. For example, renaming it to `ccfddl.10m.py` will update every 10 minutes.

## Credits

- Data sourced from [CCF Deadlines](https://github.com/ccfddl/ccf-deadlines)
- Plugin built for [SwiftBar](https://github.com/swiftbar/SwiftBar)

## License

[MIT](./LICENSE) License © 2025 [Super Lee](https://github.com/superpung)
