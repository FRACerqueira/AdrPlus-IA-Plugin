---
name: manage-adrs
description: Use whenever the user wants to create, review, approve, reject, version, revise, supersede, undo, migrate, configure, audit, or fix the header/format of Architecture Decision Records (ADRs) via the `adrplus` CLI tool — including bringing pre-existing, hand-written ADR files into compliance with the adrplus schema, and (v1.0.0-beta6+) managing adrplus's own plugin system (`adrplus plugins`/`sync`). Trigger on requests like "create an ADR for X", "approve this ADR", "supersede ADR 0001", "set up adrplus in this repo", "fix these ADR headers to match adrplus", "adjust our ADRs to the adrplus standard", "list/activate/install an adrplus plugin", or any mention of ADRs/architecture decision records in a repo that could use adrplus.
allowed-tools: Bash Read Write Glob
compatibility: Requires the adrplus CLI installed as a .NET global tool (dotnet tool install -g adrplus).
metadata:
  ported-from: skills/manage-adrs/SKILL.md (Claude Code plugin, canonical source)
---

> Ported from this repo's Claude Code skill (`skills/manage-adrs/SKILL.md`). Content is functionally identical — only `allowed-tools` syntax and a couple of tool-name references below were adapted for the GitHub Copilot / Agent Skills open standard (agentskills.io/specification). There is no generator yet: if the canonical Claude version changes, re-sync this file by hand. **Last synced: 2026-08-06.**

# Managing ADRs with adrplus

`adrplus` is a cross-platform .NET CLI tool for managing Architecture Decision Records. This skill teaches you how to drive it directly, without ever going through its interactive `--wizard` mode.

## Critical rule: never use `--wizard`/`-w`

`adrplus`'s wizard mode is an interactive terminal UI (arrow-key menus, live text prompts) built for a human sitting at a real terminal. You cannot drive it through a non-interactive shell/terminal tool (`Bash` in Claude Code, `runCommands` in GitHub Copilot) — it will hang waiting for keystrokes it will never receive. **Always use the direct, non-interactive flags documented below instead.** If a user explicitly asks to run the wizard themselves, tell them to run the command in their own terminal — don't attempt it yourself.

## Prerequisite

`adrplus` must already be installed as a .NET global tool:
```bash
adrplus --version
```
If this fails, tell the user to run `dotnet tool install -g adrplus` (requires .NET 8+ runtime) before continuing. To upgrade an existing install to the latest release — including when the user asks directly how to update `adrplus`, or when the installed version is below one of the minimums in this section — the command is `dotnet tool update -g adrplus`, then re-check with `adrplus --version`. Don't wait for a crash to mention this.

**Requires v1.0.0-beta3 or later (any 1.x release, including pre-releases).** Versions before beta1 drew a startup banner and could fall into an interactive first-run wizard on every command, unconditionally — both crashed or hung when an agent runs them non-interactively via a shell/terminal tool, even with all the right non-interactive flags. beta1/beta2 still crashed non-interactively on a genuinely fresh repository or a fresh `adrplus` install (a machine-global template dependency that only the interactive first-run wizard ever satisfied); beta3 removed that dependency from every repo-touching command. If a command you run this way fails with `"The handle is invalid"` or similar console errors instead of a normal error message, tell the user their `adrplus` is too old and needs upgrading (see the update command above).

**`plugins` and `sync` (below) need v1.0.0-beta6 or later — published to NuGet since beta6 (latest published release as of this writing is beta9).** Check with `adrplus help` first: if `plugins`/`sync` aren't listed in its output, the installed version predates the plugin system — don't invent flags or attempt an alternate route around a missing command.

## Two config files, one hard rule

- `adrplus.json` — application settings: `language`, `comandopenadr` (command to open a file, e.g. `code {0}`), `withoutargs`.
- `adr-config.adrplus` — repository settings: naming (`prefix`, `lenseq`, `lenversion`, `lenrevision`, `separator`, `casetransform`), scopes (`scopes`, `lenscope`, `folderbyscope`, `skipdomain`), status labels (`statusnew`, `statusacc`, `statusrej`, `statussup`), header labels, and (v1.0.0-beta6+) plugin settings — `activeplugins` (names of host-installed plugins expected active for this repo, written by `init` and managed via `adrplus plugins --activate/--deactivate`, see below) and `disableplugins` (repo-wide kill switch; `true` skips all plugin dispatch regardless of `activeplugins`, without affecting the ADR operation itself).

**The `config` command is ALWAYS interactive unless you pass `--file <path>` pointing to a ready-made JSON file.** There is no other non-interactive path for `config`. If you need to change a setting, write the JSON file yourself first, then pass it with `--file`. Read the current file first (it's plain JSON in the repo root) so you only change what's needed.

`init` and `migrate`, by contrast, are designed to work non-interactively out of the box with just `--path` — no `--file` needed unless you want to seed a specific config.

## Command reference (verified against the actual `Arguments` definitions — do not invent flags not listed here)

Run `adrplus help <command>` yourself if anything here seems inconsistent with what you observe — the CLI's own help output is the source of truth.

| Command | Flags | Notes |
|---|---|---|
| `adrplus --version` | — | Prints the installed version. Not `adrplus version` (that's a different command, see below). |
| `adrplus help [command]` | | |
| `adrplus init` | `-p/--path <dir>` `-f/--file <config.json>` | Creates/updates `adr-config.adrplus` + the ADR folder. Safe to re-run. |
| `adrplus config --application` | `-f/--file <json>` | Edits `adrplus.json`. **Requires `--file` to be non-interactive.** |
| `adrplus config --repository` | `-f/--file <json>` | Edits `adr-config.adrplus`. **Requires `--file` to be non-interactive.** |
| `adrplus config --template` | `-f/--file <template.md>` | Sets the ADR template. **Requires `--file`.** |
| `adrplus config --migrate` | `-f/--file <json>` | Sets migration pattern settings (used by `migrate`, see below). **Requires `--file` to be non-interactive** — do NOT confuse with the `migrate` command itself. |
| `adrplus migrate` | `-p/--path <dir>` | Adds AdrPlus headers to existing hand-written ADR files. Only works when **no** ADR has ever been created with `adrplus new` in that repo. Run `config --migrate` first if the default detection pattern doesn't fit. **Verified (1.0.0-beta4):** the header row it writes embeds a literal `<!-- Migrated -->` marker inside the "Values" cell (e.g. `|Adr-Plus Fields|Values Migrated <!-- Migrated -->|`) — absent on ADRs created via `new`. `explore`'s `Format` column reports `Migrated` instead of `AdrPlus Format` for these files; this is intentional provenance tracking, not a defect, and `explore` still reads Status/dates correctly either way. Also verified: `migrate` leaves `Version`/`Revision`/`Created`/`Changed` **blank** in the new header — it does not carry values over from the old hand-written block. If you are hand-fixing a header to match this format (e.g. `migrate` itself is unusable because the repo already has `adrplus new`-created ADRs, or you're reconciling many files at once), include the `<!-- Migrated -->` marker for honesty about provenance, and manually carry the real Version/Revision/Status+date values over from the old block before deleting it — do not leave them blank. |
| `adrplus new` | `-p/--path <dir>` `-t/--title "<text>"` `-d/--domain "<text>"` `-s/--scope "<text>"` `-r/--refdate "YYYY-MM-DD"` `-o/--open` | Creates a new ADR with an incremental number. `--domain` is required unless the chosen scope is listed in `skipdomain`. |
| `adrplus approve` | `-f/--file <adr.md>` `-r/--refdate "YYYY-MM-DD"` | Sets status to Accepted. ADR must not already be approved/rejected. |
| `adrplus reject` | `-f/--file <adr.md>` `-r/--refdate "YYYY-MM-DD"` | Sets status to Rejected. Same eligibility as approve. |
| `adrplus undo` | `-f/--file <adr.md>` | Reverts the last status change. ADR must already be approved/rejected and not superseded. |
| `adrplus version` | `-f/--file <adr.md>` `-r/--refdate "YYYY-MM-DD"` `-o/--open` `-e/--empty` | Creates a new **major version** of an approved/rejected, non-superseded ADR. `--empty` starts from a blank template instead of copying content forward. |
| `adrplus revise` | `-f/--file <adr.md>` `-r/--refdate "YYYY-MM-DD"` `-o/--open` `-e/--empty` | Creates a new **revision** (minor change) of an ADR. Only works if revisions are enabled (`lenrevision > 0` in `adr-config.adrplus`). |
| `adrplus supersede` | `-f/--file <adr.md>` `-r/--refdate "YYYY-MM-DD"` `-o/--open` | Creates a successor ADR with a new sequence number; marks the original Superseded. Original must already be approved. |
| `adrplus explore` | `-p/--path <dir>` `-f/--file <report.md>` `-o/--open` | With both `--path` and `--file` given, generates a full Markdown table report of every ADR in the repo — fully non-interactive, includes all fields. This is the data source the `adr-indexer` agent uses. |
| `adrplus plugins` (v1.0.0-beta6+) | `-p/--path <dir>` `-l/--list` `-v/--validate` `-a/--activate <name>` `-d/--deactivate <name>` `-i/--install <zip>` `-u/--uninstall <name>` `-f/--force` | Manages AdrPlus's own plugin system — plugins implementing `IAdrPlugin` that react to ADR lifecycle events (e.g. the bundled `AdrIndexer` reference plugin, which auto-writes `<folderadr>/indexadrs.md` on every create/approve/reject/revise/supersede/undo). **Not this Copilot skill or the Claude Code plugin it's ported from** — a separate, unrelated extensibility mechanism inside the `adrplus` CLI itself. `--path` is required for `--list`/`--validate`/`--activate`/`--deactivate` (repo-scoped); `--install`/`--uninstall` take **no** `--path` — they install/remove a plugin machine-wide. `--force` (with `--install`) overwrites an already-installed plugin entirely. |
| `adrplus sync` (v1.0.0-beta6+) | `-p/--path <dir>` `-b/--backfill` | Re-drives plugin dispatches that failed to complete for a repo. `--backfill` re-emits every ADR's current settled event to all active plugins — per the CLI's own help text, this is **manual/occasional use only, never automate via cron/CI**. |

`version` vs `revise` vs `supersede`, in one line each: **version** = new major decision on the same topic; **revise** = fix/clarify wording, same decision; **supersede** = a *different* decision replaces this one entirely.

## Typical flows

**First time in a repo with no existing ADRs:**
```bash
adrplus init --path .
adrplus new --path . --title "Use PostgreSQL as primary database" --domain "Backend"
```

**Repo with existing hand-written ADRs to bring under adrplus:**
```bash
adrplus init --path .
# only if the default filename pattern won't be auto-detected correctly:
adrplus config --migrate --file migration-config.json
adrplus migrate --path .
```

**Everyday lifecycle:**
```bash
adrplus approve --file "./doc/adr/ADR0001V01-UsePostgresql.md"
adrplus revise  --file "./doc/adr/ADR0001V01-UsePostgresql.md"
adrplus supersede --file "./doc/adr/ADR0001V01-UsePostgresql.md" --open
```

## When in doubt

If a user's request doesn't map cleanly onto one of the rows above, run `adrplus help <command>` and read its actual output before guessing at a flag. Never fall back to `--wizard` to sidestep uncertainty.

## Before committing or opening a PR

When you're about to run `git commit` or open a pull request on the user's behalf, launch the `adr-decision-check` agent first. The Claude Code version launches this in the background (non-blocking) and reports the verdict as a follow-up once ready, so it never delays the commit/PR; do the same on Copilot if your surface supports non-blocking subagent invocation. If it doesn't, run it in the foreground instead, but keep it advisory either way: never hold up or refuse a commit because of its recommendation.
