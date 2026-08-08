function Search-ClaudeHistory {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory, Position = 0)]
        [string]$Pattern,

        # Limit to one project's history. Accepts a substring of the project-hash
        # folder name (e.g. "source-repos"). Omit to search every project.
        [string]$Project,

        # Show the matching line text instead of just file/session summary.
        [switch]$ShowLines,

        # Case-sensitive match (default is case-insensitive).
        [switch]$CaseSensitive
    )

    $root = Join-Path $env:USERPROFILE ".claude\projects"
    if (-not (Test-Path $root)) {
        Write-Warning "No Claude history found at $root"
        return
    }

    $glob = if ($Project) { "*$Project*" } else { "*" }
    $files = Get-ChildItem -Path (Join-Path $root $glob) -Filter "*.jsonl" -Recurse -ErrorAction SilentlyContinue
    if (-not $files) {
        Write-Warning "No transcript files matched project filter '$Project'."
        return
    }

    $matches = $files | Select-String -Pattern $Pattern -CaseSensitive:$CaseSensitive

    if ($ShowLines) {
        $matches | ForEach-Object {
            [pscustomobject]@{
                Session = [IO.Path]::GetFileNameWithoutExtension($_.Path)
                Line    = $_.LineNumber
                Text    = ($_.Line.Trim() -replace '\s+', ' ').Substring(0, [Math]::Min(160, $_.Line.Trim().Length))
            }
        }
        return
    }

    # One row per session, with hit count and last-modified time, newest first.
    $matches | Group-Object Path | ForEach-Object {
        $f = Get-Item $_.Name
        [pscustomobject]@{
            Session  = [IO.Path]::GetFileNameWithoutExtension($f.Name)
            Hits     = $_.Count
            Modified = $f.LastWriteTime
            Project  = Split-Path (Split-Path $f.FullName -Parent) -Leaf
        }
    } | Sort-Object Modified -Descending
}

Set-Alias claude-search Search-ClaudeHistory
