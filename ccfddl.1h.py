#!/Users/super/i/swiftbar/.venv/bin/python3
# <swiftbar.hideAbout>true</swiftbar.hideAbout>
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.hideLastUpdated>false</swiftbar.hideLastUpdated>
# <swiftbar.hideDisablePlugin>true</swiftbar.hideDisablePlugin>
# <swiftbar.hideSwiftBar>true</swiftbar.hideSwiftBar>
# <swiftbar.refreshEvery>1h</swiftbar.refreshEvery>
# <swiftbar.title>CCF Deadlines</swiftbar.title>

import os
from datetime import datetime

import pytz
import yaml

CCFDDL_DIR = os.path.expanduser("~/i/swiftbar/assets/ccfddl")


def parse_yaml_file(file_path):
    """parse the YAML file and return the data"""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
            return data
    except (FileNotFoundError, PermissionError, yaml.YAMLError):
        return None


def get_future_deadlines(data):
    """process the YAML data to find future deadlines"""
    now = datetime.now(pytz.utc)
    future_deadlines = []

    title = data[0]["title"]
    for conf in data[0]["confs"]:
        year = conf.get("year")
        conf_id = conf.get("id")
        timezone_str = conf.get("timezone", "UTC")

        try:
            if timezone_str == "AoE":
                timezone = pytz.timezone("Etc/GMT+12")
            elif timezone_str.startswith("UTC"):
                offset_str = timezone_str[3:]
                if offset_str:
                    offset = int(offset_str)
                    tz_name = f"Etc/GMT{'-' if offset > 0 else '+'}{abs(offset)}"
                    timezone = pytz.timezone(tz_name)
                else:
                    timezone = pytz.utc
            else:
                timezone = pytz.timezone(timezone_str)
        except (ValueError, pytz.exceptions.UnknownTimeZoneError):
            timezone = pytz.utc

        for event in conf.get("timeline", []):
            for deadline_type in ["deadline", "abstract_deadline"]:
                if deadline_type in event:
                    deadline_str = event[deadline_type]
                    comment = event.get("comment")
                    deadline_type_str = (
                        "Abstract Deadline" if deadline_type == "abstract_deadline" else "Submission Deadline"
                    )

                    try:
                        deadline_dt = datetime.strptime(deadline_str, "%Y-%m-%d %H:%M:%S")
                        deadline_dt = timezone.localize(deadline_dt)
                        deadline_utc = deadline_dt.astimezone(pytz.utc)

                        if deadline_utc > now:
                            future_deadlines.append(
                                {
                                    "deadline": deadline_utc,
                                    "original_deadline": deadline_dt,
                                    "deadline_type": deadline_type_str,
                                    "comment": comment,
                                    "conf_id": conf_id,
                                    "title": title,
                                    "year": year,
                                    "timezone": timezone_str,
                                    "link": conf.get("link"),
                                }
                            )
                    except (ValueError, TypeError, pytz.exceptions.Error):
                        continue

    return future_deadlines


def format_time_remaining(deadline_utc):
    """calculate the time remaining until the deadline"""
    now = datetime.now(pytz.utc)
    time_diff = deadline_utc - now

    days = time_diff.days
    hours, remainder = divmod(time_diff.seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    total_hours = days * 24 + hours

    if total_hours > 24:
        return f"{days}d {hours}h"
    else:
        return f"{total_hours}h {minutes}m"


def main():
    """main function to run the script"""
    if not os.path.exists(CCFDDL_DIR):
        print("❌ Error | color=red")
        print("---")
        print(f"CCFDDL directory not found: {CCFDDL_DIR}")
        return

    future_deadlines = []
    for yaml_file in os.listdir(CCFDDL_DIR):
        if not yaml_file.endswith(".yml") and not yaml_file.endswith(".yaml"):
            continue
        yaml_path = os.path.join(CCFDDL_DIR, yaml_file)
        data = parse_yaml_file(yaml_path)
        if data is None:
            continue
        future_deadlines.extend(get_future_deadlines(data))
    future_deadlines.sort(key=lambda x: x["deadline"])

    if not future_deadlines:
        print("No upcoming deadlines | color=gray")
        return

    next_deadline = future_deadlines[0]
    time_remaining = format_time_remaining(next_deadline["deadline"])
    print(f"{next_deadline['title']}: {time_remaining} | color=white")

    print("---")

    for deadline in future_deadlines:
        time_remaining = format_time_remaining(deadline["deadline"])
        local_timezone = datetime.now().astimezone().tzinfo
        deadline_local_sys = deadline["deadline"].astimezone(local_timezone).strftime("%Y-%m-%d %H:%M")
        deadline_local = deadline["original_deadline"].strftime("%Y-%m-%d %H:%M")
        timezone = deadline["timezone"]
        comment = deadline["comment"]
        conf_id = deadline["conf_id"]
        deadline_type = deadline["deadline_type"]
        link = deadline["link"]
        title = deadline["title"]
        year = deadline["year"]

        print(f"{conf_id}: {time_remaining} | color=white")
        print(f"-- {title} {year} | href={link}")
        if comment:
            print(f"-- {comment} | color=lightgray size=12")
        print(f"-- {deadline_type} | color=lightgray size=12")
        print(f"-- {deadline_local} {timezone} | color=lightgray size=12")
        print(f"-- {deadline_local_sys} {local_timezone} | color=lightgray size=12")

    print("---")

    print("Links")
    print("-- CCF Deadlines | href=https://ccfddl.com")
    print("-- Plugin Homepage | href=https://github.com/superpung/swiftbar-ccfddl")


if __name__ == "__main__":
    main()
