#!/usr/bin/env python3
"""Smoke-test the installed `adrplus` CLI against the command/flag table documented
in skills/manage-adrs/SKILL.md. Run non-interactively, exactly like Claude would via
the Bash tool - this is what actually catches console-crash regressions (see
CHANGELOG entries around v1.0.0-beta1) and documentation drift (renamed/removed flags).
"""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_MD = ROOT / "skills" / "manage-adrs" / "SKILL.md"

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


def parse_command_table():
    text = SKILL_MD.read_text(encoding="utf-8")
    rows = re.findall(r"^\|\s*`adrplus ([^`]+)`\s*\|\s*(.*?)\s*\|.*\|$", text, re.MULTILINE)
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

    commands = parse_command_table()
    if not commands:
        errors.append(f"no commands parsed from {SKILL_MD.relative_to(ROOT)} - table format may have changed")

    for command, flags in sorted(commands.items()):
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
                    f"adrplus help {command}: SKILL.md documents --{flag} but it's missing from --help output"
                )

    if errors:
        print("adrplus compatibility check FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"adrplus compatibility check OK: {len(commands)} commands verified against SKILL.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
