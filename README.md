# AdrPlus Claude Code Plugin

Lets Claude Code manage [Architecture Decision Records](https://adr.github.io/) in your repository via the [`adrplus`](https://github.com/FRACerqueira/AdrPlus) CLI, in plain language, instead of you typing every command yourself.

## Key concepts

- **Architecture Decision Records (ADR)** — the plain-Markdown files this plugin manages. Every command in `manage-adrs`, and every check `adr-auditor` runs, operates on ADRs as defined by `adrplus`'s own naming and header conventions (see `adr-config.adrplus`).
- **Claude Code Plugin Marketplace** — the mechanism (`/plugin marketplace add`, `/plugin install`) this plugin is distributed through. See [Install](#install-local-marketplace-not-yet-published) below for how `marketplace.json` and `plugin.json` are wired together.
- **Claude Code Plugin Permissions** — the Bash permission Claude needs to actually run `adrplus` on your behalf; a plugin manifest cannot grant this itself, so you configure it in your own `.claude/settings.json` (see [Install](#install-local-marketplace-not-yet-published)).

## What's included

- **Skill `manage-adrs`** — teaches Claude the `adrplus` command surface (new, approve, reject, version, revise, supersede, undo, init, migrate, config, explore) so it can drive the CLI directly instead of guessing at flags.
- **Agent `adr-auditor`** — audits an existing ADR repository: structural compliance with `adr-config.adrplus`, content completeness, supersede-chain integrity, and status hygiene. Read-only, produces a report.
- **Agent `adr-indexer`** — generates a readable, grouped index page of all ADRs from `adrplus explore`'s report data.

## Prerequisite

Install the CLI itself first — this plugin doesn't bundle it:
```bash
dotnet tool install -g adrplus
adrplus --version
```

**Requires `adrplus` v1.0.0-beta or later.** Earlier versions unconditionally draw a startup banner and can fall into an interactive first-run wizard on every command — both crash or hang when driven non-interactively (exactly how Claude runs `adrplus` via the Bash tool). v1.0.0-beta is the first release safe for this plugin. Last tested: v1.0.0-beta — see `.github/workflows/validate.yml` for the automated compatibility check run against that version.

## Install (local marketplace, not yet published)

This plugin currently lives only on disk, not on GitHub. From a Claude Code session:
```
/plugin marketplace add C:\Sources\adrplus-claude-plugin
/plugin install adrplus@adrplus-tools
```

Once installed, Claude will need permission to run `adrplus` via Bash. If you don't want to approve it interactively every time, add to your own `.claude/settings.json` (project or user level):
```json
{
  "permissions": {
    "allow": ["Bash(adrplus *)"]
  }
}
```
(A plugin cannot grant this for you — see the [plugin permissions docs](https://code.claude.com/docs/en/plugins-reference.md).)

## Publishing later

To share this beyond your own machine, push this folder to a Git repo (e.g. `FRACerqueira/adrplus-claude-plugin`) and update `.claude-plugin/marketplace.json`'s plugin `source` if you split the marketplace from the plugin. Others would then run:
```
/plugin marketplace add FRACerqueira/adrplus-claude-plugin
/plugin install adrplus@adrplus-tools
```

## Versioning

`plugin.json` and `marketplace.json` both pin `0.1.0`. Bump both together on every meaningful change — Claude Code only picks up updates when the version changes (or, if you drop the `version` field, on every new commit).
