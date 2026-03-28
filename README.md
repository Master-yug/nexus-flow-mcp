# NexusFlow MCP
__*The Bridge Between Intent and Action: Remote-control your physical workstation directly from Notion.*__

## Key Project Feature Implementations SO FAR
- **Real-time Monitoring:** Polls your Notion database every 10 seconds for status changes
- **Smart Environment Launch:** Automatically opens browser, folder, and VS Code when a task is set to "Focusing"
- **Two-Way Time Tracking:** Automatically tracks and syncs time spent on each task back to Notion
- **System Cleanup:** Closes previous browser sessions and manages VS Code windows before launching new environments
- **Heartbeat System:** Updates "Last Synced" timestamp every 5 minutes to show the script is active
- **State Tracking:** Prevents re-launching the same environment multiple times
- **Multiple Browser Support:** Works with Chrome, Edge, Firefox, and more
- **Graceful Shutdown:** Clean exit with Ctrl+C
- **Rich Console Output:** Color-coded, timestamped messages with emoji indicators

## Installation
1. Prerequisites
   - A Notion Integration Token (Internal Integration).
   - A Notion Database shared with your integration.
   - Python installed on your local machine.
2. Clone & Install
   ```
   git clone https://github.com/Master-yug/nexus-flow-mcp
   cd nexus-flow-mcp
   pip install -r requirements.txt
   ```
4. Environment Configuration
    Create a .env file in the root directory:
   ```
   NOTION_TOKEN=your_internal_integration_token_here
   DATABASE_ID=your_database_id_here
   ```
5. Database Schema
   Ensure your Notion Database (Table view) has the following properties:
   - Task Name: Title
   - Status: Select/Status (Options: Focusing, Standby, etc.)
   - Folder Path: Text/Rich-text (Local path to your project)
   - Resources: URL (Main documentation or dashboard link)
## Usage
1.  Start the watcher:
   ```
   python notion_query.py
   ```
2. Trigger a Context Switch:
      Go to your Notion "Command Center" and set a project to Focusing.
3. Watch the Magic:
   NexusFlow will detect the change, perform a system cleanup, and launch your environment automatically.
## What does the code do when you hit python notion_query.py
1. Connection Test: Verifies Notion API access
2. Configuration Display: Shows cleanup and time tracking settings
3. Active Monitoring: Polls database every 10 seconds
4. Status Detection: Looks for tasks with "Focusing" status
5. Environment Launch: When a focusing task is detected:
   - Cleans up previous session (closes browsers, manages VS Code)
   - Opens configured URL in browser
   - Opens folder in Windows Explorer
   - Opens VS Code in that folder
   - Starts time tracking session
6. Continuous Sync: Every 5 minutes, updates "Last Synced" timestamp
7.Time Tracking: When task changes from "Focusing", calculates and saves time spent
## What does the output look like
ON STARTUP:
```
============================================================
🔮 NOTION CONTEXT SWITCHER - BACKGROUND WATCHER
   with Two-Way Time Tracking
============================================================
Testing connection to Notion API...
✅ Connected to Notion API

🧹 Cleanup Configuration:
  ENABLE_CLEANUP: True
  CLOSE_BROWSER: True
  CLOSE_VSCODE: True
  USE_REUSE_WINDOW: True
  Browser targets: msedge.exe, chrome.exe, firefox.exe

⏱️  Time Tracking Configuration:
  Heartbeat Interval: 5 minutes
  Tracks time in 'Time Spent' column
  Updates 'Last Synced' every heartbeat

🔍 BACKGROUND WATCHER ACTIVE
📊 Monitoring database: 3277e5f14cae806bba52d3c246fdfcdb
⏱️  Polling every 10 seconds
💓 Heartbeat every 5 minutes
💡 Press Ctrl+C to stop
------------------------------------------------------------
[09:45:26] 🔎 Scanning... No active context

```
NEW TASK DETECTED
```
[09:45:55] 🎯 NEW FOCUSING TASK DETECTED: My Awesome Project
[09:45:55]    ID: 3277e5f1-4cae-80dc-b7af-eb26f85cab40

🧹 SYSTEM CLEANUP - Closing previous session...
   Closing browser: msedge.exe
   ✅ Browser closed: msedge.exe
   ℹ️  Using VS Code --reuse-window (not closing instances)
✅ Cleanup completed

============================================================
🚀 ENVIRONMENT MANAGER - Launching: My Awesome Project
============================================================
Status: Focusing
Resources URL: https://github.com/myproject
Folder Path: C:\Users\username\Projects\MyProject
------------------------------------------------------------
✅ Status is 'Focusing' - launching environment...

🌐 Opening URL: https://github.com/myproject
📂 Opening folder: C:\Users\username\Projects\MyProject
💻 Opening VS Code in: C:\Users\username\Projects\MyProject
   Using --reuse-window flag
✅ VS Code opened successfully

✅ Environment launch complete!
🎯 Session started: 'My Awesome Project' at 09:45:55
[09:45:55] ✅ Environment launched and session started
```
ACTIVE SESSION
```
[09:46:05] 🔄 Scanning... Environment is currently synced for: My Awesome Project
   ⏱️  Current session: 0.2 minutes
```
HEARTBEAT
```
💓 HEARTBEAT: Updated 'Last Synced' for 'My Awesome Project'
```
SESSION END
```
[09:55:26] ℹ️  No 'Focusing' task. Ending session...

⏱️  Ending session for 'My Awesome Project'...
   Time spent: 9.5 minutes
💾 TIME SYNC: Added 9.5 minutes to 'My Awesome Project' (Total: 9.5 minutes)
```
## Advanced Configuration
You can customize the automation behavior directly in the script:
  - POLL_INTERVAL: Set the frequency of Notion scans (Default: 10s).
  - ENABLE_CLEANUP: Toggle whether previous apps should be closed.
  - BROWSER_PROCESS_NAMES: Define which browsers to target for cleanup (Chrome, Edge, Firefox).
      
  
