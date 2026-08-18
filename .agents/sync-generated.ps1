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

# relative path -> LF-normalized content
$generated = [ordered]@{}

foreach ($skill in $skills.Values) {
    $generated[".claude/skills/$($skill.Name)/SKILL.md"] =
        if ($skill.Doc) { $skill.Body } else { Get-StubBody $skill.Name $skill.Description }
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

# Prune generated skill directories whose canonical skill is gone.
$pruned = @()
$stubRoot = Join-Path $repoRoot '.claude/skills'
if (Test-Path $stubRoot) {
    foreach ($dir in Get-ChildItem -Path $stubRoot -Directory) {
        if ($skills.Contains($dir.Name)) { continue }
        $pruned += (To-RepoRelative $dir.FullName $repoRoot)
        if (-not $Check) { Remove-Item -Recurse -Force $dir.FullName }
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
