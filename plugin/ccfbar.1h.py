#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# <xbar.title>CCFBar</xbar.title>
# <xbar.author>Super Lee</xbar.author>
# <xbar.author.github>superpung</xbar.author.github>
# <xbar.desc>Track CCF conference deadlines in the macOS menu bar.</xbar.desc>
# <xbar.dependencies>python3</xbar.dependencies>
# <xbar.abouturl>https://github.com/superpung/swiftbar-ccfddl</xbar.abouturl>
#
# <swiftbar.hideAbout>true</swiftbar.hideAbout>
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.hideLastUpdated>false</swiftbar.hideLastUpdated>
# <swiftbar.hideDisablePlugin>true</swiftbar.hideDisablePlugin>
# <swiftbar.hideSwiftBar>true</swiftbar.hideSwiftBar>
# <swiftbar.refreshEvery>1h</swiftbar.refreshEvery>
# <swiftbar.title>CCFBar</swiftbar.title>
# <swiftbar.environment>[CCFBAR_CONFIG=]</swiftbar.environment>

import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

APP_NAME = "CCFBar"
REPO_URL = "https://github.com/superpung/swiftbar-ccfddl"
CCF_DEADLINES_RAW_BASE_URL = "https://raw.githubusercontent.com/ccfddl/ccf-deadlines/refs/heads/main/conference"
CCF_DEADLINES_CONFERENCE_URL = "https://github.com/ccfddl/ccf-deadlines/tree/main/conference"
CCF_DEADLINES_WEB_URL = "https://ccfddl.com"

DEADLINE_TYPES = (
    ("deadline", "Submission Deadline"),
    ("abstract_deadline", "Abstract Deadline"),
)
DATETIME_FORMATS = ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M")
UTC_OFFSET_RE = re.compile(r"^UTC(?:([+-])(\d{1,2})(?::?(\d{2}))?)?$")
KEY_RE = re.compile(r"^[A-Za-z0-9_-]+$")


def xdg_config_home():
    """Return the base config directory."""
    return Path(os.environ.get("XDG_CONFIG_HOME") or "~/.config").expanduser()


def default_data_dir():
    """Return the default conference YAML directory."""
    return xdg_config_home() / "ccfbar" / "conferences"


def config_path():
    """Resolve the config path from env or the default ccfbar location."""
    env_path = os.environ.get("CCFBAR_CONFIG", "").strip()
    if env_path:
        return Path(env_path).expanduser()
    return xdg_config_home() / "ccfbar" / "config.json"


def expand_config_path(value):
    """Expand ~ and environment variables in a config path value."""
    return Path(os.path.expandvars(os.path.expanduser(str(value))))


EXAMPLE_CONFIG = {
    "data_dir": "~/.config/ccfbar/conferences",
    "display": {
        "within_days": 365,
        "show_remaining_after_within_days": True,
    },
    "sources": {
        "raw_base_url": CCF_DEADLINES_RAW_BASE_URL,
        "conference_url": CCF_DEADLINES_CONFERENCE_URL,
    },
    "conferences": [
        "SE/icse.yml",
    ],
}


def write_example_config():
    """Create an example config if absent; return the path."""
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        with path.open("w", encoding="utf-8") as handle:
            json.dump(EXAMPLE_CONFIG, handle, indent=2)
            handle.write("\n")
        os.chmod(path, 0o600)
    return path


def load_config():
    """Load config; return (config_dict_or_None, error_string_or_None)."""
    path = config_path()
    if not path.exists():
        return None, "missing"
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle), None
    except json.JSONDecodeError as exc:
        return None, f"Invalid JSON in config: {exc}"
    except OSError as exc:
        return None, f"Cannot read config: {exc}"


def display_config(config):
    """Return display settings with defaults applied."""
    display = dict(EXAMPLE_CONFIG["display"])
    display.update(config.get("display") or {})
    return display


def source_config(config):
    """Return source URL settings with defaults applied."""
    sources = dict(EXAMPLE_CONFIG["sources"])
    sources.update(config.get("sources") or {})
    return sources


def configured_data_dir(config):
    """Resolve the conference YAML directory from env, config, or default."""
    env_dir = os.environ.get("CCFBAR_DATA_DIR")
    if env_dir:
        return expand_config_path(env_dir)
    return expand_config_path(config.get("data_dir") or default_data_dir())


def swiftbar_escape(value):
    """Escape a value for a single SwiftBar parameter."""
    return str(value).replace("'", "'\"'\"'")


def print_config_actions(data_dir=None):
    """Render common config/data menu actions."""
    path = config_path()
    print("Config")
    print(f"-- Edit config | terminal=false bash='open' param1='-t' param2='{swiftbar_escape(path)}'")
    print(f"-- Config folder | terminal=false bash='open' param1='{swiftbar_escape(path.parent)}'")
    if data_dir is not None:
        print(f"-- Data directory | terminal=false bash='open' param1='{swiftbar_escape(data_dir)}'")
    print(f"-- Project homepage | href={REPO_URL}")


def render_no_config(error):
    """Render setup help when the config is missing or invalid."""
    print(f"{APP_NAME} | color=gray")
    print("---")
    path = config_path()
    if error == "missing":
        print("No config found | color=orange")
        print(f"Expected at: {path} | color=lightgray size=12")
        plugin = os.environ.get("SWIFTBAR_PLUGIN_PATH", "")
        if plugin:
            print(
                f"Create example config | terminal=false refresh=true bash='{swiftbar_escape(plugin)}' param1='--init'"
            )
    else:
        print("Config error | color=red")
        print(f"{error} | color=lightgray size=12")
    print(f"Open config folder | terminal=false bash='open' param1='{swiftbar_escape(path.parent)}'")
    print(f"Documentation | href={REPO_URL}")


def render_missing_data_dir(data_dir, config):
    """Render setup help when config exists but data_dir is absent."""
    print(f"{APP_NAME} | color=gray")
    print("---")
    print("Conference data directory not found | color=red")
    print(f"{data_dir} | color=lightgray size=12")
    print("Run install.sh or add CCF deadline YAML files to the data directory.")
    print("---")
    print_config_actions(data_dir)
    print(f"More conferences | href={source_config(config)['conference_url']}")


def strip_inline_comment(line):
    """Remove YAML comments while preserving # inside quoted strings."""
    in_single = False
    in_double = False
    index = 0

    while index < len(line):
        char = line[index]
        if char == "'" and not in_double:
            if in_single and index + 1 < len(line) and line[index + 1] == "'":
                index += 2
                continue
            in_single = not in_single
        elif char == '"' and not in_single:
            escaped = index > 0 and line[index - 1] == "\\"
            if not escaped:
                in_double = not in_double
        elif char == "#" and not in_single and not in_double:
            if index == 0 or line[index - 1].isspace():
                return line[:index].rstrip()
        index += 1

    return line.rstrip()


def unescape_double_quoted(value):
    """Decode the small YAML double-quote escape set used by ccfddl files."""
    escapes = {
        "0": "\0",
        "a": "\a",
        "b": "\b",
        "t": "\t",
        "\t": "\t",
        "n": "\n",
        "v": "\v",
        "f": "\f",
        "r": "\r",
        "e": "\x1b",
        '"': '"',
        "/": "/",
        "\\": "\\",
        " ": " ",
    }
    result = []
    index = 0

    while index < len(value):
        char = value[index]
        if char != "\\" or index + 1 >= len(value):
            result.append(char)
            index += 1
            continue

        escaped = value[index + 1]
        if escaped == "x" and index + 3 < len(value):
            result.append(chr(int(value[index + 2 : index + 4], 16)))
            index += 4
        elif escaped == "u" and index + 5 < len(value):
            result.append(chr(int(value[index + 2 : index + 6], 16)))
            index += 6
        elif escaped == "U" and index + 9 < len(value):
            result.append(chr(int(value[index + 2 : index + 10], 16)))
            index += 10
        else:
            result.append(escapes.get(escaped, escaped))
            index += 2

    return "".join(result)


def parse_scalar(value):
    """Parse the scalar value subset used in ccfddl YAML files."""
    value = value.strip()
    if value == "":
        return None

    if value[0] == "'" and value[-1:] == "'":
        return value[1:-1].replace("''", "'")
    if value[0] == '"' and value[-1:] == '"':
        return unescape_double_quoted(value[1:-1])

    lower_value = value.lower()
    if lower_value in {"null", "~"}:
        return None
    if lower_value == "true":
        return True
    if lower_value == "false":
        return False
    if re.fullmatch(r"[+-]?\d+", value):
        return int(value)

    return value


def split_key_value(text):
    """Split a simple YAML key/value pair."""
    key, separator, value = text.partition(":")
    key = key.strip()
    if not separator or not KEY_RE.fullmatch(key):
        return None, None
    return key, parse_scalar(value)


def parse_ccfddl_yaml(content):
    """Parse the ccfddl conference YAML structure without third-party packages."""
    conferences = []
    current_group = None
    current_group_indent = None
    current_conf = None
    current_conf_indent = None
    current_event = None
    current_event_indent = None
    in_timeline = False

    for raw_line in content.splitlines():
        line = strip_inline_comment(raw_line)
        if not line.strip():
            continue

        indent = len(line) - len(line.lstrip(" "))
        text = line.strip()

        if text.startswith("- "):
            key, value = split_key_value(text[2:].strip())

            if indent == 0:
                current_group = {"confs": []}
                current_group_indent = indent
                current_conf = None
                current_conf_indent = None
                current_event = None
                current_event_indent = None
                in_timeline = False
                conferences.append(current_group)
                if key:
                    current_group[key] = value
                continue

            if current_group is None:
                continue

            if key == "year":
                current_conf = {"timeline": [], "year": value}
                current_conf_indent = indent
                current_event = None
                current_event_indent = None
                in_timeline = False
                current_group.setdefault("confs", []).append(current_conf)
                continue

            if current_conf is not None and in_timeline:
                current_event = {}
                current_event_indent = indent
                current_conf.setdefault("timeline", []).append(current_event)
                if key:
                    current_event[key] = value
                continue

            continue

        key, value = split_key_value(text)
        if key is None or current_group is None:
            continue

        if current_conf is not None and current_conf_indent is not None:
            if current_event is not None and current_event_indent is not None and indent > current_event_indent:
                current_event[key] = value
                continue

            if indent > current_conf_indent:
                if key == "timeline":
                    current_conf.setdefault("timeline", [])
                    current_event = None
                    current_event_indent = None
                    in_timeline = True
                elif value is not None:
                    current_conf[key] = value
                continue

        if current_group_indent is not None and indent > current_group_indent:
            if key == "confs":
                current_group.setdefault("confs", [])
            elif value is not None:
                current_group[key] = value

    return conferences


def parse_yaml_file(file_path):
    """Parse a local ccfddl YAML file."""
    try:
        content = file_path.read_text(encoding="utf-8")
    except OSError:
        return []
    return parse_ccfddl_yaml(content)


def get_timezone(timezone_str):
    """Return a tzinfo object for ccfddl timezone strings."""
    if not timezone_str:
        return timezone.utc

    timezone_str = str(timezone_str).strip()
    if timezone_str == "AoE":
        return timezone(timedelta(hours=-12), "AoE")

    match = UTC_OFFSET_RE.fullmatch(timezone_str)
    if match:
        sign, hours, minutes = match.groups()
        if sign is None:
            return timezone.utc
        offset = timedelta(hours=int(hours), minutes=int(minutes or 0))
        if sign == "-":
            offset = -offset
        return timezone(offset, timezone_str)

    try:
        return ZoneInfo(timezone_str)
    except ZoneInfoNotFoundError:
        return timezone.utc


def parse_deadline_datetime(deadline_str, timezone_str):
    """Parse a deadline string and convert it to UTC."""
    if not isinstance(deadline_str, str):
        return None, None

    for date_format in DATETIME_FORMATS:
        try:
            deadline_dt = datetime.strptime(deadline_str, date_format)
            break
        except ValueError:
            deadline_dt = None

    if deadline_dt is None:
        return None, None

    original_deadline = deadline_dt.replace(tzinfo=get_timezone(timezone_str))
    return original_deadline, original_deadline.astimezone(timezone.utc)


def get_future_deadlines(data):
    """Process ccfddl data to find future deadlines."""
    now = datetime.now(timezone.utc)
    future_deadlines = []

    for group in data:
        title = group.get("title", "Unknown")
        for conf in group.get("confs", []):
            year = conf.get("year")
            conf_id = conf.get("id")

            for event in conf.get("timeline", []):
                timezone_str = event.get("timezone") or conf.get("timezone", "UTC")

                for deadline_field, deadline_type in DEADLINE_TYPES:
                    deadline_str = event.get(deadline_field)
                    if deadline_str is None:
                        continue

                    original_deadline, deadline_utc = parse_deadline_datetime(deadline_str, timezone_str)
                    if deadline_utc is None or deadline_utc <= now:
                        continue

                    future_deadlines.append(
                        {
                            "deadline": deadline_utc,
                            "original_deadline": original_deadline,
                            "deadline_type": deadline_type,
                            "comment": event.get("comment"),
                            "conf_id": conf_id,
                            "title": title,
                            "year": year,
                            "timezone": timezone_str,
                            "link": conf.get("link"),
                        }
                    )

    return future_deadlines


def format_time_remaining(deadline_utc):
    """Calculate the time remaining until the deadline."""
    total_seconds = max(0, int((deadline_utc - datetime.now(timezone.utc)).total_seconds()))
    days, remainder = divmod(total_seconds, 24 * 60 * 60)
    hours, remainder = divmod(remainder, 60 * 60)
    minutes, _ = divmod(remainder, 60)

    if days > 0:
        return f"{days}d {hours}h"
    return f"{hours}h {minutes}m"


def display_deadline_info(deadline, level=0):
    """Display deadline information in SwiftBar menu format."""
    time_remaining = format_time_remaining(deadline["deadline"])
    local_timezone = datetime.now().astimezone().tzinfo
    deadline_local_sys = deadline["deadline"].astimezone(local_timezone).strftime("%Y-%m-%d %H:%M")
    deadline_local = deadline["original_deadline"].strftime("%Y-%m-%d %H:%M")
    timezone_str = deadline["timezone"]
    comment = deadline["comment"]
    conf_id = deadline["conf_id"]
    deadline_type = deadline["deadline_type"]
    link = deadline["link"]
    title = deadline["title"]
    year = deadline["year"]

    indent = "--" * level
    print(f"{indent}{conf_id}: {time_remaining}")
    print(f"{indent}-- {title} {year} | href={link}")
    if comment:
        print(f"{indent}-- {comment} | color=lightgray size=12")
    print(f"{indent}-- {deadline_type} | color=lightgray size=12")
    print(f"{indent}-- {deadline_local} {timezone_str} | color=lightgray size=12")
    print(f"{indent}-- {deadline_local_sys} {local_timezone} | color=lightgray size=12")


def collect_conferences(data_dir):
    """Read local conference YAML files and return grouped files plus future deadlines."""
    confs = {}
    future_deadlines = []

    for yaml_file in sorted(data_dir.iterdir()):
        if yaml_file.suffix not in {".yml", ".yaml"}:
            continue

        data = parse_yaml_file(yaml_file)
        if not data:
            continue

        conf_type = data[0].get("sub") or "other"
        confs.setdefault(str(conf_type), []).append(yaml_file.name)
        future_deadlines.extend(get_future_deadlines(data))

    future_deadlines.sort(key=lambda item: item["deadline"])
    return confs, future_deadlines


def render_edit_menu(confs, data_dir, sources):
    """Render the conference management section."""
    print("Edit")
    for conf_type, conf_files in confs.items():
        print(f"-- {conf_type.upper()} | color=lightgray")
        for conf_file in conf_files:
            local_file = data_dir / conf_file
            remote_file = f"{sources['raw_base_url'].rstrip('/')}/{conf_type}/{conf_file}"
            print(f"-- {conf_file}")
            print(
                f"---- Sync | terminal=false refresh=true bash='curl' param1='-fsSL' param2='{remote_file}' param3='-o' param4='{swiftbar_escape(local_file)}'"
            )
            print(
                f"---- Remove | color=red terminal=false refresh=true bash='mv' param1='{swiftbar_escape(local_file)}' param2='{swiftbar_escape(local_file)}.deleted'"
            )
        print("-----")
    print(f"-- More... | href={sources['conference_url']}")


def render_footer(config, data_dir, confs):
    """Render common footer actions."""
    print("---")
    if confs:
        render_edit_menu(confs, data_dir, source_config(config))
        print("---")
    print_config_actions(data_dir)
    print("Open")
    print("-- LINKS | color=lightgray")
    print(f"-- CCF Deadlines | href={CCF_DEADLINES_WEB_URL}")
    print(f"-- CCFBar Homepage | href={REPO_URL}")


def render_plugin(config):
    """Render the SwiftBar plugin menu."""
    data_dir = configured_data_dir(config)
    if not data_dir.is_dir():
        render_missing_data_dir(data_dir, config)
        return

    confs, future_deadlines = collect_conferences(data_dir)
    if not future_deadlines:
        print("No upcoming deadlines | color=gray")
        render_footer(config, data_dir, confs)
        return

    next_deadline = future_deadlines[0]
    time_remaining = format_time_remaining(next_deadline["deadline"])
    print(f"{next_deadline['title']}: {time_remaining} | color=white")

    print("---")

    display = display_config(config)
    within_days = int(display.get("within_days", 365) or 365)
    display_until = datetime.now(timezone.utc) + timedelta(days=within_days)
    future_display_deadlines = [deadline for deadline in future_deadlines if deadline["deadline"] <= display_until]
    if not future_display_deadlines and display.get("show_remaining_after_within_days", True):
        future_display_deadlines = future_deadlines

    for deadline in future_display_deadlines:
        display_deadline_info(deadline)

    future_remaining_deadlines = [deadline for deadline in future_deadlines if deadline not in future_display_deadlines]
    if future_remaining_deadlines:
        print("---")
        print("More")
        for deadline in future_remaining_deadlines:
            display_deadline_info(deadline, level=1)

    render_footer(config, data_dir, confs)


def main(argv):
    """Entry point."""
    if "--init" in argv:
        path = write_example_config()
        print(f"Wrote example config to {path}")
        return 0

    config, error = load_config()
    if config is None:
        render_no_config(error)
        return 0

    try:
        render_plugin(config)
    except Exception as exc:  # pylint: disable=broad-exception-caught
        print(f"{APP_NAME} | color=red")
        print("---")
        print("Plugin error | color=red")
        print(f"{exc} | color=lightgray size=12")
        print("Refresh | refresh=true")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
