$ErrorActionPreference = 'Stop'
$ravenRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$ravenConfig = Get-Content -LiteralPath (Join-Path $ravenRoot '00-System/Config/settings.json') -Raw | ConvertFrom-Json
$ravenPython = Join-Path (Split-Path $ravenConfig.python -Parent) 'pythonw.exe'
if (-not (Test-Path -LiteralPath $ravenPython)) { throw 'Raven Python runtime not found.' }
$ravenWorker = Join-Path $PSScriptRoot 'memory_worker.py'
$ravenTaskId = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($ravenRoot)).Replace('/','_').Replace('+','-').TrimEnd('=')
$ravenTaskName = 'Raven Memory - ' + $ravenTaskId
$ravenExisting = Get-ScheduledTask -TaskName $ravenTaskName -ErrorAction SilentlyContinue
if ($ravenExisting -and $ravenExisting.Actions.WorkingDirectory -ne $ravenRoot) {
    throw 'An unrelated task already uses this name.'
}
$ravenAction = New-ScheduledTaskAction -Execute $ravenPython -Argument ('"' + $ravenWorker + '"') -WorkingDirectory $ravenRoot
$ravenUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$ravenTriggers = @(
    (New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(2) -RepetitionInterval (New-TimeSpan -Minutes 15)),
    (New-ScheduledTaskTrigger -AtLogOn -User $ravenUser)
)
$ravenPrincipal = New-ScheduledTaskPrincipal -UserId $ravenUser -LogonType Interactive -RunLevel Limited
$ravenSettings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 5)
Register-ScheduledTask -TaskName $ravenTaskName -Action $ravenAction -Trigger $ravenTriggers -Principal $ravenPrincipal -Settings $ravenSettings -Description 'Raven shared memory: bounded local queue, subscription summarizer, no raw archive.' -Force | Select-Object TaskName,State
