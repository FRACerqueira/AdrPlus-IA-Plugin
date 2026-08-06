# How to use AdrPlus with Claude Code

This page is for the person actually managing Architecture Decision Records day to day — not for
maintaining this repo. If you haven't installed the plugin yet, do that first: [Claude Code
install](README.md#install). Come back here once that's done.

The idea: instead of memorizing `adrplus` flags, you just say what you want in plain language, and
Claude runs the right command. Everything below uses one running example — a team deciding to adopt
PostgreSQL as their primary database — so you can see the same decision move through its whole
lifecycle.

## Create your first ADR

Say something like:
> "Create an ADR for using PostgreSQL as our primary database, domain Backend."

Claude runs `adrplus new` behind the scenes and tells you the file it created, something like
`doc/adr/ADR0001V01-UsePostgreSqlAsPrimaryDatabase.md`. Open it — it's a normal Markdown file, status
**Proposed**. Fill in the Context/Decision/Consequences sections yourself (Claude won't invent your
reasoning for you); this is a record of a decision your team actually made, not generated content.

## Approve it once the team agrees

> "Approve the PostgreSQL ADR."

Status flips to **Accepted**, with today's date recorded. `reject` works the same way if the decision
was turned down instead.

## Ask "does this even need an ADR?"

Before committing or opening a pull request, you don't have to remember to ask — Claude runs this check
proactively in the background and reports back without holding up your commit. But you can also ask
directly:
> "Does this change need an ADR?"

You'll get a short verdict: no ADR needed, or a recommendation (new ADR, or a `version`/`revise`/
`supersede` of an existing one) with a reason. It's advisory — it never blocks your commit, and it never
creates or edits anything itself.

## Something changes later

- Decision needs updating in a real way → **version**: `"Create a new version of the PostgreSQL ADR — we're adding a read replica."`
- Same decision, wording needs fixing → **revise**: `"Revise the PostgreSQL ADR, the consequences section was unclear."`
- A different decision replaces this one entirely → **supersede**: `"Supersede the PostgreSQL ADR — we're moving to CockroachDB instead."`

Each of these creates a new file and links it back to the original; the original's status updates
automatically (e.g. superseded ADRs get marked **Superseded**, pointing at their replacement).

## Keep your ADRs healthy

> "Audit our ADRs."

This launches the `adr-auditor` agent and produces a report: broken naming/headers, incomplete sections
still holding template placeholder text, broken supersede chains, and ADRs stuck in **Proposed** for a
long time with nobody deciding. It's read-only — it tells you what's wrong, it doesn't fix anything for
you.

## Get a readable overview

> "Generate an ADR index."

This launches the `adr-indexer` agent. Unlike the raw `adrplus explore` report (a flat table), you get a
page grouped by status and scope, with links to each ADR — the kind of page you'd actually want to open
to see where things stand.

## If something goes wrong

- **Nothing happens / it seems to hang** — Claude is probably trying to run `adrplus` in interactive
  wizard mode. That should never happen (both the skill and every agent are built to avoid it); if you
  see it, say so, it's a bug worth reporting.
- **"adrplus: command not found"** — the CLI isn't installed. See [Prerequisite](README.md#prerequisite).
- **A command fails with an odd console error instead of a normal message** — your `adrplus` version is
  probably too old. See [Prerequisite](README.md#prerequisite) for the minimum version and how to update.

Using GitHub Copilot instead? See [HOWTO-COPILOT.md](HOWTO-COPILOT.md).
