<#
.SYNOPSIS
Deploy the canonical UTILITY skills to ~/.agents/skills and ~/.claude/skills as directory junctions, and
unlink the retired ~/.agents/standards tree. STANDARDS are not deployed here — plugins deliver those, and
the plugin name is what keeps two repos' same-named pairs apart.

.DESCRIPTION
Replaces copy-deployment with links so a `git pull` IS the deployment and drift is structurally
impossible. Junctions are per-skill because skill discovery is <root>/skills/*/SKILL.md and does not
recurse, and because several source repos must land in one namespace.

Utility skills are junctioned per SKILL, flat, for that same reason. They declare no domain, ship in no
plugin, and their names are unique across the source repos.

Standards are NOT junctioned. Flat delivery demands globally unique names, but a standard and its
counterpart in another repo share a name deliberately - `persistence` here and `persistence` in
agent-standards are the generic rule and the product's roster of the same topic. Forcing them apart used
to mean prefixing one of them; plugins do it properly, since `dotnet-standards:persistence` and
`dotnet:persistence` are already distinct. So the prefix is gone and this script stops competing with
the plugin for the same folder name.

~/.agents/standards is now PRUNED rather than populated. Each standard is authored inside its own
SKILL.md, so no repo has a standards tree left to junction, and a junction left behind would dangle into
a clone whose tree is gone - or worse, keep resolving against one that has not pulled yet, which is an
answer the reader cannot tell apart from a current one. A real directory there is authored content with
no source repo and is never touched.

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

# A STANDARD declares a domain and is delivered by its plugin, which namespaces it - `dotnet:persistence`
# and `dotnet-standards:persistence` coexist. Junctioning standards into one flat root cannot: the two
# repos' pairs share a name on purpose, and 16 of them collide. That collision is the only reason the
# local names ever carried a `concertable-` prefix, so the prefix went with this. A UTILITY declares no
# domain, ships in no plugin, and is still delivered from this clone. The discriminator is the same one
# sync-generated.ps1 uses: a `domain:` field in front matter.
function Test-IsStandard([string]$SkillDir) {
    $skill = Join-Path $SkillDir 'SKILL.md'
    if (-not (Test-Path -LiteralPath $skill)) { return $false }
    $text = (Get-Content -LiteralPath $skill -Raw -Encoding utf8) -replace "`r`n", "`n"
    # Matched against the front matter alone, not the whole file - a body line opening `domain:` would
    # otherwise classify a utility as a standard and silently stop deploying it.
    $front = [regex]::Match($text, "(?s)\A---\n(.*?)\n---\n")
    if (-not $front.Success) { return $false }
    return [regex]::IsMatch($front.Groups[1].Value, "^domain:[ \t]*\S", 'Multiline')
}

$sources = @{}
$standards = 0
foreach ($root in $SourceRoot) {
    if (-not (Test-Path -LiteralPath $root)) { Write-Warning "source root missing: $root"; continue }
    foreach ($dir in Get-ChildItem -LiteralPath $root -Directory) {
        if (Test-IsStandard $dir.FullName) { $standards++; continue }
        if ($sources.ContainsKey($dir.Name)) {
            throw "utility skill '$($dir.Name)' is declared by two source roots: $($sources[$dir.Name]) and $($dir.FullName)"
        }
        $sources[$dir.Name] = $dir.FullName
    }
}
Write-Host "utility skills to deploy: $($sources.Count) (skipped $standards standard(s) - plugins deliver those)" -ForegroundColor Cyan

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
    # standard, after the cut to plugin delivery. Left in place it keeps resolving to a stale clone under
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

# The retired standards tree. Nothing junctions into it any more - each standard is authored inside its
# own SKILL.md and shipped by its plugin - so every junction this script previously created here now
# points at a tree that is gone, or at one that is merely stale until that clone pulls. Both answer a
# reader who cannot tell the difference, so they are removed rather than left. A real directory is
# authored content with no source repo and is left alone.
#
# Walked as the exact two levels it was deployed as, <repo>/<domain>, rather than with -Recurse: recursion
# descends THROUGH a junction into the tree it points at, so a single stale link would enumerate - and
# report on - a whole source clone.
if (Test-Path -LiteralPath $StandardsTarget) {
    $unlinked = 0
    $leftovers = @()
    foreach ($repoDir in Get-ChildItem -LiteralPath $StandardsTarget -Directory -Force) {
        if ($repoDir.LinkType -eq 'Junction') {
            if ($PSCmdlet.ShouldProcess($repoDir.FullName, 'remove junction into the retired standards tree')) {
                Remove-Item -LiteralPath $repoDir.FullName -Force -Recurse -Confirm:$false
            }
            $unlinked++
            continue
        }
        foreach ($domainDir in Get-ChildItem -LiteralPath $repoDir.FullName -Directory -Force) {
            if ($domainDir.LinkType -ne 'Junction') { $leftovers += "$($repoDir.Name)/$($domainDir.Name)"; continue }
            if ($PSCmdlet.ShouldProcess($domainDir.FullName, 'remove junction into the retired standards tree')) {
                Remove-Item -LiteralPath $domainDir.FullName -Force -Recurse -Confirm:$false
            }
            $unlinked++
        }
        if (-not (Get-ChildItem -LiteralPath $repoDir.FullName -Force)) {
            if ($PSCmdlet.ShouldProcess($repoDir.FullName, 'remove emptied standards folder')) {
                Remove-Item -LiteralPath $repoDir.FullName -Force -Confirm:$false
            }
        }
    }
    if (-not (Get-ChildItem -LiteralPath $StandardsTarget -Force)) {
        if ($PSCmdlet.ShouldProcess($StandardsTarget, 'remove the emptied standards root')) {
            Remove-Item -LiteralPath $StandardsTarget -Force -Confirm:$false
        }
    }
    Write-Host "$StandardsTarget : unlinked=$unlinked (retired - standards ship in plugins)" -ForegroundColor Green
    if ($leftovers) { Write-Warning "real directories left in place under the retired standards tree: $($leftovers -join ', ')" }
}

if ($refused) {
    Write-Host ''
    Write-Warning "REFUSED $($refused.Count) target(s) - their content exists nowhere else:"
    $refused | ForEach-Object { Write-Warning "  $_" }
    Write-Warning 'Commit each into its source repo, then re-run. -Force overrides and DISCARDS them.'
    exit 1
}
