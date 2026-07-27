---
name: manage-adrs
description: Use whenever the user wants to create, review, approve, reject, version, revise, supersede, undo, migrate, configure, or otherwise manage Architecture Decision Records (ADRs) via the `adrplus` CLI tool. Trigger on requests like "create an ADR for X", "approve this ADR", "supersede ADR 0001", "set up adrplus in this repo", or any mention of ADRs/architecture decision records in a repo that could use adrplus.
allowed-tools: Bash, Read, Write, Glob
---

# Managing ADRs with adrplus

`adrplus` is a cross-platform .NET CLI tool for managing Architecture Decision Records. This skill teaches you how to drive it directly, without ever going through its interactive `--wizard` mode.

## Critical rule: never use `--wizard`/`-w`

`adrplus`'s wizard mode is an interactive terminal UI (arrow-key menus, live text prompts) built for a human sitting at a real terminal. You cannot drive it through the Bash tool — it will hang waiting for keystrokes it will never receive. **Always use the direct, non-interactive flags documented below instead.** If a user explicitly asks to run the wizard themselves, tell them to run the command in their own terminal — don't attempt it yourself.

## Prerequisite

`adrplus` must already be installed as a .NET global tool:
```bash
adrplus --version
```
If this fails, tell the user to run `dotnet tool install -g adrplus` (requires .NET 8+ runtime) before continuing.

**Requires v1.0.0-beta or later.** Earlier versions draw a startup banner and can fall into an interactive first-run wizard on every command, unconditionally — both crash or hang when you (Claude) run them via Bash, even with all the right non-interactive flags. If a command you run this way fails with `"The handle is invalid"` or similar console errors instead of a normal error message, tell the user their `adrplus` is too old and needs upgrading (`dotnet tool update -g adrplus`).

## Two config files, one hard rule

- `adrplus.json` — application settings: `language`, `comandopenadr` (command to open a file, e.g. `code {0}`), `withoutargs`.
- `adr-config.adrplus` — repository settings: naming (`prefix`, `lenseq`, `lenversion`, `lenrevision`, `separator`, `casetransform`), scopes (`scopes`, `lenscope`, `folderbyscope`, `skipdomain`), status labels (`statusnew`, `statusacc`, `statusrej`, `statussup`), and header labels.

**The `config` command is ALWAYS interactive unless you pass `--file <path>` pointing to a ready-made JSON file.** There is no other non-interactive path for `config`. If you need to change a setting, write the JSON file yourself first (Write tool), then pass it with `--file`. Read the current file first (it's plain JSON in the repo root) so you only change what's needed.

`init` and `migrate`, by contrast, work non-interactively out of the box with just `--path` — no `--file` needed unless you want to seed a specific config.

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
| `adrplus migrate` | `-p/--path <dir>` | Adds AdrPlus headers to existing hand-written ADR files. Only works when **no** ADR has ever been created with `adrplus new` in that repo. Run `config --migrate` first if the default detection pattern doesn't fit. |
| `adrplus new` | `-p/--path <dir>` `-t/--title "<text>"` `-d/--domain "<text>"` `-s/--scope "<text>"` `-r/--refdate "YYYY-MM-DD"` `-o/--open` | Creates a new ADR with an incremental number. `--domain` is required unless the chosen scope is listed in `skipdomain`. |
| `adrplus approve` | `-f/--file <adr.md>` `-r/--refdate "YYYY-MM-DD"` | Sets status to Accepted. ADR must not already be approved/rejected. |
| `adrplus reject` | `-f/--file <adr.md>` `-r/--refdate "YYYY-MM-DD"` | Sets status to Rejected. Same eligibility as approve. |
| `adrplus undo` | `-f/--file <adr.md>` | Reverts the last status change. ADR must already be approved/rejected and not superseded. |
| `adrplus version` | `-f/--file <adr.md>` `-r/--refdate "YYYY-MM-DD"` `-o/--open` `-e/--empty` | Creates a new **major version** of an approved/rejected, non-superseded ADR. `--empty` starts from a blank template instead of copying content forward. |
| `adrplus revise` | `-f/--file <adr.md>` `-r/--refdate "YYYY-MM-DD"` `-o/--open` `-e/--empty` | Creates a new **revision** (minor change) of an ADR. Only works if revisions are enabled (`lenrevision > 0` in `adr-config.adrplus`). |
| `adrplus supersede` | `-f/--file <adr.md>` `-r/--refdate "YYYY-MM-DD"` `-o/--open` | Creates a successor ADR with a new sequence number; marks the original Superseded. Original must already be approved. |
| `adrplus explore` | `-p/--path <dir>` `-f/--file <report.md>` `-o/--open` | With both `--path` and `--file` given, generates a full Markdown table report of every ADR in the repo — fully non-interactive, includes all fields. This is the data source the `adr-indexer` agent uses. |

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

When you're about to run `git commit` or open a pull request on the user's behalf, launch the `adr-decision-check` agent **in the background** first — don't wait for it, and don't let it delay the commit/PR. Proceed with the commit/PR immediately; report the agent's verdict as a follow-up once it's ready, the same way a CI check reports after a push rather than blocking it. This is advisory only — never hold up or refuse a commit because of its recommendation.
