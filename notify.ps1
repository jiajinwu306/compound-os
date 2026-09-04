# COMPOUND.OS Daily AI News - Windows Desktop Notification
# Called by run_daily.bat after fetch_news.py succeeds. Can also be run manually.
# Uses .NET WinForms NotifyIcon (built into Windows), no third-party modules.

param(
    [string]$Mode = "ok"   # ok | fail
)

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$jsonPath = Join-Path $scriptDir "news.json"

$title = "COMPOUND.OS - AI Radar"
$body = ""
$iconType = [System.Windows.Forms.ToolTipIcon]::Info

function Read-NewsJson {
    if (-not (Test-Path $jsonPath)) { return $null }
    try {
        $raw = Get-Content $jsonPath -Raw -Encoding UTF8
        return $raw | ConvertFrom-Json
    } catch {
        return $null
    }
}

if ($Mode -eq "fail") {
    $body = "Today's AI news fetch failed. Check network or run fetch_news.py for details."
    $iconType = [System.Windows.Forms.ToolTipIcon]::Warning
} else {
    $news = Read-NewsJson
    if ($news -and $news.items -and $news.items.Count -gt 0) {
        $count = $news.items.Count
        $headline = $news.items[0].original_title
        if (-not $headline) { $headline = $news.items[0].title }
        if (-not $headline) { $headline = "Headline missing" }
        $body = "Updated $count items.`nHeadline: $headline"
    } else {
        $body = "No valid news found. Run fetch_news.py to refresh."
        $iconType = [System.Windows.Forms.ToolTipIcon]::Warning
    }
}

$notify = New-Object System.Windows.Forms.NotifyIcon
$notify.Icon = [System.Drawing.SystemIcons]::Information
$notify.Visible = $true
$notify.BalloonTipTitle = $title
$notify.BalloonTipText = $body
$notify.BalloonTipIcon = $iconType

$notify.ShowBalloonTip(8000)

Start-Sleep -Milliseconds 200
$notify.Dispose()
