param([switch]$CheckOnly, [switch]$SelfTest)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$repo = 'C:\Users\Admin\AppData\Local\hermes'
$git = 'D:\hermes-data\desktop-runtime\hermes\0.21.0\win-x64\git\cmd\git.exe'
$ssh = 'C:\Windows\System32\OpenSSH\ssh.exe'
$state = 'D:\hermes-data\task-maintenance'
$url = 'git@github.com:windowsmoon/hermes-skills.git'
$paths = @('autosync.py', 'sync_to_github.bat', 'scripts/github-sync.ps1', 'scripts/github-sync.md')
$log = Join-Path $state 'github-sync.log'
$code = 10
$lock = $null
$temp = $null
$before = $null
$index = Join-Path $repo '.git\index'
$indexLock = "$index.lock"
function Record([string]$message) {
    $line = "$(Get-Date -Format o) $message"
    Add-Content -LiteralPath $log -Value $line -Encoding UTF8
    Write-Output $line
}
function Git([string[]]$a) {
    # Never include Git output in errors/logs: credentials or file contents may occur there.
    $old = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    $output = & $git -c core.hooksPath=NUL -c commit.gpgSign=false -C $repo @a 2>&1
    $result = $LASTEXITCODE
    $ErrorActionPreference = $old
    if ($result -ne 0) { throw "git-operation-failed" }
    return @($output | ForEach-Object { $_.ToString() })
}
function SafeText([string]$text) {
    $rules = @(
        '(?i)-----BEGIN [A-Z ]*PRIVATE KEY-----',
        '(?i)\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,}|AKIA[A-Z0-9]{16})\b',
        '(?i)\bBearer\s+[A-Za-z0-9_./+=-]{16,}',
        '(?i)https?://[^\s/@:]+:[^\s/@]+@',
        '(?i)["'']?(?:api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret|password|secret[_-]?key)["'']?\s*[:=]\s*["'']?[^\s"''`,;\]\}]{8,}',
        '\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b'
    )
    foreach ($rule in $rules) { if ($text -match $rule) { return $false } }
    # Long random-looking material is suspect, including unknown token formats.
    foreach ($m in [regex]::Matches($text, '[A-Za-z0-9_+/=-]{40,}')) {
        $token = $m.Value
        if ($token -match '^[0-9a-fA-F]{40,64}$') { continue }
        $counts = @{}
        foreach ($ch in $token.ToCharArray()) { $k = [string]$ch; if (!$counts.ContainsKey($k)) { $counts[$k] = 0 }; $counts[$k]++ }
        $entropy = 0.0
        foreach ($n in $counts.Values) { $p = $n / [double]$token.Length; $entropy -= $p * [Math]::Log($p, 2) }
        if ($entropy -gt 4.5) { return $false }
    }
    return $true
}
if ($SelfTest) {
    $cases = @(
        ('ghp_' + ('X' * 30)),
        ('sk-' + ('z' * 30)),
        ('-----BEGIN ' + 'OPENSSH PRIVATE KEY-----'),
        ('api_key' + ' = "' + ('x' * 20) + '"'),
        ('Bearer ' + ('x' * 24)),
        ('https://' + 'user:credential@example.invalid')
    )
    foreach ($case in $cases) { if (SafeText $case) { Write-Output 'FAIL scanner'; exit 20 } }
    if (!(SafeText 'ordinary documentation without credentials')) { exit 20 }
    Write-Output 'PASS scanner: six blocked fixtures and clean text'
    exit 0
}
try {
    if (!(Test-Path -LiteralPath $git -PathType Leaf) -or !(Test-Path -LiteralPath $ssh -PathType Leaf)) { throw 'missing-executable' }
    if (!(Test-Path -LiteralPath (Join-Path $repo '.git') -PathType Container)) { throw 'unsupported-worktree' }
    # Reject inherited alternate Git contexts instead of operating on an unintended repository.
    foreach ($name in @('GIT_INDEX_FILE','GIT_DIR','GIT_WORK_TREE','GIT_OBJECT_DIRECTORY','GIT_ALTERNATE_OBJECT_DIRECTORIES','GIT_CONFIG_COUNT')) {
        if ([Environment]::GetEnvironmentVariable($name)) { throw 'inherited-git-context' }
    }
    $env:GIT_TERMINAL_PROMPT = '0'
    $env:GIT_SSH_COMMAND = 'C:/Windows/System32/OpenSSH/ssh.exe -o BatchMode=yes -o ConnectTimeout=15 -o StrictHostKeyChecking=yes'
    $env:GIT_SSH_VARIANT = 'ssh'
    $code = 50
    # Standard index lock excludes normal Git writers; never write, reset, stash, or restore the user's index.
    $lock = [IO.File]::Open($indexLock, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    $before = (Get-FileHash -LiteralPath $index -Algorithm SHA256).Hash
    $code = 20
    $origin = @(Git @('remote','get-url','origin'))
    $pushOrigin = @(Git @('remote','get-url','--push','--all','origin'))
    if ($origin.Count -ne 1 -or $origin[0] -cne $url -or $pushOrigin.Count -ne 1 -or $pushOrigin[0] -cne $url) { throw 'unexpected-origin' }
    foreach ($marker in @('MERGE_HEAD','CHERRY_PICK_HEAD','REVERT_HEAD','rebase-merge','rebase-apply')) {
        if (Test-Path -LiteralPath (Join-Path "$repo\.git" $marker)) { throw 'operation-in-progress' }
    }
    $staged = @(Git @('diff','--cached','--name-only','--no-renames'))
    foreach ($path in $paths) { if ($staged -contains $path) { throw 'allowlist-overlaps-user-index' } }
    $code = 60
    $manifest = Get-Content -LiteralPath (Join-Path $state 'github-sync-approved.json') -Raw | ConvertFrom-Json
    if ($manifest.version -ne 1 -or @($manifest.files.PSObject.Properties).Count -ne $paths.Count) { throw 'invalid-approval' }
    $temp = Join-Path $state ('sync-' + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $temp | Out-Null
    $snapshots = @{}
    foreach ($path in $paths) {
        $source = Join-Path $repo $path
        # No directory traversal, reparse-point escape, symlink, submodule, binary, or oversized payload.
        $item = Get-Item -LiteralPath $source -Force
        if ($item.PSIsContainer -or $item.Length -gt 262144) { throw 'invalid-file' }
        $cursor = $item
        while ($null -ne $cursor) {
            if ($cursor.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'reparse-point' }
            if ($cursor -is [IO.FileInfo]) { $cursor = $cursor.Directory } else { $cursor = $cursor.Parent }
        }
        $snapshot = Join-Path $temp ([IO.Path]::GetFileName($path))
        [IO.File]::WriteAllBytes($snapshot, [IO.File]::ReadAllBytes($source))
        $actual = (Get-FileHash -LiteralPath $snapshot -Algorithm SHA256).Hash
        $property = $manifest.files.PSObject.Properties[$path]
        if ($null -eq $property -or $property.Value -cne $actual) { throw 'unreviewed-file-version' }
        $bytes = [IO.File]::ReadAllBytes($snapshot)
        $text = (New-Object Text.UTF8Encoding($false, $true)).GetString($bytes)
        if ($text.IndexOf([char]0) -ge 0 -or !(SafeText $text)) { $code = 20; throw 'secret-or-binary-detected' }
        $snapshots[$path] = $snapshot
    }
    $code = 30
    $remote = @(Git @('ls-remote','--exit-code',$url,'refs/heads/main'))
    if ($remote.Count -ne 1 -or $remote[0] -notmatch '^([0-9a-f]{40})\s+refs/heads/main$') { throw 'remote-main-missing' }
    $remoteId = $Matches[1]
    if ($CheckOnly) { Record 'PASS check-only: exact scope, approved hashes, secret scan, SSH remote main; no commit or push'; $code = 0 }
    else {
        Git @('fetch','--no-tags','--no-write-fetch-head',$url,'refs/heads/main') | Out-Null
        Git @('cat-file','-e',"$remoteId^{commit}") | Out-Null
        # Never publish unrelated local commits. The new commit's only parent is remote main.
        Git @('merge-base','--is-ancestor','HEAD',$remoteId) | Out-Null
        $code = 40
        $env:GIT_INDEX_FILE = Join-Path $temp 'index'
        Git @('read-tree',$remoteId) | Out-Null
        foreach ($path in $paths) {
            $blob = @(Git @('hash-object','-w','--no-filters','--',$snapshots[$path]))[0]
            Git @('update-index','--add','--cacheinfo',"100644,$blob,$path") | Out-Null
        }
        $tree = @(Git @('write-tree'))[0]
        $oldTree = @(Git @('rev-parse',"$remoteId^{tree}"))[0]
        $changes = @(Git @('diff-tree','--no-commit-id','--name-only','-r',$oldTree,$tree))
        foreach ($change in $changes) { if ($paths -cnotcontains $change) { $code = 20; throw 'unexpected-payload' } }
        if ($tree -eq $oldTree) { Record "OK no approved changes; remote-main=$remoteId" }
        else {
            $commit = @(Git @('commit-tree',$tree,'-p',$remoteId,'-m','fix: isolate and safeguard scheduled GitHub sync'))[0]
            $code = 50
            if ((Get-FileHash -LiteralPath $index -Algorithm SHA256).Hash -cne $before) { throw 'index-changed' }
            $code = 30
            # Explicit single refspec; ordinary fast-forward push, never force or mirror.
            Git @('-c','push.followTags=false','push','--porcelain',$url,"${commit}:refs/heads/main") | Out-Null
            $verified = @(Git @('ls-remote','--exit-code',$url,'refs/heads/main'))
            if ($verified.Count -ne 1 -or $verified[0] -notmatch "^$commit\s+refs/heads/main$") { throw 'push-verification-failed' }
            Record "OK committed-and-pushed=$commit files=$($changes.Count); local HEAD/index untouched"
        }
        $code = 0
    }
} catch {
    # Codes describe the failing phase without revealing file contents, tokens, or raw command output.
    Record "ERROR exit=$code (10=prerequisite,20=safety,30=remote,40=git,50=index-lock,60=approval); no broad staging performed"
} finally {
    Remove-Item Env:GIT_INDEX_FILE -ErrorAction SilentlyContinue
    if ($null -ne $lock) {
        if ($null -ne $before -and (Get-FileHash -LiteralPath $index -Algorithm SHA256).Hash -cne $before) { $code = 50; Record 'ERROR user index changed externally; not restored or overwritten' }
        $lock.Dispose()
        Remove-Item -LiteralPath $indexLock -ErrorAction SilentlyContinue
    }
    if ($null -ne $temp -and (Test-Path -LiteralPath $temp)) { Remove-Item -LiteralPath $temp -Recurse -Force -ErrorAction SilentlyContinue }
}
exit $code
