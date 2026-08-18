# How the agent standards are authored and delivered

This doc exists because the architecture below kept being rediscovered, and each rediscovery got at
least one part of it wrong. It lives here because `dotagents` is the repo that is general to every
codebase and the one opened when starting a new project. `Concertable/agent-standards` links it rather
than restating it.

## The four tiers — settled; do not redesign this

**Several sessions have re-derived this wrongly, each time confidently.** It is split by **who a rule
applies to**, and the repo boundary carries the scope — so a folder never repeats what its repo already
says.

| Tier | Repo | Scope | Sections |
|---|---|---|---|
| Generic .NET | `tomjseery/dotagents` | every .NET repo Tommy owns | the .NET concerns, plus his personal machine config |
| Generic React/TS | `tomjseery/react-agents` | every React/TS repo Tommy owns | the React concerns |
| Concertable | `Concertable/agent-standards` | everything Concertable-specific | `dotnet/`, `react/`, `process/` |
| One microservice | that service's own repo | only what is true of that service alone | `AGENTS.md` plus sibling docs it names |

### The three mistakes this table exists to stop

1. **`dotagents` is *dot-NET* agents — not "dotfiles for agents".** It holds the generic **.NET** standards.
   React standards live in `react-agents`. Any proposal that puts both stacks in one generic repo is wrong,
   and has been made more than once.
2. **`agent-standards` gets no `platform/` or `concertable/` section.** Concertable **is** the platform, and
   the repo already carries that scope; such a folder states it twice. An earlier revision proposed
   `concertable/` because it assumed one merged repo holding generic *and* product rules, where a folder was
   the only separator. Once the repos split by audience that folder became redundant.
3. **A microservice's `AGENTS.md` is not a dumping ground.** Where a service or module has conventions of its
   own, it points at sibling docs in its own repo — `CODE_CONVENTIONS.md`, `ARCHITECTURE.md`,
   `TECH_DEBT.md`. Roster and pointers in `AGENTS.md`; the detail in the doc it names.

### Placement test — one question per rule

| Does the rule… | Home |
|---|---|
| name no product at all | the generic repo for its stack — `dotagents` (.NET) or `react-agents` (React/TS) |
| name a Concertable type every service shares | `agent-standards`, in the section for its stack |
| name one service's own type | that service's repo, in `AGENTS.md` or a sibling doc |

Naming a **framework or third-party** type (`WebApplicationFactory`, `Testcontainers`, `axios`, `Reqnroll`)
does **not** make a rule product-specific. Only the *product's own* identifiers do. Stripping library names
out of a generic doc is how rules become ungreppable and unenforceable — see `DOCS_AND_DEBT.md`.

### Why they stay separate

Audience, not repo count. A TypeScript project has no use for the C# corpus, and a work repo has no use for
Concertable's merge queue. Plugins make count nearly free, because a project installs only what applies to
it. `dotagents` additionally mirrors `%USERPROFILE%` (`~/AGENTS.md`, `~/.agents/`, `~/.claude/`), which is
why the personal machine config sits alongside its .NET standards rather than in an org repo.

Also present: `Infonetica/standards-docs` (work standards, separate audience), `agent-utilities` (session
tooling, no standards), `agent-starter-kit` (archived — strict subset of `dotagents`).

## The doc is the payload; the skill is a router

A standard is a plain markdown file at `standards/<domain>/<TOPIC>.md`. Its skill is ~8 lines: front
matter plus that doc's path in backticks.

The inversion buys two things that text living inside a `SKILL.md` can never have:

- **Two delivery modes.** A repo can `@`-import the doc to make it always-on, or route to it by skill
  everywhere else. Content inside a `SKILL.md` is only ever delivered one way.
- **A browsable corpus.** A tree answers *"did I document this, and where?"*. A flat list of skill names
  answered that only for someone who already knew the answer.

Two naming rules that pull in opposite directions, deliberately:

- **A doc name never repeats its folder.** `dotnet/STYLE.md`, not `dotnet/CSHARP_STYLE.md`.
- **A skill name is globally unique**, because the deployed skill namespace is flat and spans every
  stack. So the skill is `csharp-style` while its doc is `dotnet/STYLE.md`; a skill called `style` would
  collide the moment a second stack wanted one.

**Skills stay flat.** Discovery is `<root>/skills/*/SKILL.md` and does not recurse. Only content nests.

## Authoring → generate → install

**A plugin COPIES its payload into a cache. It cannot reference anything outside the plugin root.**
`plugin.json`'s `skills` field rejects `../` paths, because files outside the root are never copied on
install. So there is one authored place and a **generate** step — never a reference.

*"The harness just reads the canonical skill"* is **false**, and believing it is the root of both the
stub mechanism and an earlier triple-copy generator.

**So be precise about what "defined once, referenced everywhere" means here**, because the loose version of
it causes real damage in both directions:

- **Authoring: one home, always.** A rule lives in exactly one file. Every other mention links to it and
  never restates it. A hand-written second copy is a bug, not emphasis.
- **Delivery: a copy, generated and checked.** A plugin cannot reference outside its root, so its payload is
  a full copy. That is fine *only* because it is generated from the one authored source and
  `sync-generated.ps1 -Check` fails when it drifts. An artifact that cannot be regenerated and diffed has no
  single home, whatever the intent was.

The failure this distinction prevents: reasoning "it's referenced, so I don't need to copy it" and shipping a
plugin whose skills point at a path present only on the author's machine.

```text
AUTHORED                                  GENERATED (never edit)
standards/<domain>/<TOPIC>.md   ───────►  plugins/<p>/standards/<domain>/<TOPIC>.md   full copy
.agents/skills/<name>/SKILL.md  ───────►  plugins/<p>/skills/<name>/SKILL.md          doc path rewritten
                                          .claude/skills/<name>/SKILL.md              repo-local
                                          standards/<domain>/INDEX.md                 from the tree
.agents/plugins/marketplace.json ──────►  .claude-plugin/marketplace.json             Codex reads both
.agents/plugins/payloads.json             which plugin ships which domains
.agents/hooks/*                 ───────►  plugins/<p>/hooks/*                         hook + its wiring
```

Run after any change to an authored file:

```
pwsh .agents/sync-generated.ps1          # write
pwsh .agents/sync-generated.ps1 -Check   # verify only; what CI runs
```

**Why the paths differ per target.** In the repo, cwd *is* the repo, so a root-relative
`standards/dotnet/STYLE.md` resolves. Inside an installed plugin, cwd is the **consuming project**, so
the same path would dangle — the plugin copy therefore carries a path relative to its own `SKILL.md`
(`../../standards/...`). The generator owns that rewrite; nobody hand-maintains it.

**The generator refuses to write** rather than emit something unroutable: a router naming a doc that does
not exist, a doc no router points at, two routers claiming one doc, a domain no plugin ships, a
description it cannot parse, a bare colon-space that truncates a YAML scalar, or a marketplace entry
pointing at a plugin with no manifest. Two structures that can drift is exactly how 754 lines of
frontend law once ended up with zero inbound links.

**`sync-generated.ps1` exists three times, and that is the open cost of this design.** Each standards repo
carries its own copy, because each one's CI has to verify itself without reaching a private sibling and a
plugin cannot reference outside its root. The copies are structurally parallel but not identical — this one
also handles utility stubs, `agent-standards` also copies a hook, `react-agents` does neither — so they are
kept diffable rather than merged: only the header paragraph of the `react-agents` copy differs from this
one. Sharing them properly needs a published PowerShell module or a submodule; a fourth repo is the point
at which that stops being the more expensive option.

## Per-machine setup — one time, both harnesses

**Neither harness auto-installs from a repo's settings.** Both need a one-time marketplace add plus
install, **per machine, not per repo** — so the cost does not grow with the number of repos. `--scope
user` makes one install cover every repo, present and future.

Claude Code:

```
/plugin marketplace add Concertable/agent-standards
/plugin install agent-process@agent-standards          # process + the write-time hook
/plugin marketplace add tomjseery/dotagents
/plugin install dotnet-standards@dotagents             # per stack - install what applies
/plugin marketplace add tomjseery/react-agents
/plugin install react-standards@react-agents
```

Codex — same plugins, and its skills appear namespaced (`agent-process:committing`):

```
codex plugin marketplace add https://github.com/Concertable/agent-standards
codex plugin add agent-process@agent-standards
codex plugin marketplace add https://github.com/tomjseery/dotagents
codex plugin add dotnet-standards@dotagents
```

`dotagents` and `react-agents` are private, so those marketplace adds need git credentials that can read
them.

Installed plugins land at `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/` and
`~/.codex/plugins/cache/<marketplace>/<plugin>/<version>/` — same shape, different home. Uninstalling
leaves the directory behind carrying an `.orphaned_at` marker, so a cache directory existing is **not**
evidence a plugin is installed.

**Plus, on Tommy's own machine only:** the personal half of `dotagents` is not a plugin. Copy `AGENTS.md`
and `.claude/` into `%USERPROFILE%`, then junction the skills and standards trees into place:

```
pwsh .agents/deploy-skills.ps1 -WhatIf   # inspect first
pwsh .agents/deploy-skills.ps1
```

That is also what delivers the 10 **utility** skills (`sync`, `worktree`, `recents`, …). They ship in no
plugin: they are procedures for working this machine, not standards any project consults.

## What a new project needs

**Nothing.** No `.claude/skills/` stubs, no vendored hook, no sync script. The standards arrive from
plugins installed per machine.

Two optional files, both the project's own:

1. **Its own `AGENTS.md`**, carrying only what the standards deliberately omit — the roster of real types,
   contexts, clients, tables and pins in *that* system. A generic rule in a project doc is a duplicate.
2. **`.agents/skill-routes.json`**, if it wants write-time enforcement: a table of path regex → owning
   skill, plus optional content-matched deny rules. A repo without it gets nothing and pays nothing.

## The hook is mechanism, not a standard

`skill_router.py` names no product and states no rule. It ships in `agent-process` and fires with **zero
repo wiring** — proven end to end: a directory holding only `.agents/skill-routes.json` blocked a write
into a routed path, named the owning skill, and the agent loaded it and retried. That is what retires
vendoring.

It exists because reachability was never the problem. A skill applies only if it is invoked: an agent
added a test project, misclassified it, used the wrong assertion library, with both testing skills
installed and listed — and the follow-up review repeated the same blind spot and returned clean. So the
trigger stopped being "the model decided this is relevant" and became **the path being written**.

Its coverage is deliberately partial: matchers are per-tool, so `dotnet new`, a shell heredoc, or an MCP
write never reach it, and injection is not compliance. **Where a rule is decidable at build time, the
build is the tier that guarantees**; this is the tier that gives fast feedback.

The same table also answers the question after the fact, which closes the *review* half of that failure:

```
git diff --name-only <range> | python <hook> --skills-for   # add --json for a machine
```

Because a skill can be delivered three ways, the hook resolves a skill's description from its own plugin
first, then `~/.agents/skills` and `~/.claude/skills`, then every other installed plugin's cache. Missing
any of those makes it report a correctly-installed skill as `NOT INSTALLED`.
