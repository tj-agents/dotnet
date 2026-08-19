<#
.SYNOPSIS
Deploy the canonical UTILITY skills to ~/.agents/skills and ~/.claude/skills, and every repo's standards
tree to ~/.agents/standards, as directory junctions. Standards ROUTERS are not deployed here — plugins
deliver those, and the plugin name is what keeps two repos' mirrored pairs apart.

.DESCRIPTION
Replaces copy-deployment with links so a `git pull` IS the deployment and drift is structurally
impossible. Junctions are per-skill because skill discovery is <root>/skills/*/SKILL.md and does not
recurse, and because several source repos must land in one namespace.

Utility skills are junctioned per SKILL, flat, because discovery is <root>/skills/*/SKILL.md and does not
recurse. They own no doc, ship in no plugin, and their names are unique across the source repos.

Routers are NOT junctioned. Flat delivery demands globally unique names, but a router and its
counterpart in another repo share a name deliberately - `persistence` here and `persistence` in
agent-standards are the generic rule and the product's roster of the same topic. Forcing them apart used
to mean prefixing one of them; plugins do it properly, since `dotnet-standards:persistence` and
`dotnet:persistence` are already distinct. So the prefix is gone and this script stops competing with
the plugin for the same folder name.

Standards trees ARE still junctioned, per SOURCE REPO, at ~/.agents/standards/<repo>/<domain>. That
namespace never had the problem: it is repo-scoped, so two repos owning the same domain name cannot
shadow each other - and it must stay that way. Flattening it once made agent-standards' persistence doc
resolve to dotagents' generic one, right path, wrong repo, no error. A plugin carries its own copy of
the domains it ships, so this deployment is for reading and grepping from a clone, not for resolution.

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
        (Join-Path $HOME 'source/repos/react-agents/.agents/skills'),
        (Join-Path $HOME 'source/repos/agent-standards/.agents/skills')
    ),
    [string[]]$StandardsRoot = @(
        (Join-Path $HOME 'source/repos/dotagents/standards'),
        (Join-Path $HOME 'source/repos/react-agents/standards'),
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

# A ROUTER owns a doc under `standards/` and is delivered by its plugin, which namespaces it -
# `dotnet:persistence` and `dotnet-standards:persistence` coexist. Junctioning routers into one flat
# root cannot: the two repos' mirrored pairs share a name on purpose, and 16 of them collide. That
# collision is the only reason the local names ever carried a `concertable-` prefix, so the prefix went
# with this. A UTILITY owns no doc, ships in no plugin, and is still delivered from this clone.
# The discriminator is the same one sync-generated.ps1 uses: a backticked `standards/....md` path.
function Test-IsRouter([string]$SkillDir) {
    $skill = Join-Path $SkillDir 'SKILL.md'
    if (-not (Test-Path -LiteralPath $skill)) { return $false }
    return (Get-Content -LiteralPath $skill -Raw -Encoding utf8) -match '`standards/[^`]+\.md`'
}

$sources = @{}
$routers = 0
foreach ($root in $SourceRoot) {
    if (-not (Test-Path -LiteralPath $root)) { Write-Warning "source root missing: $root"; continue }
    foreach ($dir in Get-ChildItem -LiteralPath $root -Directory) {
        if (Test-IsRouter $dir.FullName) { $routers++; continue }
        if ($sources.ContainsKey($dir.Name)) {
            throw "utility skill '$($dir.Name)' is declared by two source roots: $($sources[$dir.Name]) and $($dir.FullName)"
        }
        $sources[$dir.Name] = $dir.FullName
    }
}
Write-Host "utility skills to deploy: $($sources.Count) (skipped $routers router(s) - plugins deliver those)" -ForegroundColor Cyan

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

    # A junction we no longer own is a skill this script deployed and has stopped deploying - every
    # router, after the cut to plugin delivery. Left in place it keeps resolving to a stale clone under
    # its old name, which is worse than absent: the reader gets an answer and cannot tell it is the one
    # the plugin was meant to replace. A real directory is never touched; it is content with no source.
    $pruned = 0
    $orphans = @()
    if (Test-Path -LiteralPath $targetRoot) {
        foreach ($dir in Get-ChildItem -LiteralPath $targetRoot -Directory) {
            if ($sources.ContainsKey($dir.Name)) { continue }
            if ($dir.LinkType -eq 'Junction') {
                if ($PSCmdlet.ShouldProcess($dir.FullName, 'remove junction we no longer deploy')) {
                    Remove-Item -LiteralPath $dir.FullName -Force -Recurse -Confirm:$false
                }
                $pruned++
                continue
            }
            $orphans += $dir.Name
        }
    }
    Write-Host "$targetRoot : linked=$linked replaced=$replaced already-correct=$kept pruned=$pruned" -ForegroundColor Green
    if ($orphans) { Write-Warning "orphaned real directories (no canonical source, left in place): $($orphans -join ', ')" }
}

# repo-scoped key -> source tree. The repo name comes from the folder holding `standards`, so the deployed
# path states which repo a doc came from and two repos owning the same domain name cannot shadow each other.
$domains = [ordered]@{}
foreach ($root in $StandardsRoot) {
    if (-not (Test-Path -LiteralPath $root)) { Write-Warning "standards root missing: $root"; continue }
    $repo = Split-Path -Leaf (Split-Path -Parent (Resolve-Path -LiteralPath $root).ProviderPath)
    foreach ($dir in Get-ChildItem -LiteralPath $root -Directory) {
        $key = "$repo/$($dir.Name)"
        if ($domains.Contains($key)) {
            throw "standards path '$key' is declared twice: $($domains[$key]) and $($dir.FullName)"
        }
        $domains[$key] = $dir.FullName
    }
}

if ($domains.Count) {
    if (-not (Test-Path -LiteralPath $StandardsTarget)) {
        if ($PSCmdlet.ShouldProcess($StandardsTarget, 'create standards root')) {
            New-Item -ItemType Directory -Path $StandardsTarget -Force | Out-Null
        }
    }
    $linked = $replaced = $kept = 0
    foreach ($name in @($domains.Keys) | Sort-Object) {
        $src = $domains[$name]
        $dst = Join-Path $StandardsTarget $name
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $dst) | Out-Null
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
