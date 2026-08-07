#!/usr/bin/env python3
"""Smoke-test the installed `adrplus` CLI against the command/flag table documented
in skills/manage-adrs/SKILL.md (and its copilot/ mirror). Run non-interactively,
exactly like Claude/Copilot would via their shell tool - this is what actually
catches console-crash regressions (see CHANGELOG entries around v1.0.0-beta1) and
documentation drift (renamed/removed flags), in *both* copies of the command table.
"""

import itertools
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import ROOT, report  # noqa: E402

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

# The specific regression class this script exists to catch (see beta1/beta2 notes in the
# skill/README): only a beta-numbered adrplus below this is known to crash/hang non-interactively.
# This is a narrow, adrplus-specific heuristic, not a general SemVer comparator - it doesn't
# attempt to order beta vs. rc vs. stable, only "is this a beta build below the documented floor".
MIN_ADRPLUS_BETA = 3

errors = []


def run(args):
    """Runs `adrplus <args>`, or returns None (after recording why) if it couldn't be run at all -
    a missing executable or a hang are themselves findings this script needs to report, not
    something that should crash the checker with a raw traceback."""
    try:
        return subprocess.run(
            ["adrplus", *args],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except FileNotFoundError:
        errors.append(f"'adrplus {' '.join(args)}' failed: adrplus executable not found on PATH - is it installed? (dotnet tool install -g adrplus)")
        return None
    except subprocess.TimeoutExpired:
        errors.append(
            f"'adrplus {' '.join(args)}' timed out after 30s - likely hung waiting for interactive "
            f"input (a non-interactive-flag regression, exactly what this script exists to catch)"
        )
        return None


def check_no_crash(label, result):
    """Returns False (and records why) if `result` is missing (run() already failed) or hit a
    known crash marker; True only when the command actually ran and produced clean output."""
    if result is None:
        return False
    combined = result.stdout + result.stderr
    for marker in CRASH_MARKERS:
        if marker in combined:
            errors.append(f"{label}: hit a known crash marker ({marker!r}) - output:\n{combined}")
            return False
    return True


def check_minimum_version(version_output):
    """Flags an installed adrplus below the documented minimum (beta3) - a narrow, adrplus-
    specific heuristic (see MIN_ADRPLUS_BETA), not a general version comparator. Silently does
    nothing for a stable/rc build or a beta at/above the floor, exactly like the plugin's own
    docs describe "beta3 or later, including any 1.x release" as sufficient."""
    m = re.search(r"beta(\d+)", version_output, re.IGNORECASE)
    if m and int(m.group(1)) < MIN_ADRPLUS_BETA:
        errors.append(
            f"installed adrplus version ({version_output.strip()!r}) is a beta below the documented "
            f"minimum (beta{MIN_ADRPLUS_BETA}) - README.md and both SKILL.md files promise support "
            f"from beta{MIN_ADRPLUS_BETA} onward, but this CI job otherwise only ever installs the "
            f"newest 1.x release, so a regression specific to the beta1/beta2 era would never be "
            f"caught here."
        )


def parse_command_table(skill_md):
    text = skill_md.read_text(encoding="utf-8")
    # Leading/trailing `|` on the row are optional (both patterns are valid GFM) - requiring them
    # made a reformatted-without-outer-pipes row silently vanish from `commands` with no error.
    # `[^|\n]*` (not `\s*`) between the closing backtick and the next `|` tolerates rows like
    # "`adrplus plugins` (v1.0.0-beta6+) | ..." - without it, any row with a version-suffix
    # annotation silently fails to match and its command is never checked.
    rows = re.findall(r"^\|?[ \t]*`adrplus ([^`]+)`[^|\n]*\|[ \t]*(.*?)[ \t]*\|", text, re.MULTILINE)
    commands = {}
    for command_cell, flags_cell in rows:
        tokens = command_cell.split()
        if not tokens:
            errors.append(
                f"{skill_md.relative_to(ROOT)}: found a `adrplus ...` table row with an empty "
                f"command cell - check for a formatting mistake near that row"
            )
            continue
        base = tokens[0]
        # `config` has no behavior of its own - its mode selector
        # (--application/--repository/--template/--migrate) is what actually picks which file it
        # edits, so track each selector as its own key instead of collapsing all four rows into
        # one "config" bucket, which hid drift in exactly this column (the selector itself).
        if base == "config" and len(tokens) > 1 and tokens[1].startswith("--"):
            base = f"config {tokens[1]}"
        if base in SKIP_COMMANDS:
            continue
        flags = re.findall(r"--([a-zA-Z0-9-]+)", flags_cell)
        commands.setdefault(base, set()).update(flags)
    return commands


def describe_drift(first, second, first_commands, second_commands):
    only_first = {c: f - second_commands.get(c, set()) for c, f in first_commands.items()}
    only_first = {c: f for c, f in only_first.items() if f}
    only_second = {c: f - first_commands.get(c, set()) for c, f in second_commands.items()}
    only_second = {c: f for c, f in only_second.items() if f}
    missing_in_second = set(first_commands) - set(second_commands)
    missing_in_first = set(second_commands) - set(first_commands)
    return (
        f"{first} and {second} command tables have drifted apart: "
        f"commands only in {first}={missing_in_second or 'none'}, "
        f"only in {second}={missing_in_first or 'none'}, "
        f"flags only in {first}'s shared commands={only_first or 'none'}, "
        f"flags only in {second}'s shared commands={only_second or 'none'}"
    )


def main():
    version_result = run(["--version"])
    if version_result is not None:
        crash_free = check_no_crash("adrplus --version", version_result)
        if version_result.returncode != 0:
            errors.append(f"adrplus --version exited {version_result.returncode}")
        elif crash_free:
            # Only meaningful once we know the process actually ran cleanly - a returncode!=0 or a
            # crash marker is already its own, more specific finding above; don't also evaluate a
            # possibly-garbled version string as "too old" on top of that.
            check_minimum_version(version_result.stdout)

    per_file_commands = {}
    for skill_md in SKILL_MD_PATHS:
        label = skill_md.relative_to(ROOT)
        commands = parse_command_table(skill_md)
        if not commands:
            errors.append(f"no commands parsed from {label} - table format may have changed")
        per_file_commands[label] = commands

    # Catch any two of the command tables silently drifting apart from each other, independent of
    # whether either one still matches the installed CLI. Compares every pair, not just "the
    # first two" - SKILL_MD_PATHS growing to 3+ entries silently stopped this check entirely.
    labels = list(per_file_commands)
    for first, second in itertools.combinations(labels, 2):
        if not per_file_commands[first] or not per_file_commands[second]:
            continue
        if per_file_commands[first] != per_file_commands[second]:
            errors.append(describe_drift(first, second, per_file_commands[first], per_file_commands[second]))

    all_commands = {}
    for commands in per_file_commands.values():
        for command, flags in commands.items():
            all_commands.setdefault(command, set()).update(flags)

    for command, flags in sorted(all_commands.items()):
        # `command` may be a compound key like "config --application" (see parse_command_table) -
        # split it into separate argv entries rather than passing it as one literal token.
        result = run(["help", *command.split()])
        if not check_no_crash(f"adrplus help {command}", result):
            continue
        if result.returncode != 0:
            errors.append(f"adrplus help {command} exited {result.returncode}")
            continue
        help_text = result.stdout
        for flag in sorted(flags):
            # Word-boundary match, not substring - `--file` is a substring of `--filename`, so a
            # flag renamed to something containing the old name would otherwise false-pass.
            if not re.search(rf"--{re.escape(flag)}\b", help_text):
                errors.append(
                    f"adrplus help {command}: documented --{flag} but it's missing from --help output"
                )

    return report(
        errors,
        "adrplus compatibility check",
        f"adrplus compatibility check OK: {len(all_commands)} commands verified across {len(SKILL_MD_PATHS)} SKILL.md files.",
    )


if __name__ == "__main__":
    sys.exit(main())
