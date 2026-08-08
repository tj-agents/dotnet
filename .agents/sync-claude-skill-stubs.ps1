#!/usr/bin/env pwsh
# Regenerates the Claude Code compatibility stubs under .claude/skills/ from the
# canonical agent-agnostic skills in .agents/skills/. Claude Code only discovers
# skills in .claude/skills/, so every canonical skill needs a one-line stub that
# points Claude at the real instructions. Run after adding/removing a skill.
#   pwsh .agents/sync-claude-skill-stubs.ps1

$ErrorActionPreference = 'Stop'
$repoRoot   = Split-Path -Parent $PSScriptRoot
$canonical  = Join-Path $repoRoot '.agents/skills'
$stubRoot   = Join-Path $repoRoot '.claude/skills'
$utf8NoBom  = New-Object System.Text.UTF8Encoding($false)

function Stub-Body([string]$name) {
@"
---
name: $name
description: Compatibility stub for Claude Code. The canonical skill lives in .agents/skills/$name/SKILL.md.
---

# $name

This is a Claude Code compatibility stub. Do not edit skill instructions here.

Read and follow the canonical agent-agnostic skill at ../../../.agents/skills/$name/SKILL.md.

"@ -replace "`r`n", "`n"
}

$names = Get-ChildItem -Path $canonical -Directory |
    Where-Object { Test-Path (Join-Path $_.FullName 'SKILL.md') } |
    Select-Object -ExpandProperty Name | Sort-Object

$written = @(); $unchanged = @(); $pruned = @()

foreach ($name in $names) {
    $dir  = Join-Path $stubRoot $name
    $file = Join-Path $dir 'SKILL.md'
    $body = Stub-Body $name
    $current = if (Test-Path $file) { [System.IO.File]::ReadAllText($file) -replace "`r`n", "`n" } else { $null }
    if ($current -ne $body) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
        [System.IO.File]::WriteAllText($file, ($body -replace "`n", "`r`n"), $utf8NoBom)
        $written += $name
    } else {
        $unchanged += $name
    }
}

# Prune orphan stubs whose canonical skill no longer exists (stub files only).
if (Test-Path $stubRoot) {
    foreach ($d in Get-ChildItem -Path $stubRoot -Directory) {
        if ($names -notcontains $d.Name) {
            $sf = Join-Path $d.FullName 'SKILL.md'
            if ((Test-Path $sf) -and ((Get-Content -Raw $sf) -match 'Compatibility stub for Claude Code')) {
                Remove-Item -Recurse -Force $d.FullName
                $pruned += $d.Name
            }
        }
    }
}

Write-Host "stubs: $($names.Count) canonical | $($written.Count) written | $($unchanged.Count) unchanged | $($pruned.Count) pruned"
if ($written.Count) { Write-Host ("  written:   " + ($written -join ', ')) }
if ($pruned.Count)  { Write-Host ("  pruned:    " + ($pruned  -join ', ')) }
