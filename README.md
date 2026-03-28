# NexusFlow MCP
__*The Bridge Between Intent and Action: Remote-control your physical workstation directly from Notion.*__

## Key Project Feature Implementations
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
## Advanced Configuration
You can customize the automation behavior directly in the script:
  - POLL_INTERVAL: Set the frequency of Notion scans (Default: 10s).
  - ENABLE_CLEANUP: Toggle whether previous apps should be closed.
  - BROWSER_PROCESS_NAMES: Define which browsers to target for cleanup (Chrome, Edge, Firefox).
      
  
