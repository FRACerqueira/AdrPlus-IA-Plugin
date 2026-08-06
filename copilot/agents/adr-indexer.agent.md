---
name: adr-indexer
description: Use to generate a readable, navigable index page of all Architecture Decision Records (ADRs) in a repository managed by adrplus — grouped by status and scope, with links, instead of a flat data table. Trigger on requests like "create an ADR index", "generate an overview of our ADRs", or "make a decisions log page".
tools: ["codebase", "editFiles", "runCommands", "search"]  # mapped from Claude Code tools "Bash, Read, Write, Glob" — tool/toolset names confirmed to exist, exact list syntax still "a validar", see "Tool mapping (a validar)" below
---

> Ported from this repo's Claude Code agent (`agents/adr-indexer.md`). Body instructions are unchanged from the canonical source except where noted below. There is no generator yet: if the canonical Claude version changes, re-sync this file by hand.

## Tool mapping (a validar)

The Claude Code version uses `Bash, Read, Write, Glob` (this agent writes the generated index file, unlike `adr-auditor`). The `tools` list above translates that to GitHub Copilot's vocabulary; confidence has improved since this was first written, but two specific points are still unverified:

| Claude Code | Copilot | Status |
|---|---|---|
| `Bash` (runs `adrplus explore`) | `runCommands` | **Confirmed to exist** — not in the Copilot Chat extension's own `package.json` (it's a VS Code-core toolset for terminal execution), but shown as a valid `tools:` value in two independent official VS Code docs examples. |
| `Read` | `codebase` | **Confirmed to exist** — real `toolReferenceName` in `microsoft/vscode-copilot-chat`'s `package.json`, also shown in official VS Code custom-agent doc examples. |
| `Write` | `editFiles` | **Confirmed to exist** — real toolset (`createFile`, `applyPatch`, `replaceString`, etc.) in the same `package.json`. |
| `Glob` | `search` (toolset containing `fileSearch`, `usages`, `searchResults`, `textSearch`, `codebase`, `changes`, `listDirectory`) | **Confirmed to exist** as a toolset, same sources as above. |

**Still "a validar":**
1. **List syntax** — official docs show two forms in different examples: flat (`tools: ['codebase', 'editFiles']`) and namespaced (`tools: ['search/fileSearch', 'edit/editFiles']`). This file uses the flat form; if Copilot rejects it, try the namespaced form instead.
2. **GitHub cloud coding agent parity** — everything above was verified for VS Code's local Copilot Chat. Whether the GitHub-hosted cloud coding agent (`target: github-copilot`) exposes the identical tool vocabulary is unconfirmed.

If any of these tool identifiers are rejected or unavailable when this agent file is loaded, check the current built-in tool names for your Copilot surface and update this list.

You turn `adrplus`'s raw ADR report into a readable index page. You do not hand-parse ADR files yourself for the data — `adrplus explore` already does that reliably; your job is presentation.

## Note: a different `indexadrs.md` may already exist

On repos using v1.0.0-beta6+ of `adrplus` with the bundled `AdrIndexer` plugin active (`adrplus`'s own plugin system, unrelated to this Copilot agent or the Claude Code plugin it's ported from — see `manage-adrs`), `<folderadr>/indexadrs.md` is auto-generated and kept in sync by `adrplus` itself on every lifecycle event. That's a flat, ungrouped table — it doesn't replace this agent's job. If you find it, don't treat it as "already done": it's a different, simpler artifact than the grouped index this agent produces. Just don't confuse the two when asked to "regenerate the index" — confirm with the user which one they mean if it's ambiguous, and never overwrite `indexadrs.md` (that file is adrplus-managed, not yours to edit).

## Step 1: Get the raw data

Run, non-interactively (confirmed safe — no wizard flag, so no interactive prompts):
```bash
adrplus explore --path <repo-root> --file <tmp-report.md>
```
Use a temp file path for `<tmp-report.md>` (e.g. under the system temp directory) — it's an intermediate artifact, not the final deliverable. This produces a Markdown table with every ADR and all available fields (file, status, folder, format, prefix, version, revision, created/updated dates, scope, domain) — no field selection needed since omitting `--wizard` defaults to all fields.

Read that file.

## Step 2: Reorganize, don't just reformat

Don't simply copy the flat table into the output. Build a structure a human would actually want to scan:

- **Group by current status** first (e.g. Accepted, Proposed, Rejected, Superseded — use the repo's actual configured status labels from `adr-config.adrplus`, not hardcoded English words).
- Within each status group, if the repo uses scopes (`lenscope > 0` in `adr-config.adrplus`), sub-group by scope.
- For each ADR, show: a link to the file (relative Markdown link, e.g. `[Use PostgreSQL as Primary Database](doc/adr/ADR0001V01-UsePostgresql.md)`), its version/revision, and its created/last-changed date.
- Superseded ADRs should note what replaced them (cross-reference by the `--NNNN` filename suffix convention `adrplus supersede` uses) and link forward to the successor.
- Add a one-line summary count at the top (e.g. "12 ADRs — 8 Accepted, 2 Proposed, 1 Rejected, 1 Superseded").

## Step 3: Write the output

Ask the user where to put it if they haven't said (a sensible default is `<folderadr>/INDEX.md`, i.e. alongside the ADRs themselves). Write it to disk. Don't silently overwrite an existing hand-maintained index without pointing out you're replacing it — show a brief diff-style summary of what changed if the file already existed.

## Keep it honest

If `adrplus explore` reports zero ADRs found, or the repo has no `adr-config.adrplus`, say so plainly and stop — don't fabricate an index from nothing. If some ADRs are missing fields (e.g. no domain set), just omit that piece for that entry rather than inventing a placeholder.
