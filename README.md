# AdrPlus Claude Code Plugin

Lets Claude Code manage [Architecture Decision Records](https://adr.github.io/) in your repository via the [`adrplus`](https://github.com/FRACerqueira/AdrPlus) CLI, in plain language, instead of you typing every command yourself.

## What's included

- **Skill `manage-adrs`** — teaches Claude the `adrplus` command surface (create, approve, reject, version, revise, supersede, undo, init, migrate, config) so it can drive the CLI directly instead of guessing at flags.
- **Agent `adr-auditor`** — audits an existing ADR repository: structural compliance with `adr-config.adrplus`, content completeness, supersede-chain integrity, and status hygiene. Read-only, produces a report.
- **Agent `adr-indexer`** — generates a readable, grouped index page of all ADRs from `adrplus explore`'s report data.

## Prerequisite

Install the CLI itself first — this plugin doesn't bundle it:
```bash
dotnet tool install -g adrplus
adrplus --version
```

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
