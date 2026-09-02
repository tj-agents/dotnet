# How the agent standards are authored and delivered

This doc exists because the architecture below kept being rediscovered, and each rediscovery got at
least one part of it wrong. It lives here because `dotagents` is the repo that is general to every
codebase and the one opened when starting a new project. `Concertable/agent-standards` links it rather
than restating it.

## The five tiers — settled; do not redesign this

**Several sessions have re-derived this wrongly, each time confidently.** It is split by **who a rule
applies to**, and the repo boundary carries the scope — so a folder never repeats what its repo already
says.

| Tier | Repo | Scope | Sections |
|---|---|---|---|
| Generic process | `tomjseery/process-agents` | every repo Tommy owns, whatever it is written in | the method, plus the hook mechanisms |
| Generic .NET | `tomjseery/dotagents` | every .NET repo Tommy owns | the .NET concerns, plus his personal machine config |
| Generic React/TS | `tomjseery/react-agents` | every React/TS repo Tommy owns | the React concerns |
| Concertable | `Concertable/agent-standards` | everything Concertable-specific | `dotnet/`, `react/` |
| One microservice | that service's own repo | only what is true of that service alone | `AGENTS.md` plus sibling docs it names |

### The four mistakes this table exists to stop

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
4. **Process is a tier, not a stack's leftovers.** Branching, plans, reviews, merging and handoffs belong to
   no stack, so for a while they had no generic home and defaulted into the product repo — 46 skills naming
   no product, shipping from `Concertable/agent-standards` under a plugin called `concertable`. Parking them
   in `dotagents` instead is mistake 1 in a new coat. They get their own repo, and it is the one plugin every
   repo installs.

### Placement test — one question per rule

| Does the rule… | Home |
|---|---|
| name no product **and** no stack — how work is done rather than what it is written in | `process-agents` |
| name no product, but bind to a stack | the generic repo for that stack — `dotagents` (.NET) or `react-agents` (React/TS) |
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

`process-agents` is the one that applies to *all* of them, which is why it also carries the hook mechanisms:
a rule enforced somewhere other than where it is written is a rule with nothing watching for drift.

Also present: `Infonetica/standards-docs` (work standards, separate audience), `agent-utilities` (session
tooling, no standards), `agent-starter-kit` (archived — strict subset of `dotagents`).

## Two authored skill shapes — routed, and self-contained

**Routed, and the default for a *stack* corpus.** A standard is a plain markdown file at
`standards/<domain>/<TOPIC>.md`, and its skill is ~8 lines: front matter plus that doc's path in backticks.
The inversion buys two things text living inside a `SKILL.md` can never have:

- **Two delivery modes.** A repo can `@`-import the doc to make it always-on, or route to it by skill
  everywhere else. Content inside a `SKILL.md` is only ever delivered one way.
- **A browsable corpus.** A tree answers *"did I document this, and where?"*. A flat list of skill names
  answered that only for someone who already knew the answer.

But the reason it is worth the split is narrower than either: **a routed doc's path is the pairing.**
`dotnet/testing/INTEGRATION.md` sits at the same path in `dotagents` and in `agent-standards`, and one skill
name (`integration-testing`) routes to both, so a generic rule and its product roster pair by construction.

**Self-contained, and what the process corpus actually is.** `process-agents` pairs with nothing, so the
split buys it nothing and costs it something: `@`-import does not expand inside a `SKILL.md` body — only
inside `CLAUDE.md`/`AGENTS.md` — so a router there is not a second delivery mode, just a guaranteed extra
Read for content the skill will never *not* need. Its skills carry the standard in the body and declare
`domain:` in front matter, since there is no doc path left to derive a domain from. One doc stays routed
(`standards/process/FLOOR.md`), because `session_floor.py` injects it rather than invoking it and so needs
it at a stable path.

**The generated payload is inline either way.** Whichever shape a skill is authored in, the generator emits
routed front matter combined with its canonical doc, so invoking any installed skill loads its rules in one
step. The authored split survives only where it is paying for the cross-repo pairing.

Two naming rules, and one that was retired:

- **A doc name never repeats its folder.** `dotnet/STYLE.md`, not `dotnet/CSHARP_STYLE.md`.
- **A skill name is unique within its plugin**, not globally. So the skill is `csharp-style` while its
  doc is `dotnet/STYLE.md` — a skill called `style` would still be a bad name, because it says nothing,
  but it would not *collide*.
- **Retired: globally-unique skill names.** It held while every skill was junctioned flat into one
  `~/.claude/skills`, and it cost a product prefix on one side of every mirrored pair — `persistence`
  and `concertable-persistence` for the generic rule and the product's roster of one topic. Plugins
  namespace them properly (`dotnet-standards:persistence`, `dotnet:persistence`), so routers stopped
  being junctioned and the prefix went with the constraint that produced it.

**Skills stay flat within a plugin.** Discovery is `<root>/skills/*/SKILL.md` and does not recurse. Only
content nests.

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
.agents/skills/<name>/SKILL.md  ───────►  plugins/<p>/skills/<name>/SKILL.md          doc inlined
                                          .claude/skills/<name>/SKILL.md              repo-local
                                          standards/<domain>/INDEX.md                 from the tree
.agents/plugins/marketplace.json         authored Codex marketplace
.claude-plugin/marketplace.json          authored Claude marketplace
plugins/<p>/.codex-plugin/plugin.json    authored Codex plugin manifest
.agents/plugins/payloads.json             which plugin ships which domains, and which ONE plugin
                                          owns the hooks, the route tables, the workflow resources
.agents/hooks/*                 ───────►  plugins/<p>/hooks/*                         hook + its wiring
.agents/routes/*                ───────►  plugins/<p>/routes/*                        registry + tables
.agents/workflows/*             ───────►  plugins/<p>/workflows/*, agents/, codex-agents/
```

Each of the last three is optional and gated on `payloads.json` naming an owner for it — that is what lets
one script serve a repo shipping only standards and a repo shipping the whole mechanism.

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

**`sync-generated.ps1` exists four times, and that is the open cost of this design.** Each standards repo
carries its own copy, because each one's CI has to verify itself without reaching a private sibling and a
plugin cannot reference outside its root.

An earlier revision named the fourth repo as the point where sharing them stops being the more expensive
option. **It was measured when the fourth arrived, and it is not** — for two reasons the estimate did not
have. First, the copies are structurally parallel but *not* converging: this one handles utility stubs,
`process-agents` handles hooks, route-table payloads, workflow contracts, host agent roles and Codex skill
payloads, `agent-standards` handles route tables and the routed `dotnet`/`react` trees, and `react-agents`
handles none of it. What each repo does *not* ship is as load-bearing as what it does. Second, every
consumer is private, so sharing means either a public tooling repo or a PAT provisioned into four CI
workflows — a real, recurring cost against copies that already diverge on purpose.

So they stay copies, and stay **diffable**: the shared spine is byte-identical and each repo's own payload
handling is gated on its `payloads.json` declaring an owner, so a repo that ships no hooks or no workflows
runs the same script and simply generates less. Diff two of them before editing either.

## Per-machine setup — one time, both harnesses

**Neither harness auto-installs from a repo's settings.** Provision both once per machine from a clone of
`Concertable/agent-standards`:

```
powershell -ExecutionPolicy Bypass -File scripts/provision-agent-standards.ps1
```

It installs or refreshes all five plugins at user scope in Claude Code and Codex, then verifies they are
enabled — three generic (`process-standards@process-agents`, `dotnet-standards@dotagents`,
`react-standards@react-agents`) and two Concertable (`dotnet@agent-standards`, `react@agent-standards`).
`-VerifyOnly` makes the same check without changing state. Start a new session afterward. All three generic
repos are private, so provisioning needs git credentials that can read them.

**The provisioning script itself still lives in `Concertable/agent-standards`**, which is the last thing
tying a non-Concertable machine to that repo. It stays there because it is the one file that must keep
working through every other move; relocating it is its own change, not a side effect of one.

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

That delivers the 10 **utility** skills (`sync`, `worktree`, `recents`, …) and every repo's standards
tree for reading and grepping. Utilities ship in no plugin: they are procedures for working this machine,
not standards any project consults.

**It does not deliver routers, and it prunes any it previously junctioned.** Those come from plugins now,
so a junction left behind under the same name would keep answering from a stale clone — an answer the
reader cannot tell apart from the plugin's. Install the plugins *before* running this, or the machine has
no standards between the two steps.

## What a new project needs

**Nothing.** No `.claude/skills/` stubs, no vendored hook, no sync script. The standards arrive from
plugins installed per machine.

Two optional files, both the project's own:

1. **Its own `AGENTS.md`**, carrying only what the standards deliberately omit — the roster of real types,
   contexts, clients, tables and pins in *that* system. A generic rule in a project doc is a duplicate.
2. **`.agents/skill-routes.json`**, if it wants write-time enforcement: a table of path regex → owning
   skill, plus optional content-matched deny rules. A repo without it gets nothing and pays nothing.

## The hook is mechanism, not a standard

`skill_router.py` names no product and states no rule. It ships in `process-standards@process-agents` and
fires with **zero repo wiring** — proven end to end: a directory holding only `.agents/skill-routes.json`
blocked a write into a routed path, named the owning skill, and the agent loaded it and retried. That is
what retires vendoring.

**The router and the route tables ship from different repos, and that is the point.** A carved service repo
carries no table of its own; the organisation registers it in a `routes/registry.json` that ships from *that
organisation's* repo — `Concertable/agent-standards`, whose `gen_skill_routes.py` holds the repo roster and
the rows naming its own types. The router names no organisation, so it resolves a registry from **any**
installed plugin, its own first, rather than only from beside itself.

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
