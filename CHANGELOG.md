# Changelog

Versions refer to `.claude-plugin/plugin.json` / `marketplace.json` (the Claude Code plugin only —
`copilot/` has no version of its own, see [README.md](README.md#versioning)).

## Unreleased

- Added `HOWTO.md` / `HOWTO-CLAUDE-CODE.md` / `HOWTO-COPILOT.md` — end-user walkthroughs with a single
  running example, separate from the reference-style README.
- Fixed `adr-indexer` writing the raw `adrplus explore` table verbatim instead of a grouped, linked
  index when a repo has only one ADR (both `agents/adr-indexer.md` and its `copilot/` mirror).
- Corrected a stale claim in README.md and both `manage-adrs` `SKILL.md` files: `adrplus plugins`/`sync`
  have been on NuGet since beta6 (latest published release is beta9), not "unpublished, latest is beta5".
- Restored the "Invocation mode" clause to `copilot/agents/adr-decision-check.agent.md`'s `description`
  that had been dropped during the initial port, so Copilot's automatic agent-selection can match on it.
- `scripts/check_adrplus_compat.py` now also parses `copilot/skills/manage-adrs/SKILL.md`'s command
  table (previously only checked the Claude Code copy) and fails if the two tables drift apart from each
  other. Also fixed a regex that silently skipped the `plugins`/`sync` rows entirely (their
  `(v1.0.0-beta6+)` suffix broke the match) — both commands are now actually verified against
  `adrplus help`.

## 0.6.0 — 2026-08-06

- Added a `copilot/` mirror of `skills/manage-adrs` and all three agents, adapted for GitHub Copilot's
  Agent Skills / custom-agent format; tool-name mapping (`Bash`→`runCommands`, `Read`→`codebase`, etc.)
  live-tested in VS Code + Copilot Chat.
- Repository renamed `AdrPlus-Claude-Plugin` → `AdrPlus-IA-Plugin`; updated all internal references.
- README restructured into parallel `## Claude Code` / `## GitHub Copilot` sections.

## 0.5.0 — 2026-08-04

- Documented how to update the `adrplus` CLI and this plugin itself; fixed a version drift between
  `plugin.json` and `marketplace.json`.

## 0.4.0 — 2026-08-04

- Bumped the minimum required `adrplus` version to beta3 (earlier versions crashed when driven
  non-interactively — see beta1/beta2 notes in the skill).
- Documented `adrplus`'s own plugin system (`plugins`/`sync`, beta6+) — a separate mechanism from this
  Claude Code plugin.

## 0.3.0 — 2026-07-27/28

- Added the `adr-decision-check` agent (pre-commit/PR ADR-worthiness check).
- Sharpened its rules to exclude operational tweaks and offer a relaxed re-check.
- Tracked `adrplus` 1.0.0-beta1 as the minimum required version; documented known `adrplus` bugs.
- Fixed `adr-decision-check`'s frontmatter and `adr-auditor`'s naming formula.

## 0.2.0 — 2026-07-27

- Pointed `plugin.json` and the README at the real published repository.

## 0.1.0 — 2026-07-27

- Initial version: `manage-adrs` skill plus the `adr-auditor` and `adr-indexer` agents.
- Added `LICENSE`, `.gitignore`, plugin manifest fixes, and CI validation
  (`scripts/validate_plugin.py`, `.github/workflows/validate.yml`).
