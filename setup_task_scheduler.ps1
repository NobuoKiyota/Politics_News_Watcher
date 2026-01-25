$TaskName = "PoliticsNewsWatcher_Backup"
$Action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c F:\Politics_News_Watcher\backup_to_drive.bat"
$Trigger = New-ScheduledTaskTrigger -Daily -At 1:00am
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

# Clean up if exists
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

# Register as current user (Interactive) to ensure H: drive access
Register-ScheduledTask -Action $Action -Trigger $Trigger -TaskName $TaskName -Settings $Settings -Description "Daily Backup of Politics News Watcher to Google Drive"

Write-Host "Task '$TaskName' has been registered successfully."
Write-Host "It will run daily at 01:00 AM as the current user."
