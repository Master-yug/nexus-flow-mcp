# NexusFlow MCP
__*The Bridge Between Intent and Action: Remote-control your physical workstation directly from Notion.*__

## Key Project Feature Implementations
- **Real-Time Context Switching:** Instantly transition between "Code Mode," "Research," or "Design" by changing a single status dropdown in Notion.
- **Smart System Cleanup:** Features a "Fresh Start" utility that gracefully closes previous browser sessions and VS Code instances before launching a new context to eliminate digital clutter.
- **Intelligent Background Watcher:** Runs as a headless service, polling the Notion API every 10 seconds to detect "Intent Changes" without manual terminal interaction.
- **VS Code Integration**: Automatically launches VS Code in the specific project directory, supporting the --reuse-window flag to keep your desktop organized.
- **Multi-Platform Path Handling:** Supports environment variable expansion and absolute/relative pathing for project folders.

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
      
  
