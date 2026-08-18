<#
.SYNOPSIS
Deploy canonical agent skills to ~/.agents/skills and ~/.claude/skills, and the standards trees they
route to under ~/.agents/standards, all as directory junctions.

.DESCRIPTION
Replaces copy-deployment with links so a `git pull` IS the deployment and drift is structurally
impossible. Junctions are per-skill because skill discovery is <root>/skills/*/SKILL.md and does not
recurse, and because several source repos must land in one namespace.

The standards trees are junctioned per DOMAIN for the same reason the skills are per skill: several
repos share one deployed namespace, so `standards/process` (agent-standards) and `standards/dotnet`
(here) must both land under ~/.agents/standards without either repo owning the parent. A domain
declared by two repos is a collision and is refused, exactly as a duplicate skill name is.

Deploying the trees is not optional. A skill is now a router whose body names its doc's path, so a
skill junctioned without its tree points at a file the reading session cannot open.

Refuses to replace a target directory holding content that is neither identical to canonical nor a
generated stub - that is an edit made against the installed copy and never committed, and deleting it
destroys the only copy. Two such edits were found and recovered on 2026-08-17 (dotagents c153697).

.EXAMPLE
./deploy-skills.ps1 -WhatIf
./deploy-skills.ps1
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [string[]]$SourceRoot = @(
        (Join-Path $HOME 'source/repos/dotagents/.agents/skills'),
        (Join-Path $HOME 'source/repos/agent-standards/.agents/skills')
    ),
    [string[]]$StandardsRoot = @(
        (Join-Path $HOME 'source/repos/dotagents/standards'),
        (Join-Path $HOME 'source/repos/agent-standards/standards')
    ),
    [string]$StandardsTarget = (Join-Path $HOME '.agents/standards'),
    [string[]]$Target = @(
        (Join-Path $HOME '.agents/skills'),
        (Join-Path $HOME '.claude/skills')
    ),
    [switch]$Force
)

$ErrorActionPreference = 'Stop'
$STUB_MARKER = 'compatibility stub'

function Get-NormalizedText([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $null }
    ((Get-Content -LiteralPath $Path -Raw -Encoding utf8) -replace "`r`n", "`n").Trim()
}

function Test-SafeToReplace([string]$TargetDir, [string]$SourceDir) {
    $targetSkill = Join-Path $TargetDir 'SKILL.md'
    $text = Get-NormalizedText $targetSkill
    if ($null -eq $text) { return @{ Safe = $true; Why = 'no SKILL.md' } }
    if ($text -like "*$STUB_MARKER*") { return @{ Safe = $true; Why = 'generated stub' } }
    if ($text -eq (Get-NormalizedText (Join-Path $SourceDir 'SKILL.md'))) {
        return @{ Safe = $true; Why = 'identical to canonical' }
    }
    @{ Safe = $false; Why = 'DIVERGED from canonical - commit it to its source repo first' }
}

$sources = @{}
foreach ($root in $SourceRoot) {
    if (-not (Test-Path -LiteralPath $root)) { Write-Warning "source root missing: $root"; continue }
    foreach ($dir in Get-ChildItem -LiteralPath $root -Directory) {
        if ($sources.ContainsKey($dir.Name)) {
            throw "skill '$($dir.Name)' is declared by two source roots: $($sources[$dir.Name]) and $($dir.FullName)"
        }
        $sources[$dir.Name] = $dir.FullName
    }
}
Write-Host "canonical skills discovered: $($sources.Count)" -ForegroundColor Cyan

$refused = @()
foreach ($targetRoot in $Target) {
    if (-not (Test-Path -LiteralPath $targetRoot)) {
        if ($PSCmdlet.ShouldProcess($targetRoot, 'create target root')) {
            New-Item -ItemType Directory -Path $targetRoot -Force | Out-Null
        }
    }
    $linked = $replaced = $kept = 0
    foreach ($name in $sources.Keys | Sort-Object) {
        $src = $sources[$name]
        $dst = Join-Path $targetRoot $name
        $existing = Get-Item -LiteralPath $dst -ErrorAction SilentlyContinue

        if ($existing -and $existing.LinkType -eq 'Junction') {
            if ($existing.Target -contains $src) { $kept++; continue }
            if ($PSCmdlet.ShouldProcess($dst, "repoint junction -> $src")) {
                Remove-Item -LiteralPath $dst -Force -Recurse -Confirm:$false
                New-Item -ItemType Junction -Path $dst -Target $src | Out-Null
            }
            $replaced++; continue
        }

        if ($existing) {
            $check = Test-SafeToReplace $dst $src
            if (-not ($check.Safe -or $Force)) {
                $refused += "$dst - $($check.Why)"
                continue
            }
            if ($PSCmdlet.ShouldProcess($dst, "replace directory ($($check.Why)) with junction -> $src")) {
                Remove-Item -LiteralPath $dst -Force -Recurse -Confirm:$false
                New-Item -ItemType Junction -Path $dst -Target $src | Out-Null
            }
            $replaced++; continue
        }

        if ($PSCmdlet.ShouldProcess($dst, "link -> $src")) {
            New-Item -ItemType Junction -Path $dst -Target $src | Out-Null
        }
        $linked++
    }

    $orphans = @()
    if (Test-Path -LiteralPath $targetRoot) {
        $orphans = Get-ChildItem -LiteralPath $targetRoot -Directory |
            Where-Object { -not $sources.ContainsKey($_.Name) } |
            Select-Object -ExpandProperty Name
    }
    Write-Host "$targetRoot : linked=$linked replaced=$replaced already-correct=$kept" -ForegroundColor Green
    if ($orphans) { Write-Warning "orphaned (no canonical source, left in place): $($orphans -join ', ')" }
}

$domains = @{}
foreach ($root in $StandardsRoot) {
    if (-not (Test-Path -LiteralPath $root)) { Write-Warning "standards root missing: $root"; continue }
    foreach ($dir in Get-ChildItem -LiteralPath $root -Directory) {
        if ($domains.ContainsKey($dir.Name)) {
            throw "standards domain '$($dir.Name)' is declared by two source roots: $($domains[$dir.Name]) and $($dir.FullName)"
        }
        $domains[$dir.Name] = $dir.FullName
    }
}

if ($domains.Count) {
    if (-not (Test-Path -LiteralPath $StandardsTarget)) {
        if ($PSCmdlet.ShouldProcess($StandardsTarget, 'create standards root')) {
            New-Item -ItemType Directory -Path $StandardsTarget -Force | Out-Null
        }
    }
    $linked = $replaced = $kept = 0
    foreach ($name in $domains.Keys | Sort-Object) {
        $src = $domains[$name]
        $dst = Join-Path $StandardsTarget $name
        $existing = Get-Item -LiteralPath $dst -ErrorAction SilentlyContinue

        if ($existing -and $existing.LinkType -eq 'Junction') {
            if ($existing.Target -contains $src) { $kept++; continue }
            if ($PSCmdlet.ShouldProcess($dst, "repoint junction -> $src")) {
                Remove-Item -LiteralPath $dst -Force -Recurse -Confirm:$false
                New-Item -ItemType Junction -Path $dst -Target $src | Out-Null
            }
            $replaced++; continue
        }

        # A real directory here is not a stale link but authored content with no source repo, so it is
        # never silently replaced.
        if ($existing) {
            $refused += "$dst - a real directory, not a junction; move its content into a standards repo first"
            continue
        }

        if ($PSCmdlet.ShouldProcess($dst, "link -> $src")) {
            New-Item -ItemType Junction -Path $dst -Target $src | Out-Null
        }
        $linked++
    }
    Write-Host "$StandardsTarget : linked=$linked replaced=$replaced already-correct=$kept ($($domains.Count) domains)" -ForegroundColor Green
}

if ($refused) {
    Write-Host ''
    Write-Warning "REFUSED $($refused.Count) target(s) - their content exists nowhere else:"
    $refused | ForEach-Object { Write-Warning "  $_" }
    Write-Warning 'Commit each into its source repo, then re-run. -Force overrides and DISCARDS them.'
    exit 1
}
