param(
    [Parameter(Mandatory=$true)][string]$Vault,
    [string]$CodexPath,
    [string]$Destination = [Environment]::GetFolderPath('Desktop')
)
$ErrorActionPreference = 'Stop'
$vaultPath = (Resolve-Path -LiteralPath $Vault).Path
$settingsPath = Join-Path $vaultPath '00-System\Config\settings.json'
if (-not (Test-Path -LiteralPath $settingsPath)) { throw 'Select an installed Raven vault.' }
$config = Get-Content -LiteralPath (Join-Path $vaultPath '00-System\Config\memory.json') -Raw | ConvertFrom-Json
if (-not $CodexPath) { $CodexPath = $config.codex_path }
if (-not $CodexPath -or -not (Test-Path -LiteralPath $CodexPath -PathType Leaf)) {
    throw 'Provide -CodexPath pointing to the installed codex.exe.'
}
$codexExecutable = (Resolve-Path -LiteralPath $CodexPath).Path
if ([IO.Path]::GetExtension($codexExecutable) -ne '.exe') { throw 'Use the native codex.exe executable.' }
$destinationPath = (Resolve-Path -LiteralPath $Destination).Path
$name = Split-Path $vaultPath -Leaf
$terminalLink = Join-Path $destinationPath "Raven - $name.lnk"
$dashboardLink = Join-Path $destinationPath "RavenOS - $name.lnk"
$terminalIcon = Join-Path $vaultPath '00-System\Assets\raven-terminal.ico'
$dashboardIcon = Join-Path $vaultPath '00-System\Assets\raven-dashboard.ico'
foreach ($file in @($terminalIcon, $dashboardIcon, (Join-Path $vaultPath 'Dashboard.md'))) {
    if (-not (Test-Path -LiteralPath $file -PathType Leaf)) { throw "Missing file: $file" }
}
foreach ($file in @($terminalLink, $dashboardLink)) {
    if (Test-Path -LiteralPath $file) { throw "Shortcut already exists; nothing changed: $file" }
}
$shortcutShell = New-Object -ComObject WScript.Shell
$terminal = $shortcutShell.CreateShortcut($terminalLink)
$terminal.TargetPath = $codexExecutable
$terminal.WorkingDirectory = $vaultPath
$terminal.IconLocation = "$terminalIcon,0"
$terminal.Description = 'Raven - Codex in this vault'
$dashboard = $shortcutShell.CreateShortcut($dashboardLink)
$dashboard.TargetPath = Join-Path $env:WINDIR 'explorer.exe'
$dashboard.Arguments = '"obsidian://open?path=' + [Uri]::EscapeDataString((Join-Path $vaultPath 'Dashboard.md')) + '"'
$dashboard.WorkingDirectory = $vaultPath
$dashboard.IconLocation = "$dashboardIcon,0"
$dashboard.Description = 'RavenOS - Obsidian Dashboard (requires Obsidian)'
try {
    $terminal.Save()
    $dashboard.Save()
} catch {
    foreach ($file in @($terminalLink, $dashboardLink)) {
        if (Test-Path -LiteralPath $file) { Remove-Item -LiteralPath $file }
    }
    throw
}
Write-Output "Created: $terminalLink"
Write-Output "Created: $dashboardLink"
