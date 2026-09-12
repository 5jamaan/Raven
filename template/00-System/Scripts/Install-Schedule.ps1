$ErrorActionPreference = 'Stop'
$taskVault = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$taskSettings = Get-Content -LiteralPath (Join-Path $taskVault '00-System/Config/settings.json') -Raw | ConvertFrom-Json
$taskName = 'RavenOS - Yerel Bakim'
if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) { throw 'Görev mevcut; üzerine yazılmadı' }
$taskArgs = '"' + (Join-Path $PSScriptRoot 'brain.py') + '" maintenance'
$taskPythonw = Join-Path (Split-Path $taskSettings.python -Parent) 'pythonw.exe'
$taskAction = New-ScheduledTaskAction -Execute $taskPythonw -Argument $taskArgs -WorkingDirectory $taskVault
$taskTriggers = @((New-ScheduledTaskTrigger -Daily -At $taskSettings.daily_time), (New-ScheduledTaskTrigger -Weekly -DaysOfWeek $taskSettings.weekly_day -At $taskSettings.weekly_time), (New-ScheduledTaskTrigger -AtLogOn -User ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name)))
$taskOptions = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 10) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
$taskPrincipal = New-ScheduledTaskPrincipal -UserId ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName $taskName -Action $taskAction -Trigger $taskTriggers -Settings $taskOptions -Principal $taskPrincipal -Description 'RavenOS yerel inceleme, gizlilik taraması ve doğrulanmış yedek. Sırlar kaydedilmez.' | Select-Object TaskName,State
