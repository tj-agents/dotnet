#!/usr/bin/env pwsh
<#
Regenerates everything in this repo that is derived from `.agents/` and `standards/`.

Two kinds of skill live here, and the difference is what gets generated:

  a STANDARD   the rule text is a doc under `standards/<domain>/`, and `.agents/skills/<name>/SKILL.md`
               is a router: front matter plus the doc's root-relative path in backticks. A doc is a
               plain markdown file, so it can be `@`-imported by a repo that wants it always-on or
               routed to by its skill everywhere else. Text inside a SKILL.md gets one delivery mode.

  a UTILITY    a procedure the agent runs (`sync`, `worktree`, `recents`). There is no corpus to
               consult, so the body stays in its SKILL.md and no doc exists.

Generated:
  .claude/skills/<name>/SKILL.md   for a harness opened on THIS repo. A router is copied verbatim -
                                   its root-relative doc path resolves because cwd is this repo. A
                                   utility gets a stub pointing at canonical, so its body is not
                                   duplicated.
  standards/<domain>/INDEX.md      the tree answers "where is it"; this answers "did I document this"
                                   without opening anything.
  plugins/<p>/skills/…             router copy with its doc path rewritten relative to the SKILL.md,
                                   and plugins/<p>/standards/… a full copy of the domains that plugin
                                   claims. An installed plugin is only its own subtree and cwd is the
                                   consuming project, so a root-relative path would dangle and a
                                   reference outside the plugin root is never copied at all.
  .agents/plugins/marketplace.json and .claude-plugin/marketplace.json are authored separately because
                                   the two harnesses require different schemas. Each plugin carries both
                                   .claude-plugin/plugin.json and .codex-plugin/plugin.json.

Plugins carry the domains `.agents/plugins/payloads.json` assigns them, so a consumer installs per
stack rather than receiving every corpus. The 10 utility skills ship in no plugin - they are machine
tooling, delivered by deploy-skills.ps1 from this clone. The write-time router hook
lives in `Concertable/agent-standards` and ships in its `concertable` plugin, so a project wanting
enforcement installs that too.

Refuses to write when the two structures disagree: a router naming a doc that does not exist, a doc no
router points at, or two routers claiming one doc. A tree and a skill namespace that can drift is
exactly how 754 lines of frontend law ended up with zero inbound links.

  pwsh .agents/sync-generated.ps1
  pwsh .agents/sync-generated.ps1 -Check   # verify only; non-zero exit if anything is stale
#>

[CmdletBinding()]
param([switch]$Check)

$ErrorActionPreference = 'Stop'

$repoRoot     = Split-Path -Parent $PSScriptRoot
$canonical    = Join-Path $repoRoot '.agents/skills'
$standardsDir = Join-Path $repoRoot 'standards'
$manifest     = Join-Path $repoRoot '.agents/plugins/marketplace.json'
$claudeManifest = Join-Path $repoRoot '.claude-plugin/marketplace.json'
$payloadsFile = Join-Path $repoRoot '.agents/plugins/payloads.json'
$utf8NoBom    = New-Object System.Text.UTF8Encoding($false)

$INDEX_NAME  = 'INDEX.md'
$STUB_MARKER = 'compatibility stub'

function Read-Lf([string]$path) {
    return ([System.IO.File]::ReadAllText($path) -replace "`r`n", "`n")
}

# Kept to string trimming rather than [Path]::GetRelativePath / Resolve-Path -RelativeBasePath: both
# need PowerShell 7, and this repo is cloned onto machines that only have 5.1.
function To-RepoRelative([string]$fullPath, [string]$base) {
    $separator = [System.IO.Path]::DirectorySeparatorChar
    $normalizedBase = ((Resolve-Path -LiteralPath $base).ProviderPath.TrimEnd('\', '/')) + $separator
    $full = (Resolve-Path -LiteralPath $fullPath).ProviderPath
    if (-not $full.StartsWith($normalizedBase, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "$full is not under $normalizedBase."
    }
    return ($full.Substring($normalizedBase.Length) -replace '\\', '/')
}

# A skill's `description` is what decides whether it loads at all, so every generated copy carries the
# canonical one; boilerplate there means the skill silently never fires.
function Get-CanonicalDescription([string]$text, [string]$name) {
    $match = [regex]::Match($text, "(?s)\A---\n.*?^description:[ \t]*(.+?)\n(?:[a-zA-Z-]+:|---)", 'Multiline')
    if (-not $match.Success) {
        throw "$name/SKILL.md has no parsable ``description:`` in its front matter."
    }
    $description = $match.Groups[1].Value.Trim() -replace "\s*\n\s*", " "
    # A bare colon-space anywhere in an unquoted YAML scalar silently truncates the value.
    if ($description -match ':\s') {
        throw "$name/SKILL.md description contains a colon-space, which breaks the YAML scalar: $description"
    }
    return $description
}

# A router's single authored fact about its payload: the doc's root-relative path, in backticks. Parsed
# rather than held in a side table, because a second structure is a second thing that drifts. No match
# means a utility, which owns no doc.
function Get-RoutedDoc([string]$text, [string]$name) {
    $found = [regex]::Matches($text, '`(standards/[^`]+\.md)`')
    $paths = @($found | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique)
    if ($paths.Count -eq 0) { return $null }
    if ($paths.Count -gt 1) {
        throw "$name/SKILL.md names $($paths.Count) docs ($($paths -join ', ')); a router owns exactly one."
    }
    return $paths[0]
}

# The plugin copy must name only what ships beside it. The authored router also cites the deployed
# ~/.agents/standards path, which need not exist on a machine that installed the plugin and never cloned
# the repo - a reader who tries it first finds nothing.
function Rewrite-ForPlugin([string]$body) {
    $rewritten = [regex]::Replace(
        $body,
        'The standard is `standards/(?<doc>[^`]+)` in `[^`]+`, deployed to `~/\.agents/standards/[^`]+`\.',
        'The standard is `../../standards/${doc}`, shipped in this plugin.')
    if ($rewritten -eq $body) {
        throw "plugin rewrite matched nothing; the router sentence changed shape and the copy would keep a path that dangles on install."
    }
    return $rewritten
}

function Get-StubBody([string]$name, [string]$description) {
@"
---
name: $name
description: $description
---

# $name

This is a Claude Code $STUB_MARKER. Do not edit skill instructions here.

Read and follow the canonical agent-agnostic skill at ../../../.agents/skills/$name/SKILL.md.

"@ -replace "`r`n", "`n"
}

# Skills stay flat: discovery is <root>/skills/*/SKILL.md and does not recurse. Only content nests.
$skillDirs = @(Get-ChildItem -Path $canonical -Directory |
    Where-Object { Test-Path (Join-Path $_.FullName 'SKILL.md') } | Sort-Object Name)
if (-not $skillDirs) { throw "No canonical skills found under .agents/skills." }

$skills = [ordered]@{}
foreach ($dir in $skillDirs) {
    $text = Read-Lf (Join-Path $dir.FullName 'SKILL.md')
    $skills[$dir.Name] = [pscustomobject]@{
        Name        = $dir.Name
        Body        = $text
        Description = Get-CanonicalDescription $text $dir.Name
        Doc         = Get-RoutedDoc $text $dir.Name
    }
}

# The standards tree is walked recursively - nesting is the whole point of the tree.
$docs = @()
if (Test-Path $standardsDir) {
    $docs = @(Get-ChildItem -Path $standardsDir -Recurse -File -Filter '*.md' |
        Where-Object { $_.Name -ne $INDEX_NAME } |
        ForEach-Object { To-RepoRelative $_.FullName $repoRoot } |
        Sort-Object)
}

# Neither structure may grow an orphan.
$problems = @()
foreach ($skill in $skills.Values) {
    if ($skill.Doc -and ($docs -notcontains $skill.Doc)) {
        $problems += "skill '$($skill.Name)' routes to '$($skill.Doc)', which does not exist."
    }
}
foreach ($doc in $docs) {
    $owners = @($skills.Values | Where-Object { $_.Doc -eq $doc } | Select-Object -ExpandProperty Name)
    if ($owners.Count -eq 0) {
        $problems += "doc '$doc' has no routing skill, so nothing loads it."
    }
    if ($owners.Count -gt 1) {
        $problems += "doc '$doc' is routed by $($owners.Count) skills ($($owners -join ', ')); it needs exactly one owner."
    }
}
if ($problems) {
    Write-Host "The standards tree and the skill namespace disagree:"
    foreach ($problem in $problems) { Write-Host "  $problem" }
    exit 1
}

$pluginRoot = Join-Path $repoRoot 'plugins'
$plugins = @()
if (Test-Path $pluginRoot) { $plugins = @(Get-ChildItem -Path $pluginRoot -Directory) }

# Refuse to generate against a marketplace pointing at a plugin that is not there, or a plugin with no
# manifest of its own - an unroutable package installs and delivers nothing.
if (-not (Test-Path $manifest)) { throw "Missing canonical manifest .agents/plugins/marketplace.json." }
$manifestBody = Read-Lf $manifest
$manifestJson = ConvertFrom-Json $manifestBody
$declared = @()
foreach ($entry in $manifestJson.plugins) {
    $declared += $entry.name
    if ($entry.source.source -ne 'local' -or -not $entry.source.path) {
        throw "marketplace.json plugin '$($entry.name)' must use a local source object with a path."
    }
    if (-not $entry.policy.installation -or -not $entry.policy.authentication -or -not $entry.category) {
        throw "marketplace.json plugin '$($entry.name)' must declare installation, authentication, and category."
    }
    $source = Join-Path $repoRoot ($entry.source.path -replace '^\./', '')
    if (-not (Test-Path $source)) {
        throw "marketplace.json declares '$($entry.name)' at $($entry.source.path), which does not exist."
    }
    if (-not (Test-Path (Join-Path $source '.claude-plugin/plugin.json'))) {
        throw "Plugin '$($entry.name)' has no .claude-plugin/plugin.json, so Claude cannot load it."
    }
    if (-not (Test-Path (Join-Path $source '.codex-plugin/plugin.json'))) {
        throw "Plugin '$($entry.name)' has no .codex-plugin/plugin.json, so Codex cannot load it."
    }
}
if (-not (Test-Path $claudeManifest)) { throw "Missing Claude manifest .claude-plugin/marketplace.json." }
$claudeDeclared = @((ConvertFrom-Json (Read-Lf $claudeManifest)).plugins | ForEach-Object { $_.name } | Sort-Object)
$codexDeclared = @($declared | Sort-Object)
if (($claudeDeclared -join "`n") -ne ($codexDeclared -join "`n")) {
    throw "Claude and Codex marketplaces declare different plugins."
}

# Which plugin ships which domains. Authored rather than inferred from a plugin's name, and cross-checked
# both ways against the marketplace so the two cannot drift about what exists.
if (-not (Test-Path $payloadsFile)) { throw "Missing .agents/plugins/payloads.json." }
$payloads = (ConvertFrom-Json (Read-Lf $payloadsFile)).payloads
$pluginDomains = @{}
foreach ($property in $payloads.PSObject.Properties) {
    if ($declared -notcontains $property.Name) {
        throw "payloads.json declares plugin '$($property.Name)', which marketplace.json does not."
    }
    $pluginDomains[$property.Name] = @($property.Value)
}
foreach ($name in $declared) {
    if (-not $pluginDomains.ContainsKey($name)) {
        throw "marketplace.json declares plugin '$name', which payloads.json assigns no domains."
    }
}
foreach ($plugin in $plugins) {
    if (-not $pluginDomains.ContainsKey($plugin.Name)) {
        throw "plugins/$($plugin.Name) exists but is declared nowhere; add it to marketplace.json and payloads.json."
    }
    foreach ($domain in $pluginDomains[$plugin.Name]) {
        if (-not (Test-Path (Join-Path $standardsDir $domain))) {
            throw "plugin '$($plugin.Name)' claims domain '$domain', which is not in standards/."
        }
    }
}
$unshipped = @($docs | ForEach-Object { ($_ -split '/')[1] } | Sort-Object -Unique |
    Where-Object { $domain = $_; -not (@($pluginDomains.Values | ForEach-Object { $_ }) -contains $domain) })
if ($unshipped) {
    throw "standards domain(s) '$($unshipped -join ', ')' are in no plugin, so a clone cannot install them."
}

# relative path -> LF-normalized content
$generated = [ordered]@{}

foreach ($skill in $skills.Values) {
    $generated[".claude/skills/$($skill.Name)/SKILL.md"] =
        if ($skill.Doc) { $skill.Body } else { Get-StubBody $skill.Name $skill.Description }
}

foreach ($plugin in $plugins) {
    $mine = @($docs | Where-Object {
        $pluginDomains[$plugin.Name] -contains (($_ -split '/')[1])
    })
    foreach ($doc in $mine) {
        $generated["plugins/$($plugin.Name)/$doc"] = Read-Lf (Join-Path $repoRoot $doc)
        $owner = @($skills.Values | Where-Object { $_.Doc -eq $doc })[0]
        # skills/<name>/SKILL.md -> the plugin's own copy of the tree, two levels up.
        $generated["plugins/$($plugin.Name)/skills/$($owner.Name)/SKILL.md"] =
            (Rewrite-ForPlugin $owner.Body)
    }
}

# One index per domain, generated from the tree so it cannot drift from it.
$domains = @($docs | ForEach-Object { ($_ -split '/')[1] } | Sort-Object -Unique)
foreach ($domain in $domains) {
    $rows = @()
    # Domain-root docs first, then each subfolder as a block. A plain path sort interleaves them.
    $inDomain = @($docs | Where-Object { $_ -like "standards/$domain/*" } | Sort-Object `
        @{ Expression = { $withinDomain = $_ -replace "^standards/$domain/", ''; if ($withinDomain -match '/') { $withinDomain.Substring(0, $withinDomain.LastIndexOf('/')) } else { '' } } },
        @{ Expression = { $_ } })
    foreach ($doc in $inDomain) {
        $owner = @($skills.Values | Where-Object { $_.Doc -eq $doc })[0]
        $heading = @((Read-Lf (Join-Path $repoRoot $doc)) -split "`n" |
            Where-Object { $_ -match '^#\s+' } | Select-Object -First 1)
        $title = ($heading[0] -replace '^#\s+', '')
        $relative = ($doc -replace "^standards/$domain/", '')
        $rows += "| [``$relative``]($relative) | $title | ``$($owner.Name)`` |"
    }
    $lines = @(
        "# $domain standards",
        '',
        'Generated by `.agents/sync-generated.ps1` from the tree. Do not edit.',
        '',
        '| Doc | Covers | Skill |',
        '|---|---|---|'
    ) + $rows + @('')
    $generated["standards/$domain/$INDEX_NAME"] = ($lines -join "`n")
}

$stale = @(); $written = @(); $unchanged = @()

foreach ($relative in $generated.Keys) {
    $target  = Join-Path $repoRoot $relative
    $body    = $generated[$relative]
    $current = $null
    if (Test-Path $target) { $current = Read-Lf $target }
    if ($current -eq $body) { $unchanged += $relative; continue }
    $stale += $relative
    if ($Check) { continue }
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $target) | Out-Null
    [System.IO.File]::WriteAllText($target, ($body -replace "`n", "`r`n"), $utf8NoBom)
    $written += $relative
}

# Prune every generated artefact this run did not just author. Membership of $generated is the test, not
# "is there still a skill by this name" - a doc moving between plugins leaves a stale copy a name check
# would happily keep, and a consumer would then install two conflicting copies of one rule.
$pruned = @()
$generatedRoots = @(Join-Path $repoRoot '.claude/skills')
foreach ($plugin in $plugins) {
    $generatedRoots += (Join-Path $plugin.FullName 'skills')
    $generatedRoots += (Join-Path $plugin.FullName 'standards')
}
foreach ($root in $generatedRoots) {
    if (-not (Test-Path $root)) { continue }
    foreach ($file in Get-ChildItem -Path $root -Recurse -File) {
        $relative = To-RepoRelative $file.FullName $repoRoot
        if ($generated.Contains($relative)) { continue }
        $pruned += $relative
        if (-not $Check) { Remove-Item -Force $file.FullName }
    }
}
if (-not $Check) {
    foreach ($root in $generatedRoots) {
        if (-not (Test-Path $root)) { continue }
        Get-ChildItem -Path $root -Recurse -Directory |
            Sort-Object { $_.FullName.Length } -Descending |
            Where-Object { -not (Get-ChildItem -Path $_.FullName -Recurse -File) } |
            ForEach-Object { Remove-Item -Recurse -Force $_.FullName }
    }
}

$routed = @($skills.Values | Where-Object { $_.Doc }).Count
$utilities = $skills.Count - $routed

if ($Check) {
    if ($stale.Count -or $pruned.Count) {
        Write-Host "STALE: $($stale.Count) generated file(s), $($pruned.Count) orphan(s). Run: pwsh .agents/sync-generated.ps1"
        foreach ($item in ($stale + $pruned)) { Write-Host "  $item" }
        exit 1
    }
    Write-Host "generated files are current: $($unchanged.Count) checked ($routed standards, $utilities utilities, $($docs.Count) docs)"
    exit 0
}

Write-Host "generated: $($generated.Count) file(s) from $routed standards, $utilities utilities and $($docs.Count) docs | $($written.Count) written | $($unchanged.Count) unchanged | $($pruned.Count) pruned"
foreach ($item in $written) { Write-Host "  written: $item" }
foreach ($item in $pruned)  { Write-Host "  pruned:  $item" }
