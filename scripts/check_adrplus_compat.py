#!/usr/bin/env python3
"""Smoke-test the installed `adrplus` CLI against the command/flag table documented
in skills/manage-adrs/SKILL.md (and its copilot/ mirror). Run non-interactively,
exactly like Claude/Copilot would via their shell tool - this is what actually
catches console-crash regressions (see CHANGELOG entries around v1.0.0-beta1) and
documentation drift (renamed/removed flags), in *both* copies of the command table.
"""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_MD_PATHS = [
    ROOT / "skills" / "manage-adrs" / "SKILL.md",
    ROOT / "copilot" / "skills" / "manage-adrs" / "SKILL.md",
]

# These appear in the table but aren't real subcommands to probe with `adrplus help <cmd>`.
SKIP_COMMANDS = {"--version", "help"}

CRASH_MARKERS = (
    "The handle is invalid",
    "Critical error occurred",
    "requires a terminal",
    "ConsoleColor enum",
)

errors = []


def run(args):
    return subprocess.run(
        ["adrplus", *args],
        capture_output=True,
        text=True,
        timeout=30,
    )


def check_no_crash(label, result):
    combined = result.stdout + result.stderr
    for marker in CRASH_MARKERS:
        if marker in combined:
            errors.append(f"{label}: hit a known crash marker ({marker!r}) - output:\n{combined}")
            return False
    return True


def parse_command_table(skill_md):
    text = skill_md.read_text(encoding="utf-8")
    # `[^|]*` (not `\s*`) between the closing backtick and the next `|` tolerates rows like
    # "`adrplus plugins` (v1.0.0-beta6+) | ..." - without it, any row with a version-suffix
    # annotation silently fails to match and its command is never checked.
    rows = re.findall(r"^\|\s*`adrplus ([^`]+)`[^|]*\|\s*(.*?)\s*\|.*\|$", text, re.MULTILINE)
    commands = {}
    for command_cell, flags_cell in rows:
        base = command_cell.split()[0]
        if base in SKIP_COMMANDS:
            continue
        flags = re.findall(r"--([a-zA-Z-]+)", flags_cell)
        commands.setdefault(base, set()).update(flags)
    return commands


def main():
    version_result = run(["--version"])
    if version_result.returncode != 0 or not check_no_crash("adrplus --version", version_result):
        errors.append(f"adrplus --version exited {version_result.returncode}")

    per_file_commands = {}
    for skill_md in SKILL_MD_PATHS:
        label = skill_md.relative_to(ROOT)
        commands = parse_command_table(skill_md)
        if not commands:
            errors.append(f"no commands parsed from {label} - table format may have changed")
        per_file_commands[label] = commands

    # Catch the two copies of the command table silently drifting apart from each other,
    # independent of whether either one still matches the installed CLI.
    labels = list(per_file_commands)
    if len(labels) == 2 and per_file_commands[labels[0]] and per_file_commands[labels[1]]:
        first, second = labels
        if per_file_commands[first] != per_file_commands[second]:
            only_first = {c: f - per_file_commands[second].get(c, set()) for c, f in per_file_commands[first].items()}
            only_first = {c: f for c, f in only_first.items() if f}
            only_second = {c: f - per_file_commands[first].get(c, set()) for c, f in per_file_commands[second].items()}
            only_second = {c: f for c, f in only_second.items() if f}
            missing_in_second = set(per_file_commands[first]) - set(per_file_commands[second])
            missing_in_first = set(per_file_commands[second]) - set(per_file_commands[first])
            message = (
                f"{first} and {second} command tables have drifted apart: "
                f"commands only in {first}={missing_in_second or 'none'}, "
                f"only in {second}={missing_in_first or 'none'}, "
                f"flags only in {first}'s shared commands={only_first or 'none'}, "
                f"flags only in {second}'s shared commands={only_second or 'none'}"
            )
            errors.append(message)

    all_commands = {}
    for commands in per_file_commands.values():
        for command, flags in commands.items():
            all_commands.setdefault(command, set()).update(flags)

    for command, flags in sorted(all_commands.items()):
        result = run(["help", command])
        if not check_no_crash(f"adrplus help {command}", result):
            continue
        if result.returncode != 0:
            errors.append(f"adrplus help {command} exited {result.returncode}")
            continue
        help_text = result.stdout
        for flag in sorted(flags):
            if f"--{flag}" not in help_text:
                errors.append(
                    f"adrplus help {command}: documented --{flag} but it's missing from --help output"
                )

    if errors:
        print("adrplus compatibility check FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"adrplus compatibility check OK: {len(all_commands)} commands verified across {len(SKILL_MD_PATHS)} SKILL.md files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
