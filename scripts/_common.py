#!/usr/bin/env python3
"""Shared boilerplate for this plugin's validation scripts (check_adrplus_compat.py,
validate_plugin.py) - both accumulate a list of error strings and report them the same way at the
end, so this is the one place that format lives instead of two copies that could drift apart.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def report(errors, label, success_message):
    """Prints accumulated `errors` (if any) under `label`, or `success_message` if there are
    none. Returns the process exit code a script's `main()` should return (1 if there were
    errors, 0 otherwise) - callers should `return report(errors, ...)` directly.
    """
    if errors:
        print(f"{label} FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(success_message)
    return 0
