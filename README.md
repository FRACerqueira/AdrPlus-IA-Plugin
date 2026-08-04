# AdrPlus Claude Code Plugin

Lets Claude Code manage [Architecture Decision Records](https://adr.github.io/) in your repository via the [`adrplus`](https://github.com/FRACerqueira/AdrPlus) CLI, in plain language, instead of you typing every command yourself.

## Key concepts

- **Architecture Decision Records (ADR)** — the plain-Markdown files this plugin manages. Every command in `manage-adrs`, and every check `adr-auditor` runs, operates on ADRs as defined by `adrplus`'s own naming and header conventions (see `adr-config.adrplus`).
- **Claude Code Plugin Marketplace** — the mechanism (`/plugin marketplace add`, `/plugin install`) this plugin is distributed through. See [Install](#install) below for how `marketplace.json` and `plugin.json` are wired together.
- **Claude Code Plugin Permissions** — the Bash permission Claude needs to actually run `adrplus` on your behalf; a plugin manifest cannot grant this itself, so you configure it in your own `.claude/settings.json` (see [Install](#install)).

## What's included

- **Skill `manage-adrs`** — teaches Claude the `adrplus` command surface (new, approve, reject, version, revise, supersede, undo, init, migrate, config, explore, and — on v1.0.0-beta6+ — plugins, sync) so it can drive the CLI directly instead of guessing at flags.
- **Agent `adr-auditor`** — audits an existing ADR repository: structural compliance with `adr-config.adrplus`, content completeness, supersede-chain integrity, and status hygiene. Read-only, produces a report.
- **Agent `adr-indexer`** — generates a readable, grouped index page of all ADRs from `adrplus explore`'s report data.
- **Agent `adr-decision-check`** — checks pending changes (before a commit or PR, or on request) for whether they're architecturally significant enough to need an ADR, and if so whether it's a new ADR or a version/revise/supersede of an existing one. Read-only, recommends — never creates or edits ADRs itself.

## Prerequisite

Install the CLI itself first — this plugin doesn't bundle it:
```bash
dotnet tool install -g adrplus
adrplus --version
```

**Requires `adrplus` v1.0.0-beta3 or later (any 1.x release, including pre-releases).** Versions before beta1 unconditionally drew a startup banner and could fall into an interactive first-run wizard on every command — both crashed or hung when driven non-interactively (exactly how Claude runs `adrplus` via the Bash tool). beta1/beta2 still crashed non-interactively on a genuinely fresh repository or a machine/version where `adrplus` had never been run interactively — beta3 removed that dependency entirely. CI always installs the highest matching 1.x release — see `.github/workflows/validate.yml` for the automated compatibility check.

**`adrplus plugins`/`adrplus sync` need v1.0.0-beta6 or later, not yet published to NuGet as of this writing** (latest published release is beta5) — AdrPlus's own plugin system (unrelated to this Claude Code plugin). The skill checks for these commands before using them and won't invent them on an older install.

## Install

From a Claude Code session:
```
/plugin marketplace add FRACerqueira/AdrPlus-Claude-Plugin
/plugin install adrplus@adrplus-tools
```

Or, to work from a local clone instead:
```
/plugin marketplace add /path/to/your/local/clone
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

## Versioning

`plugin.json` and `marketplace.json` are kept in sync — bump both together on every meaningful change. Claude Code only picks up updates when the version changes (or, if you drop the `version` field, on every new commit).
