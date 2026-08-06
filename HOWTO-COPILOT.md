# How to use AdrPlus with GitHub Copilot

This page is for the person actually managing Architecture Decision Records day to day — not for
maintaining this repo. If you haven't set up the Copilot integration yet, do that first: [GitHub
Copilot setup](README.md#github-copilot) (copying `copilot/skills/` and `copilot/agents/` into your
repo's `.github/`). Come back here once that's done.

The idea: instead of memorizing `adrplus` flags, you just say what you want in plain language in
Copilot Chat, and it runs the right command. Everything below uses one running example — a team
deciding to adopt PostgreSQL as their primary database — so you can see the same decision move through
its whole lifecycle.

Two things to know about how this works on Copilot before you start:
- The `manage-adrs` **skill** (creating, approving, versioning ADRs) is picked up automatically — you
  don't select anything, just ask.
- The three **agents** (`adr-auditor`, `adr-indexer`, `adr-decision-check`) need to be selected from
  Copilot Chat's agent picker in **Agent mode** before you ask your question — they don't run just by
  mentioning what they do in plain text.

## Create your first ADR

In Copilot Chat, say:
> "Create an ADR for using PostgreSQL as our primary database, domain Backend."

Copilot runs `adrplus new` behind the scenes and tells you the file it created, something like
`doc/adr/ADR0001V01-UsePostgreSqlAsPrimaryDatabase.md`. Open it — it's a normal Markdown file, status
**Proposed**. Fill in the Context/Decision/Consequences sections yourself (Copilot won't invent your
reasoning for you); this is a record of a decision your team actually made, not generated content.

## Approve it once the team agrees

> "Approve the PostgreSQL ADR."

Status flips to **Accepted**, with today's date recorded. `reject` works the same way if the decision
was turned down instead.

## Ask "does this even need an ADR?"

Switch to the **adr-decision-check** agent, then ask:
> "Does this change need an ADR?"

You'll get a short verdict: no ADR needed, or a recommendation (new ADR, or a `version`/`revise`/
`supersede` of an existing one) with a reason. It's advisory — it never blocks your commit, and it never
creates or edits anything itself. (This agent is meant to run automatically right before a commit/PR too
— whether your Copilot surface supports that non-blocking, launch-and-continue invocation depends on
your setup; asking directly always works.)

## Something changes later

- Decision needs updating in a real way → **version**: `"Create a new version of the PostgreSQL ADR — we're adding a read replica."`
- Same decision, wording needs fixing → **revise**: `"Revise the PostgreSQL ADR, the consequences section was unclear."`
- A different decision replaces this one entirely → **supersede**: `"Supersede the PostgreSQL ADR — we're moving to CockroachDB instead."`

Each of these creates a new file and links it back to the original; the original's status updates
automatically (e.g. superseded ADRs get marked **Superseded**, pointing at their replacement).

## Keep your ADRs healthy

Switch to the **adr-auditor** agent, then ask:
> "Audit our ADRs."

You'll get a report: broken naming/headers, incomplete sections still holding template placeholder
text, broken supersede chains, and ADRs stuck in **Proposed** for a long time with nobody deciding. It's
read-only — it tells you what's wrong, it doesn't fix anything for you.

## Get a readable overview

Switch to the **adr-indexer** agent, then ask:
> "Generate an ADR index."

Unlike the raw `adrplus explore` report (a flat table), you get a page grouped by status and scope, with
links to each ADR — the kind of page you'd actually want to open to see where things stand.

## If something goes wrong

- **The agent isn't in the picker** — confirm `copilot/agents/*.agent.md` actually landed in your repo's
  `.github/agents/` (not just `copilot/agents/` — that's this repo's source copy, not a live location).
- **A tool gets rejected / "unknown tool" error** — Copilot's built-in tool names change over time; check
  the `tools:` list at the top of the relevant `.agent.md` file against your Copilot version's current
  built-in tools and adjust if needed.
- **"adrplus: command not found"** — the CLI isn't installed. See [Prerequisite](README.md#prerequisite).
- **A command fails with an odd console error instead of a normal message** — your `adrplus` version is
  probably too old. See [Prerequisite](README.md#prerequisite) for the minimum version and how to update.

Using Claude Code instead? See [HOWTO-CLAUDE-CODE.md](HOWTO-CLAUDE-CODE.md).
