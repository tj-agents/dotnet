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

## The skill is the payload

A standard is authored in exactly one file: `.agents/skills/<name>/SKILL.md`, front matter followed by
the standard itself. There is no separate doc and no `standards/` tree.

**This reverses an earlier design, deliberately** — the doc used to be the payload and the skill a ~8-line
router naming its path. That inversion was argued to buy two things, and neither survived contact:

- **"Two delivery modes."** A repo could `@`-import the doc to make it always-on, or route to it by skill
  everywhere else. But `@`-import only expands inside `CLAUDE.md`/`AGENTS.md` — **never inside a
  `SKILL.md`**. So the second mode was only ever available to a repo willing to always-on the doc, while
  every skill invocation paid a guaranteed extra Read tool call for content it was always going to need.
- **"A browsable corpus."** A tree answered *"did I document this, and where?"*. A generated catalogue
  answers it better, because it is derived from the skills themselves and cannot drift from them — see
  `SKILLS.md`, generated per repo.

Two naming rules, and two that were retired:

- **A skill name says what it covers.** `csharp-style`, not `style` — the latter says nothing. Names are
  unique within a plugin, not globally.
- **A standard declares its `domain:`** in front matter. That is the single authored fact deciding which
  plugin ships it, and it is what tells a standard apart from a utility skill.
- **Retired: globally-unique skill names.** It held while every skill was junctioned flat into one
  `~/.claude/skills`, and it cost a product prefix on one side of every pair — `persistence` and
  `concertable-persistence` for the generic rule and the product's roster of one topic. Plugins namespace
  them properly, so the prefix went with the constraint that produced it.
- **Retired: mirrored doc paths.** A local standard and its generic counterpart used to pair by sitting
  at the *same path* in two repos. **They now pair by SKILL NAME, told apart by PLUGIN NAMESPACE** —
  `dotnet-standards:persistence` here, `dotnet:persistence` in `agent-standards`. The path mirror was a
  second structure encoding a fact the skill name already carried, it only ever held for the subset of
  topics both repos happened to cover, and it was the sole reason `dotnet`/`react` kept the routed shape
  after `process` had left it.

**Skills stay flat within a plugin.** Discovery is `<root>/skills/*/SKILL.md` and does not recurse.

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
.agents/skills/<name>/SKILL.md  ───────►  plugins/<p>/skills/<name>/SKILL.md          verbatim copy
                                          .claude/skills/<name>/SKILL.md              repo-local
                                          SKILLS.md                                   from the skills
.agents/plugins/marketplace.json         authored Codex marketplace
.claude-plugin/marketplace.json          authored Claude marketplace
plugins/<p>/.codex-plugin/plugin.json    authored Codex plugin manifest
.agents/plugins/payloads.json             which plugin ships which domains
.agents/hooks/*                 ───────►  plugins/<p>/hooks/*                         hook + its wiring
```

Run after any change to an authored file:

```
pwsh .agents/sync-generated.ps1          # write
pwsh .agents/sync-generated.ps1 -Check   # verify only; what CI runs
```

**Every copy is now verbatim**, which is the practical dividend of retiring the routed shape. A router
carried a root-relative doc path that resolved in the repo (cwd *is* the repo) but dangled inside an
installed plugin (cwd is the **consuming project**), so the generator had to rewrite that path per target
and refuse to build if the router's sentence ever changed shape. A self-contained skill names no path, so
there is nothing to rewrite and nothing to keep in sync.

**The generator refuses to write** rather than emit something unroutable: a skill whose domain no plugin
ships, a plugin claiming a domain no skill declares, a standard with no heading for the catalogue, a
description it cannot parse, a bare colon-space that truncates a YAML scalar, or a marketplace entry
pointing at a plugin with no manifest. Two structures that can drift is exactly how 754 lines of
frontend law once ended up with zero inbound links.

**`sync-generated.ps1` exists three times, and that is the open cost of this design.** Each standards repo
carries its own copy, because each one's CI has to verify itself without reaching a private sibling and a
plugin cannot reference outside its root. The copies are structurally parallel but not identical — this one
also handles utility stubs, `agent-standards` also copies a hook and generates the SessionStart floor
document from the skill that owns it, `react-agents` does neither — so they are kept diffable rather than
merged: only the header paragraph of the `react-agents` copy differs from this one. Sharing them properly
needs a published PowerShell module or a submodule; a fourth repo is the point at which that stops being
the more expensive option.

## Per-machine setup — one time, both harnesses

**Neither harness auto-installs from a repo's settings.** Provision both once per machine from a clone of
`Concertable/agent-standards`:

```
powershell -ExecutionPolicy Bypass -File scripts/provision-agent-standards.ps1
```

It installs or refreshes all five plugins at user scope in Claude Code and Codex, then verifies they are
enabled. `-VerifyOnly` makes the same check without changing state. Start a new session afterward.
`dotagents` and `react-agents` are private, so provisioning needs git credentials that can read them.

Installed plugins land at `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/` and
`~/.codex/plugins/cache/<marketplace>/<plugin>/<version>/` — same shape, different home. Uninstalling
leaves the directory behind carrying an `.orphaned_at` marker, so a cache directory existing is **not**
evidence a plugin is installed.

**Plus, on Tommy's own machine only:** the personal half of `dotagents` is not a plugin. Copy `AGENTS.md`
and `.claude/` into `%USERPROFILE%`, then junction the utility skills into place:

```
pwsh .agents/deploy-skills.ps1 -WhatIf   # inspect first
pwsh .agents/deploy-skills.ps1
```

That delivers the 10 **utility** skills (`sync`, `worktree`, `recents`, …). Utilities ship in no plugin:
they are procedures for working this machine, not standards any project consults.

**It does not deliver standards, and it prunes anything it previously junctioned** — both the skills it
stopped owning and the whole retired `~/.agents/standards` tree. Standards come from plugins now, so a
junction left behind would keep answering from a stale clone, an answer the reader cannot tell apart from
the plugin's. Install the plugins *before* running this, or the machine has no standards between the two
steps.

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
