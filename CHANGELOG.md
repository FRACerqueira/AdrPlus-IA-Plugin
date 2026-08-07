# Changelog

Versions refer to `.claude-plugin/plugin.json` / `marketplace.json` (the Claude Code plugin only —
`copilot/` has no version of its own, see [README.md](README.md#versioning)).

## 0.9.0 — 2026-08-07

- Raised the minimum supported `adrplus` version from beta3 to **v1.0.0-rc1** (matching AdrPlus's own
  README/NugetREADME, which made the same change) - beta1 through beta9 are no longer supported at
  all, not just beta1/beta2. Updated README.md, both `manage-adrs` `SKILL.md` files,
  `scripts/check_adrplus_compat.py` (now flags *any* beta pre-release, not just one below beta3), and
  `.github/workflows/validate.yml`'s `adrplus-compat` matrix (both the "latest" and "minimum" legs).

## 0.8.0 — 2026-08-07

- Corrected README's Update section: `/plugin marketplace update` reports how many plugins it bumped and
  updates the installed copy right then in practice — it doesn't require a separate manual
  reinstall-via-`/plugin` step unless it reports 0 plugins bumped.
- Fixed `scripts/check_adrplus_compat.py` collapsing `config --application`/`--repository`/`--template`/
  `--migrate` into a single `"config"` key, which hid drift in exactly that column; also relaxed its
  table-row regex to accept GFM rows without outer pipes, stopped it crashing on a malformed/empty
  command cell, generalized the two-file drift comparison to any number of `SKILL.md` copies, added
  proper error handling around the `adrplus` subprocess calls, and added a check that the installed
  `adrplus` isn't a beta below the documented minimum (beta3) - previously untested by CI.
- Fixed `scripts/validate_plugin.py` using truthy `if fm:` instead of `if fm is not None:`, which let a
  present-but-empty frontmatter block skip the `name`/`description` presence check entirely. Extended its
  `copilot/` coverage: `tools:`/`allowed-tools:` presence, the "Last synced:" provenance marker, and
  orphan detection between `agents/`↔`copilot/agents/` and `skills/`↔`copilot/skills/`. Also fixed its
  anchor-slug check to replicate GitHub's `-1`/`-2` duplicate-heading suffixing and to ignore headings
  inside fenced code blocks.
- `.github/workflows/validate.yml`'s `adrplus-compat` job now runs as a matrix testing both the
  documented minimum `adrplus` version (beta3) and the latest 1.x release - previously only ever
  installed the latest, so a regression specific to the floor would never have been caught.
- Corrected a changelog claim: the 0.6.0 tool-name mapping was checked against the
  `microsoft/vscode-copilot-chat` source, not live-tested in an actual Copilot session as previously
  worded.
- Added an explicit caveat to `copilot/skills/manage-adrs/SKILL.md`'s `allowed-tools` field: the Agent
  Skills spec marks it experimental and support/format actually diverges across GitHub's own Copilot
  surfaces (CLI vs. VS Code) - the previous wording implied a settled, verified mapping that doesn't
  exist yet. Also disclosed the foreground-fallback behavior in `copilot/agents/adr-decision-check.agent.md`
  and `copilot/skills/manage-adrs/SKILL.md`'s "Before committing" section as a deliberate Copilot-specific
  addition, not silent drift from the Claude original.
- README: promoted "Prerequisite" out of the Claude Code section (it applies to both integrations, and
  HOWTO-COPILOT.md was already linking to it as if it were neutral); added `Grep` to the documented
  Claude→Copilot tool mapping; removed an unsourced "Since November 2025" date claim.
- Added `scripts/_common.py`, shared between the two validation scripts, for the repeated
  root-path/error-reporting boilerplate.

## 0.7.0 — 2026-08-06

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
- Added `CHANGELOG.md`, a "last synced" marker in each `copilot/` file, an anchor-link validator in
  `scripts/validate_plugin.py`, and rounded out `.gitignore`.

## 0.6.0 — 2026-08-06

- Added a `copilot/` mirror of `skills/manage-adrs` and all three agents, adapted for GitHub Copilot's
  Agent Skills / custom-agent format; tool-name mapping (`Bash`→`runCommands`, `Read`→`codebase`, etc.)
  checked against the `microsoft/vscode-copilot-chat` source and its own docs/examples - not live-tested
  in an actual Copilot session (corrected wording; see also the `allowed-tools` caveat added to
  `copilot/skills/manage-adrs/SKILL.md` after researching this further).
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

## 0.3.0 — 2026-07-28

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
