# AdrPlus AI Assistant Plugin

Lets AI coding assistants manage [Architecture Decision Records](https://adr.github.io/) in your repository via the [`adrplus`](https://github.com/FRACerqueira/AdrPlus) CLI, in plain language, instead of you typing every command yourself. Two integrations are maintained in this repo:

- **[Claude Code](#claude-code)** — a full plugin (1 skill, 3 agents), distributed through Claude Code's plugin marketplace.
- **[GitHub Copilot](#github-copilot)** — the same skill and agents, adapted to Copilot's Agent Skills / custom-agent format under `copilot/` (copied manually into your repo — no marketplace exists for Copilot).

Already installed and just want to know what to actually type? See **[HOWTO.md](HOWTO.md)**.

## Key concepts

- **Architecture Decision Records (ADR)** — the plain-Markdown files this repo's tooling manages. Every command in `manage-adrs`, and every check `adr-auditor` runs, operates on ADRs as defined by `adrplus`'s own naming and header conventions (see `adr-config.adrplus`).
- **Agent Skills** — the open standard (`SKILL.md` + frontmatter) both Claude Code and GitHub Copilot consume; it's why `skills/manage-adrs` and `copilot/skills/manage-adrs` are near-identical rather than two unrelated implementations.
- **Claude Code Plugin Marketplace** — the mechanism (`/plugin marketplace add`, `/plugin install`) the Claude Code plugin is distributed through. See [Claude Code → Install](#install) below for how `marketplace.json` and `plugin.json` are wired together.
- **Claude Code Plugin Permissions** — the Bash permission Claude needs to actually run `adrplus` on your behalf; a plugin manifest cannot grant this itself, so you configure it in your own `.claude/settings.json` (see [Claude Code → Install](#install)).

## What's included

- **Skill `manage-adrs`** — teaches the assistant the `adrplus` command surface (new, approve, reject, version, revise, supersede, undo, init, migrate, config, explore, and — on v1.0.0-beta6+ — plugins, sync) so it can drive the CLI directly instead of guessing at flags.
- **Agent `adr-auditor`** — audits an existing ADR repository: structural compliance with `adr-config.adrplus`, content completeness, supersede-chain integrity, and status hygiene. Read-only, produces a report.
- **Agent `adr-indexer`** — generates a readable, grouped index page of all ADRs from `adrplus explore`'s report data.
- **Agent `adr-decision-check`** — checks pending changes (before a commit or PR, or on request) for whether they're architecturally significant enough to need an ADR, and if so whether it's a new ADR or a version/revise/supersede of an existing one. Read-only, recommends — never creates or edits ADRs itself.

The canonical source for all four lives under `skills/` and `agents/` (Claude Code format, described below). `copilot/` mirrors the same four, adapted for GitHub Copilot — see [GitHub Copilot](#github-copilot).

## Prerequisite

Applies to both integrations - `adrplus` itself is a standalone CLI, not something either plugin
bundles. Install it first:
```bash
dotnet tool install -g adrplus
adrplus --version
```

Already have it installed? Update to the latest release the same way you'd update any .NET global tool:
```bash
dotnet tool update -g adrplus
adrplus --version
```

**Requires `adrplus` v1.0.0-rc1 or later.** Earlier pre-releases aren't supported: versions before beta1 unconditionally drew a startup banner and could fall into an interactive first-run wizard on every command, and beta1/beta2 still crashed non-interactively on a genuinely fresh repository or a machine/version where `adrplus` had never been run interactively — both crashed or hung when driven non-interactively (exactly how an agent runs `adrplus` via its shell/terminal tool, regardless of which assistant). CI installs both the documented minimum (rc1) and the highest matching 1.x release — see `.github/workflows/validate.yml` for the automated compatibility check.

**`adrplus plugins`/`adrplus sync` need v1.0.0-beta6 or later** — automatically satisfied by the v1.0.0-rc1 floor above — AdrPlus's own plugin system (unrelated to either integration in this repo). The skill checks for these commands before using them and won't invent them on an older install.

## Claude Code

### Install

From a Claude Code session:
```
/plugin marketplace add FRACerqueira/AdrPlus-IA-Plugin
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

### Update

Third-party marketplaces don't auto-update by default. After a new version is pushed to this repo, refresh the catalog with:
```
/plugin marketplace update adrplus-tools
```
(`adrplus-tools` is the marketplace name from `marketplace.json`, not the GitHub repo name.) Watch its own output — in practice this command reports how many plugins it bumped (e.g. `Updated 1 marketplace (1 plugin bumped)`), and your installed copy moves to the new version right then, no extra step needed. If it reports 0 plugins bumped but you know a newer version exists, open `/plugin`, find `adrplus`, and update/reinstall it from there instead.

Prefer not to do this manually every time? Run `/plugin`, go to the **Marketplaces** tab, select `adrplus-tools`, and enable auto-update — Claude Code will then refresh the catalog and update installed plugins from it in the background on startup.

## GitHub Copilot

GitHub Copilot supports the same open [Agent Skills](https://agentskills.io/specification) standard as Claude Code, plus its own custom-agent format (`.github/agents/*.agent.md`). This repo ships a `copilot/` mirror of `skills/manage-adrs` and `agents/*.md`, adapted for Copilot:

```
copilot/
├── skills/
│   └── manage-adrs/SKILL.md
└── agents/
    ├── adr-auditor.agent.md
    ├── adr-indexer.agent.md
    └── adr-decision-check.agent.md
```

**There's no marketplace for Copilot** — unlike `/plugin install` above, there's no centralized install. Copy the files into the repo where you manage ADRs:
```bash
cp -r copilot/skills/manage-adrs your-repo/.github/skills/
cp copilot/agents/*.agent.md your-repo/.github/agents/
```
(or use `.claude/skills`, `.agents/skills`, or `~/.copilot/skills` for personal, cross-repo use — see [GitHub's agent skills docs](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills) for the full discovery rules.)

Claude Code's tool names (`Bash`, `Read`, `Write`, `Glob`, `Grep`) don't map 1:1 to Copilot's (`runCommands`, `codebase`, `editFiles`, `search`, ...) — each `copilot/agents/*.agent.md` file's `tools:` frontmatter carries the translated list (`Grep` and `Glob` both fold into Copilot's single `search` tool). This mapping only applies to the three `.agent.md` custom agents; `copilot/skills/manage-adrs/SKILL.md`'s own `allowed-tools` field follows a different, still-unsettled convention across Copilot surfaces — see the caveat in that file for specifics.

`copilot/` is not generated from `skills/`/`agents/` — there's no sync tooling yet. If you change the canonical Claude files, update `copilot/` by hand to keep them consistent.

## Versioning

Applies to the Claude Code plugin only — `copilot/` has no version/update mechanism of its own (see [GitHub Copilot](#github-copilot)). See [CHANGELOG.md](CHANGELOG.md) for what changed in each version.

`plugin.json`'s `version` and the matching plugin entry's `version` in `marketplace.json` must be bumped together on every meaningful change — Claude Code only picks up an update when that version string changes (or, if you drop the `version` field, on every new commit). Forgetting one of the two files leaves them out of sync and `/plugin marketplace update` won't see a new release.
