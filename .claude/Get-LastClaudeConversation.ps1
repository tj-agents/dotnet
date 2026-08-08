function Get-LastClaudeConversation {
    <#
    .SYNOPSIS
    Returns the most recent Claude Code conversation(s) for a project, newest
    first, with a ready-to-run `claude --resume <id>` command for each.

    Reads the transcripts under ~/.claude/projects directly, so it always shows
    the genuine latest session — unlike the built-in `--resume` picker, which
    caps its list and hides the just-active / summary-less sessions.
    #>
    [CmdletBinding()]
    param(
        # How many recent conversations to return (newest first).
        [int]$Count = 5,

        # Limit to one project by a substring of its folder name (e.g.
        # "Concertable"). Omit to use the current directory's project.
        [string]$Project,

        # Search across every project instead of just the current directory's.
        [switch]$AllProjects,

        # Resolve the project from this path instead of the current directory.
        [string]$Path = (Get-Location).Path
    )

    $root = Join-Path $env:USERPROFILE ".claude\projects"
    if (-not (Test-Path $root)) {
        Write-Warning "No Claude history found at $root"
        return
    }

    if ($AllProjects) {
        $dirs = Get-ChildItem $root -Directory
    }
    elseif ($Project) {
        $dirs = Get-ChildItem $root -Directory -Filter "*$Project*"
        if (-not $dirs) { Write-Warning "No project folder matched '$Project'."; return }
    }
    else {
        # Claude names each project folder after its cwd, with every
        # non-alphanumeric character replaced by '-'.
        $slug = ($Path -replace '[^A-Za-z0-9]', '-')
        $dirs = Get-ChildItem $root -Directory | Where-Object Name -eq $slug
        if (-not $dirs) {
            Write-Warning "No transcripts for this directory ($Path). Try -Project or -AllProjects."
            return
        }
    }

    # Top-level .jsonl only — subagent/workflow transcripts live in subfolders.
    $files = $dirs | ForEach-Object {
        Get-ChildItem -LiteralPath $_.FullName -Filter *.jsonl -File -ErrorAction SilentlyContinue
    } | Sort-Object LastWriteTime -Descending

    if (-not $files) { Write-Warning "No transcript files found."; return }

    $out = [System.Collections.Generic.List[object]]::new()
    foreach ($f in $files) {
        if ($out.Count -ge $Count) { break }

        $firstUser = $null; $summary = $null; $branch = $null; $msgs = 0
        foreach ($line in [System.IO.File]::ReadLines($f.FullName)) {
            try { $d = $line | ConvertFrom-Json } catch { continue }
            $t = $d.type
            if ($t -eq 'summary') {
                if (-not $summary) { $summary = $d.summary }
            }
            elseif (($t -eq 'user' -or $t -eq 'assistant') -and -not $d.isSidechain) {
                $msgs++
                if ($d.gitBranch) { $branch = $d.gitBranch }
                if ($t -eq 'user' -and -not $firstUser) {
                    $c = $d.message.content
                    if ($c -is [System.Array]) {
                        $c = (($c | Where-Object { $_.type -eq 'text' }).text) -join ' '
                    }
                    if ($c -is [string] -and $c.Trim() -and $c -notmatch '^\s*<') {
                        $firstUser = ($c -replace '\s+', ' ').Trim()
                    }
                }
            }
        }

        if ($msgs -eq 0) { continue }   # meta-only / empty session — not resumable

        $preview = if ($summary) { $summary } elseif ($firstUser) { $firstUser } else { '(no text)' }
        if ($preview.Length -gt 100) { $preview = $preview.Substring(0, 100) + [char]0x2026 }

        $id = [System.IO.Path]::GetFileNameWithoutExtension($f.Name)
        $out.Add([pscustomobject]@{
            Modified = $f.LastWriteTime
            Session  = $id
            Branch   = $branch
            Msgs     = $msgs
            Preview  = $preview
            Resume   = "claude --resume $id"
        })
    }

    $out
}

Set-Alias claude-last Get-LastClaudeConversation
