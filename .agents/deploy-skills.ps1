<#
.SYNOPSIS
Deploy canonical agent skills to ~/.agents/skills and ~/.claude/skills as directory junctions.

.DESCRIPTION
Replaces copy-deployment with links so a `git pull` IS the deployment and drift is structurally
impossible. Junctions are per-skill because skill discovery is <root>/skills/*/SKILL.md and does not
recurse, and because several source repos must land in one namespace.

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

if ($refused) {
    Write-Host ''
    Write-Warning "REFUSED $($refused.Count) target(s) - their content exists nowhere else:"
    $refused | ForEach-Object { Write-Warning "  $_" }
    Write-Warning 'Commit each into its source repo, then re-run. -Force overrides and DISCARDS them.'
    exit 1
}
