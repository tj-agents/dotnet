#!/usr/bin/env pwsh
<#
Regenerates everything in this repo that is derived from `.agents/`.

Two kinds of skill live here, told apart by ONE authored fact - a `domain:` field in front matter:

  a STANDARD   declares `domain:`, and its SKILL.md body IS the standard. There is no separate doc:
               `@`-import only expands inside CLAUDE.md/AGENTS.md, never inside a SKILL.md, so a skill
               pointing at a doc could only ever be a pointer - costing a guaranteed Read tool call for
               content the invocation was always going to need. The domain decides which plugin ships it.

  a UTILITY    declares no `domain:` - a procedure the agent runs (`sync`, `worktree`, `recents`). It is
               machine tooling, not a standard, so it ships in no plugin and no domain claims it.

A generic standard and its Concertable counterpart pair by SKILL NAME and are told apart by PLUGIN
NAMESPACE - `dotnet-standards:persistence` here, `dotnet:persistence` in Concertable/agent-standards.
Nothing pairs by file path any more; the skill name already carried that fact.

Generated:
  .claude/skills/<name>/SKILL.md   for a harness opened on THIS repo. A standard is copied verbatim; a
                                   utility gets a stub pointing at canonical, so its body is not
                                   duplicated.
  SKILLS.md                        the catalogue: skill -> what it covers -> owning plugin. Answers "did
                                   I write this rule down, and which skill owns it" without opening
                                   anything, which is what the per-domain standards INDEX used to answer.
  plugins/<p>/skills/...             verbatim copy of each standard whose domain that plugin claims. An
                                   installed plugin is only its own subtree, and a plugin cannot
                                   reference anything outside its root, so the payload is a full copy.
  .agents/plugins/marketplace.json and .claude-plugin/marketplace.json are authored separately because
                                   the two harnesses require different schemas. Each plugin carries both
                                   .claude-plugin/plugin.json and .codex-plugin/plugin.json.

Plugins carry the domains `.agents/plugins/payloads.json` assigns them, so a consumer installs per
stack rather than receiving every corpus. The write-time router hook lives in
`Concertable/agent-standards` and ships in its `agent-process` plugin, so a project wanting enforcement
installs that too.

Refuses to write when the skill namespace and the payload split disagree: a skill whose domain no plugin
ships, or a plugin claiming a domain no skill declares. Two structures that can drift is exactly how 754
lines of frontend law ended up with zero inbound links.

  pwsh .agents/sync-generated.ps1
  pwsh .agents/sync-generated.ps1 -Check   # verify only; non-zero exit if anything is stale
#>

[CmdletBinding()]
param([switch]$Check)

$ErrorActionPreference = 'Stop'

# Windows PowerShell 5.1 reads a BOM-less .ps1 as the system ANSI codepage rather than UTF-8, so a
# non-ASCII literal in THIS file arrives already mojibake and is written straight into the generated
# output - where it is indistinguishable from content that was always meant to look that way. Text read
# from other files is safe (ReadAllText decodes UTF-8); only the script's own literals are exposed, so
# the script keeps them ASCII and proves it here rather than relying on nobody typing an em-dash.
$ownBytes = [System.IO.File]::ReadAllBytes($PSCommandPath)
if (@($ownBytes | Where-Object { $_ -gt 127 }).Count) {
    throw "sync-generated.ps1 contains a non-ASCII byte; PowerShell 5.1 reads this file as ANSI and would emit mojibake. Keep the script's own literals ASCII."
}

$repoRoot     = Split-Path -Parent $PSScriptRoot
$canonical    = Join-Path $repoRoot '.agents/skills'
$manifest     = Join-Path $repoRoot '.agents/plugins/marketplace.json'
$claudeManifest = Join-Path $repoRoot '.claude-plugin/marketplace.json'
$payloadsFile = Join-Path $repoRoot '.agents/plugins/payloads.json'
$utf8NoBom    = New-Object System.Text.UTF8Encoding($false)

$CATALOGUE   = 'SKILLS.md'
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

# The one authored fact that classifies a skill. Absent means a utility, which ships in no plugin.
function Get-OptionalFrontMatterField([string]$text, [string]$field) {
    $match = [regex]::Match($text, "(?s)\A---\n.*?^${field}:[ \t]*(.+?)\n(?:[a-zA-Z-]+:|---)", 'Multiline')
    if (-not $match.Success) { return $null }
    return $match.Groups[1].Value.Trim()
}

# The catalogue row's "Covers" column. A standard's body opens with its own title, which says what the
# rule is about in far fewer words than the trigger-carrying description. Only a standard is catalogued,
# so only a standard needs one; a utility may go straight into its procedure.
function Get-Title([string]$text) {
    $heading = @(($text -replace "(?s)\A---\n.*?\n---\n", '') -split "`n" |
        Where-Object { $_ -match '^#\s+' } | Select-Object -First 1)
    if (-not $heading) { return $null }
    return ($heading[0] -replace '^#\s+', '')
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

function Sort-Ordinal([string[]]$values) {
    $list = [System.Collections.Generic.List[string]]::new()
    foreach ($value in $values) { $list.Add($value) }
    $list.Sort([System.StringComparer]::Ordinal)
    return $list.ToArray()
}

# Skills stay flat: discovery is <root>/skills/*/SKILL.md and does not recurse.
$skillDirs = @(Get-ChildItem -Path $canonical -Directory |
    Where-Object { Test-Path (Join-Path $_.FullName 'SKILL.md') } | Sort-Object Name)
if (-not $skillDirs) { throw "No canonical skills found under .agents/skills." }

$skills = [ordered]@{}
foreach ($dir in $skillDirs) {
    $text = Read-Lf (Join-Path $dir.FullName 'SKILL.md')
    $domain = Get-OptionalFrontMatterField $text 'domain'
    $title = Get-Title $text
    if ($domain -and -not $title) {
        throw "$($dir.Name)/SKILL.md declares a domain but has no ``# `` heading, so the catalogue has nothing to show."
    }
    $skills[$dir.Name] = [pscustomobject]@{
        Name        = $dir.Name
        Body        = $text
        Description = Get-CanonicalDescription $text $dir.Name
        Domain      = $domain
        Title       = $title
    }
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
}

# The skill namespace and the payload split are the only two structures now, so they reconcile directly
# against each other - there is no doc tree in between for either to drift from.
$claimed = @($pluginDomains.Values | ForEach-Object { $_ } | Sort-Object -Unique)
$declaredDomains = @($skills.Values | Where-Object { $_.Domain } |
    Select-Object -ExpandProperty Domain | Sort-Object -Unique)
$problems = @()
foreach ($domain in $declaredDomains) {
    if ($claimed -notcontains $domain) {
        $owners = @($skills.Values | Where-Object { $_.Domain -eq $domain } | Select-Object -ExpandProperty Name)
        $problems += "domain '$domain' (declared by $($owners -join ', ')) is in no plugin, so a clone cannot install it."
    }
}
foreach ($domain in $claimed) {
    if ($declaredDomains -notcontains $domain) {
        $problems += "a plugin claims domain '$domain', which no skill declares, so it would ship empty."
    }
}
if ($problems) {
    Write-Host "The skill namespace and the plugin payloads disagree:"
    foreach ($problem in $problems) { Write-Host "  $problem" }
    exit 1
}

# relative path -> LF-normalized content
$generated = [ordered]@{}

foreach ($skill in $skills.Values) {
    $generated[".claude/skills/$($skill.Name)/SKILL.md"] =
        if ($skill.Domain) { $skill.Body } else { Get-StubBody $skill.Name $skill.Description }
}

foreach ($plugin in $plugins) {
    $mine = @($skills.Values | Where-Object { $_.Domain -and $pluginDomains[$plugin.Name] -contains $_.Domain })
    foreach ($skill in $mine) {
        $generated["plugins/$($plugin.Name)/skills/$($skill.Name)/SKILL.md"] = $skill.Body
    }
}

# The catalogue, generated from the skill tree so it cannot drift from it - which the hand-maintained
# table its predecessor replaced could and did.
#
# Sorted ORDINALLY, not with Sort-Object: its comparison is culture-aware, and cultures disagree about
# punctuation, so a generated file would otherwise differ by platform and CI would call a locally current
# tree stale. A generated file that depends on the generating machine's culture is not generated.
$pluginFor = @{}
foreach ($plugin in $plugins) {
    foreach ($domain in $pluginDomains[$plugin.Name]) { $pluginFor[$domain] = $plugin.Name }
}

$lines = [System.Collections.Generic.List[string]]::new()
$lines.Add('# Skill catalogue')
$lines.Add('')
$lines.Add('Generated by `.agents/sync-generated.ps1` from `.agents/skills/`. Do not edit.')
$lines.Add('')
$lines.Add('Each standard is authored once, in its own `SKILL.md`. A counterpart of the same name in another')
$lines.Add('standards repo is a different plugin, not a different path. Utility skills are not standards and')
$lines.Add('are not catalogued here; `deploy-skills.ps1` is their roster.')
foreach ($domain in (Sort-Ordinal $declaredDomains)) {
    $lines.Add('')
    $lines.Add("## $domain")
    $lines.Add('')
    $lines.Add('| Skill | Covers | Plugin |')
    $lines.Add('|---|---|---|')
    foreach ($name in (Sort-Ordinal @($skills.Values | Where-Object { $_.Domain -eq $domain } |
            Select-Object -ExpandProperty Name))) {
        $lines.Add("| ``$name`` | $($skills[$name].Title) | ``$($pluginFor[$domain])`` |")
    }
}
$lines.Add('')
$generated[$CATALOGUE] = ($lines -join "`n")

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
# "is there still a skill by this name" - a skill moving between plugins leaves a stale copy a name check
# would happily keep, and a consumer would then install two conflicting copies of one rule. `standards`
# stays in the pruned roots so the payload copies of the retired doc tree are actually removed.
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
        if (-not (Get-ChildItem -Path $root -Recurse -File)) { Remove-Item -Recurse -Force $root }
    }
}

$standards = @($skills.Values | Where-Object { $_.Domain }).Count
$utilityCount = $skills.Count - $standards

if ($Check) {
    if ($stale.Count -or $pruned.Count) {
        Write-Host "STALE: $($stale.Count) generated file(s), $($pruned.Count) orphan(s). Run: pwsh .agents/sync-generated.ps1"
        foreach ($item in ($stale + $pruned)) { Write-Host "  $item" }
        exit 1
    }
    Write-Host "generated files are current: $($unchanged.Count) checked ($standards standards, $utilityCount utilities)"
    exit 0
}

Write-Host "generated: $($generated.Count) file(s) from $standards standards and $utilityCount utilities | $($written.Count) written | $($unchanged.Count) unchanged | $($pruned.Count) pruned"
foreach ($item in $written) { Write-Host "  written: $item" }
foreach ($item in $pruned)  { Write-Host "  pruned:  $item" }
