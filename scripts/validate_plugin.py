#!/usr/bin/env python3
"""Validate the plugin manifests and skill/agent frontmatter without external dependencies."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
errors = []


def check(condition, message):
    if not condition:
        errors.append(message)


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing file: {path.relative_to(ROOT)}")
        return None
    except json.JSONDecodeError as e:
        errors.append(f"invalid JSON in {path.relative_to(ROOT)}: {e}")
        return None


def parse_frontmatter(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    block = text[3:end]
    fields = {}
    for line in block.splitlines():
        if ":" in line and not line.startswith(" "):
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
    return fields


def main():
    plugin = load_json(ROOT / ".claude-plugin" / "plugin.json")
    marketplace = load_json(ROOT / ".claude-plugin" / "marketplace.json")

    if plugin is not None:
        for field in ("name", "version", "description", "license"):
            check(field in plugin, f"plugin.json missing required field: {field}")

    if marketplace is not None:
        check("plugins" in marketplace and marketplace["plugins"], "marketplace.json has no plugins entries")
        if marketplace.get("plugins"):
            entry = marketplace["plugins"][0]
            check("version" in entry, "marketplace.json plugin entry missing version")
            if plugin is not None and "version" in entry and "version" in plugin:
                check(
                    entry["version"] == plugin["version"],
                    f"version mismatch: plugin.json={plugin['version']} marketplace.json={entry['version']}",
                )

    check((ROOT / "LICENSE").exists(), "missing LICENSE file")

    for skill_md in sorted((ROOT / "skills").glob("*/SKILL.md")):
        fm = parse_frontmatter(skill_md)
        check(fm is not None, f"{skill_md.relative_to(ROOT)}: missing YAML frontmatter")
        if fm:
            for field in ("name", "description"):
                check(field in fm, f"{skill_md.relative_to(ROOT)}: frontmatter missing '{field}'")

    for agent_md in sorted((ROOT / "agents").glob("*.md")):
        fm = parse_frontmatter(agent_md)
        check(fm is not None, f"{agent_md.relative_to(ROOT)}: missing YAML frontmatter")
        if fm:
            for field in ("name", "description"):
                check(field in fm, f"{agent_md.relative_to(ROOT)}: frontmatter missing '{field}'")

    if errors:
        print("Validation FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("Validation OK: manifests, LICENSE, and frontmatter all consistent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
