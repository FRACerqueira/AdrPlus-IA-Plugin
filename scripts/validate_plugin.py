#!/usr/bin/env python3
"""Validate the plugin manifests and skill/agent frontmatter without external dependencies."""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import ROOT, report  # noqa: E402

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
    except OSError as e:
        errors.append(f"could not read {path.relative_to(ROOT)}: {e}")
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


def github_slug(heading):
    slug = heading.strip().lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug)
    return slug


def github_slugs(headings):
    """Replicates GitHub's anchor-slug algorithm including its duplicate-heading suffixing: the
    second occurrence of a given slug becomes `slug-1`, the third `slug-2`, and so on - the first
    occurrence keeps the bare slug. Without this, a link to the second `#foo` heading genuinely
    works on GitHub (as `#foo-1`) but this validator would report it as broken."""
    seen = {}
    slugs = []
    for heading in headings:
        base = github_slug(heading)
        count = seen.get(base, 0)
        slugs.append(base if count == 0 else f"{base}-{count}")
        seen[base] = count + 1
    return slugs


def strip_fenced_code_blocks(text):
    # So a line starting with `#` inside a ```bash fence (a shell comment, not a heading) can't be
    # misread as a real heading and added to valid_slugs.
    return re.sub(r"```.*?```", "", text, flags=re.DOTALL)


def check_readme_anchor_links():
    readme = ROOT / "README.md"
    if not readme.exists():
        return
    readme_text = strip_fenced_code_blocks(readme.read_text(encoding="utf-8"))
    headings = re.findall(r"^#{1,6}\s+(.+)$", readme_text, re.MULTILINE)
    valid_slugs = set(github_slugs(headings))

    for md in sorted(ROOT.glob("*.md")):
        if md.name == "README.md":
            continue
        text = md.read_text(encoding="utf-8")
        for anchor in re.findall(r"\]\(README\.md#([a-z0-9-]+)\)", text):
            check(
                anchor in valid_slugs,
                f"{md.relative_to(ROOT)}: links to README.md#{anchor}, but no README.md heading produces that anchor",
            )


def check_frontmatter_fields(md_path):
    """Checks that `md_path` has YAML frontmatter with non-empty `name`/`description` fields.

    Uses `fm is not None`, not truthy `fm` - a frontmatter block that's present but has no field
    colons at top level (or every field accidentally indented) parses to `{}`, which is falsy but
    IS present; the old `if fm:` skipped the name/description checks entirely in that case, so a
    file with neither field could still pass validation.
    """
    fm = parse_frontmatter(md_path)
    check(fm is not None, f"{md_path.relative_to(ROOT)}: missing YAML frontmatter")
    if fm is not None:
        for field in ("name", "description"):
            check(field in fm and fm[field], f"{md_path.relative_to(ROOT)}: frontmatter missing or empty '{field}'")
    return fm


def check_copilot_frontmatter_fields(md_path, tool_field):
    fm = check_frontmatter_fields(md_path)
    if fm is not None:
        check(
            tool_field in fm and fm[tool_field].strip(),
            f"{md_path.relative_to(ROOT)}: frontmatter missing or empty '{tool_field}'",
        )
    text = md_path.read_text(encoding="utf-8")
    check(
        "Last synced:" in text,
        f"{md_path.relative_to(ROOT)}: missing a 'Last synced:' provenance marker (see other copilot/ files for the convention)",
    )
    return fm


def check_copilot_parity():
    """Every canonical agents/*.md or skills/*/SKILL.md should have a copilot/ counterpart, and
    vice versa - a dropped or orphaned file on either side is exactly the kind of silent drift
    this validator otherwise has no way to catch."""
    canonical_agents = {p.stem for p in (ROOT / "agents").glob("*.md")}
    copilot_agents = {p.name[: -len(".agent.md")] for p in (ROOT / "copilot" / "agents").glob("*.agent.md")}
    for name in sorted(canonical_agents - copilot_agents):
        errors.append(f"agents/{name}.md has no copilot/agents/{name}.agent.md counterpart")
    for name in sorted(copilot_agents - canonical_agents):
        errors.append(f"copilot/agents/{name}.agent.md has no canonical agents/{name}.md counterpart")

    canonical_skills = {p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md")}
    copilot_skills = {p.parent.name for p in (ROOT / "copilot" / "skills").glob("*/SKILL.md")}
    for name in sorted(canonical_skills - copilot_skills):
        errors.append(f"skills/{name}/SKILL.md has no copilot/skills/{name}/SKILL.md counterpart")
    for name in sorted(copilot_skills - canonical_skills):
        errors.append(f"copilot/skills/{name}/SKILL.md has no canonical skills/{name}/SKILL.md counterpart")


def main():
    plugin = load_json(ROOT / ".claude-plugin" / "plugin.json")
    marketplace = load_json(ROOT / ".claude-plugin" / "marketplace.json")

    if plugin is not None:
        for field in ("name", "version", "description", "license"):
            check(field in plugin, f"plugin.json missing required field: {field}")

    if marketplace is not None:
        check("plugins" in marketplace and marketplace["plugins"], "marketplace.json has no plugins entries")
        for i, entry in enumerate(marketplace.get("plugins") or []):
            check("version" in entry, f"marketplace.json plugins[{i}] missing version")
            if plugin is not None and "version" in entry and "version" in plugin:
                check(
                    entry["version"] == plugin["version"],
                    f"version mismatch: plugin.json={plugin['version']} marketplace.json plugins[{i}].version={entry['version']}",
                )

    check((ROOT / "LICENSE").exists(), "missing LICENSE file")

    check_readme_anchor_links()
    check_copilot_parity()

    for skill_md in sorted((ROOT / "skills").glob("*/SKILL.md")):
        check_frontmatter_fields(skill_md)

    for agent_md in sorted((ROOT / "agents").glob("*.md")):
        check_frontmatter_fields(agent_md)

    for skill_md in sorted((ROOT / "copilot" / "skills").glob("*/SKILL.md")):
        check_copilot_frontmatter_fields(skill_md, "allowed-tools")

    for agent_md in sorted((ROOT / "copilot" / "agents").glob("*.agent.md")):
        check_copilot_frontmatter_fields(agent_md, "tools")

    return report(errors, "Validation", "Validation OK: manifests, LICENSE, and frontmatter all consistent.")


if __name__ == "__main__":
    sys.exit(main())
