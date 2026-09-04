COMPOUND.OS Daily AI News - Windows Setup
=========================================

3 steps to get COMPOUND.OS fetching 10 real AI news items every day at 10:00
from 4 official sources (OpenAI News / GitHub Changelog / Google DeepMind / AWS ML Blog),
updating news.json, and popping a Windows desktop notification.


Step 1: Verify fetch_news.py works
----------------------------------

  # Open PowerShell or Git Bash
  cd "E:\workbuddy\2026-09-04-11-23-02\COMPOUND.OS"

  # Install dependency (first time only)
  D:\python11\python.exe -m pip install requests

  # Run manually
  D:\python11\python.exe fetch_news.py

Expected output:
  [fetch] OpenAI News <- https://openai.com/news/rss.xml
    parsed 1169 items
  [fetch] GitHub Changelog <- ...
  [fetch] Google DeepMind <- ...
  [fetch] AWS ML Blog <- ...
  [ok] wrote E:\...\news.json . 10 items

If you see [ok], news.json is ready.


Step 2 (optional): Enable DeepSeek translation
----------------------------------------------

By default, without a DeepSeek key, items stay in English and show an orange "EN" tag.

To enable Chinese translation:
  # PowerShell (current session only)
  $env:DEEPSEEK_API_KEY = "sk-your-key"

  D:\python11\python.exe fetch_news.py

Translated items show a green "译" tag.

To make the key persistent, see Appendix A.


Step 3: Enable daily auto-fetch + notification
----------------------------------------------

Option A: One-click batch script (recommended)
  1. Right-click setup_scheduler.bat -> "Run as administrator"
  2. It creates a daily 10:00 task via schtasks
  3. The task runs run_daily.bat, which calls fetch_news.py then notify.ps1

Option B: Manual (Task Scheduler GUI)
  1. Win + R -> taskschd.msc
  2. Action -> Create Task...
  3. General:
     - Name: COMPOUND.OS Daily News Fetch
     - Run whether user is logged on or not: checked
     - Run with highest privileges: checked
  4. Triggers:
     - New -> On a schedule -> Daily -> 10:00:00
  5. Actions:
     - New -> Program: E:\workbuddy\2026-09-04-11-23-02\COMPOUND.OS\run_daily.bat
     - Start in: E:\workbuddy\2026-09-04-11-23-02\COMPOUND.OS
  6. Settings:
     - If the task fails, restart every 5 minutes, up to 3 times
  7. OK -> enter Windows password

After creation, you will see "COMPOUND.OS Daily News Fetch" in Task Scheduler Library.


Step 4 (optional): Mark as enabled in the web UI
------------------------------------------------

Open the deployed COMPOUND.OS page, go to "AI 能力雷达", and click "我已开启"
on the auto-push banner. This only changes the UI hint; the actual task is managed
by Windows Task Scheduler.


Step 5: Deploy news.json to the web
-----------------------------------

Because the web workspace is hosted on WorkBuddy, news.json must be uploaded with
index.html for the browser to read it.

Currently: re-deploy the whole COMPOUND.OS folder after each fetch.
In WorkBuddy: run workbuddy_sites_deploy to upload the folder again.


Appendix A: Persist DeepSeek key
--------------------------------

  # PowerShell (admin)
  [Environment]::SetEnvironmentVariable(
    "DEEPSEEK_API_KEY", "sk-your-key", "User"
  )
  # Restart PowerShell / Task Scheduler to pick it up


Appendix B: Debug the task
--------------------------

  # Run the task now
  schtasks /Run /TN "COMPOUND.OS Daily News Fetch"

  # Query last run result
  schtasks /Query /TN "COMPOUND.OS Daily News Fetch" /V /FO LIST

  # Bypass Task Scheduler and run manually
  cd "E:\workbuddy\2026-09-04-11-23-02\COMPOUND.OS"
  .\run_daily.bat

  # View Task Scheduler event log
  Get-WinEvent -LogName "Microsoft-Windows-TaskScheduler/Operational" |
    Where-Object {$_.Message -like "*COMPOUND.OS*"} |
    Select-Object -First 5


Appendix C: Remove the task
---------------------------

  Option 1: Right-click remove_scheduler.bat -> "Run as administrator"
  Option 2: schtasks /Delete /TN "COMPOUND.OS Daily News Fetch" /F


Appendix D: Failure fallback
----------------------------

Even if the scheduled task fails:
- The browser still reads the last news.json (marked "缓存")
- No fake content is shown
- Check run_daily.log for error messages

Common failures:
  1) PC asleep -> set Power -> Sleep -> Never
  2) No internet -> single-source failures do not block others
  3) Wrong Python path -> edit PYTHON_EXE in run_daily.bat
  4) RSS source changed -> update SOURCES in fetch_news.py
