#!/usr/bin/env python3

import os
import sys
import time
import json
import signal
import subprocess
import webbrowser
import requests
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")
POLL_INTERVAL = 10  
ENABLE_CLEANUP = True  
CLOSE_BROWSER = True  
CLOSE_VSCODE = True    
USE_REUSE_WINDOW = True  
BROWSER_PROCESS_NAMES = ["msedge.exe", "chrome.exe", "firefox.exe"] 
NOTION_VERSION = "2022-06-28"
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": NOTION_VERSION
}
last_active_page_id = None
running = True
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    ORANGE = '\033[38;5;208m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def signal_handler(sig, frame):
    global running
    print(f"\n{Colors.YELLOW}Shutting down background watcher...{Colors.END}")
    running = False

def validate_config():
    missing_vars = []    
    if not NOTION_TOKEN:
        missing_vars.append("NOTION_TOKEN")    
    if missing_vars:
        print(f"{Colors.RED}Error: Missing required environment variables: {', '.join(missing_vars)}{Colors.END}")
        print("Please check your .env file and ensure these variables are set.")
        return False
        
    return True

def test_connection():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}"    
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            return True
        elif response.status_code == 404:
            print(f"{Colors.RED}Database not found. Make sure you've shared it with your integration.{Colors.END}")
            return False
        elif response.status_code == 401:
            print(f"{Colors.RED}Authentication failed. Check your NOTION_TOKEN.{Colors.END}")
            return False
        else:
            print(f"{Colors.RED}API Error: {response.status_code} - {response.text}{Colors.END}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"{Colors.RED}Connection error: {e}{Colors.END}")
        return False

def query_database():  
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"    
    try:
        response = requests.post(url, headers=HEADERS, json={"page_size": 100})        
        if response.status_code == 200:
            data = response.json()
            return data.get('results', [])
        else:
            print(f"{Colors.RED}Failed to query database: {response.status_code}{Colors.END}")
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"{Colors.RED}Network error: {e}{Colors.END}")
        return []


def extract_page_title(properties):
    for prop_name, prop_data in properties.items():
        if prop_data.get('type') == 'title':
            title_list = prop_data.get('title', [])
            if title_list:
                return title_list[0].get('plain_text', 'Untitled')
            return 'Untitled'

    for prop_name in ['Name', 'Task', 'Title']:
        if prop_name in properties:
            prop_data = properties[prop_name]
            if prop_data.get('type') == 'rich_text':
                text_list = prop_data.get('rich_text', [])
                if text_list:
                    return text_list[0].get('plain_text', 'Untitled')    
    return 'Unnamed Task'

def extract_status(properties):
    if 'Status' in properties:
        prop_data = properties['Status']
        prop_type = prop_data.get('type')
        if prop_type == 'select':
            select_data = prop_data.get('select')
            if select_data:
                return select_data.get('name', 'No status')
        elif prop_type == 'status':
            status_data = prop_data.get('status')
            if status_data:
                return status_data.get('name', 'No status')
    for prop_name in properties:
        if prop_name.lower() == 'status':
            prop_data = properties[prop_name]
            if prop_data.get('type') == 'select':
                select_data = prop_data.get('select')
                if select_data:
                    return select_data.get('name', 'No status')    
    return 'No status set'

def extract_resources_url(properties):
    url_props = ['Resources URL', 'Resources', 'URL', 'Link', 'Resource']
    
    for prop_name in url_props:
        if prop_name in properties:
            prop_data = properties[prop_name]
            prop_type = prop_data.get('type')
            
            if prop_type == 'url':
                return prop_data.get('url', '')
            elif prop_type == 'rich_text':
                text_list = prop_data.get('rich_text', [])
                if text_list:
                    return text_list[0].get('plain_text', '')    
    return None

def extract_folder_path(properties):
    folder_props = ['Folder Path', 'Folder', 'Path', 'Directory', 'Working Directory']
    
    for prop_name in folder_props:
        if prop_name in properties:
            prop_data = properties[prop_name]
            prop_type = prop_data.get('type')            
            if prop_type == 'rich_text':
                text_list = prop_data.get('rich_text', [])
                if text_list:
                    return text_list[0].get('plain_text', '')    
    return None

def cleanup_previous_session():
    if not ENABLE_CLEANUP:
        print(f"{Colors.BLUE} Cleanup disabled (ENABLE_CLEANUP=False){Colors.END}")
        return
    
    print(f"\n{Colors.ORANGE}SYSTEM CLEANUP - Closing previous session...{Colors.END}")
    cleanup_success = False
    if CLOSE_BROWSER:
        for browser_name in BROWSER_PROCESS_NAMES:
            try:
                check_cmd = f'tasklist /FI "IMAGENAME eq {browser_name}" 2>NUL | find /I "{browser_name}" >NUL'
                result = subprocess.run(check_cmd, shell=True, capture_output=True)
                
                if result.returncode == 0:  
                    print(f"{Colors.ORANGE}   Closing browser: {browser_name}{Colors.END}")
                    graceful_cmd = f'taskkill /IM {browser_name} /T 2>NUL'
                    subprocess.run(graceful_cmd, shell=True, capture_output=True)
                    time.sleep(1)                    
                    force_cmd = f'taskkill /F /IM {browser_name} /T 2>NUL'
                    result = subprocess.run(force_cmd, shell=True, capture_output=True, text=True)                    
                    if result.returncode == 0:
                        print(f"{Colors.GREEN}   Browser closed: {browser_name}{Colors.END}")
                        cleanup_success = True
                    else:
                        print(f"{Colors.YELLOW}    Could not force close {browser_name}{Colors.END}")
                else:
                    pass                    
            except Exception as e:
                print(f"{Colors.YELLOW}    Error closing {browser_name}: {e}{Colors.END}")

    if CLOSE_VSCODE and not USE_REUSE_WINDOW:
        try:
            check_cmd = 'tasklist /FI "IMAGENAME eq code.exe" 2>NUL | find /I "code.exe" >NUL'
            result = subprocess.run(check_cmd, shell=True, capture_output=True)            
            if result.returncode == 0: 
                print(f"{Colors.ORANGE}   Closing VS Code instances...{Colors.END}")                
                subprocess.run('taskkill /IM code.exe /T 2>NUL', shell=True, capture_output=True)
                time.sleep(1)                
                result = subprocess.run('taskkill /F /IM code.exe /T 2>NUL', shell=True, capture_output=True, text=True)                
                if result.returncode == 0:
                    print(f"{Colors.GREEN}   VS Code closed{Colors.END}")
                    cleanup_success = True
                else:
                    print(f"{Colors.YELLOW}    Could not force close VS Code{Colors.END}")
            else:
                print(f"{Colors.BLUE}    VS Code not running{Colors.END}")                
        except Exception as e:
            print(f"{Colors.YELLOW}    Error closing VS Code: {e}{Colors.END}")
    elif CLOSE_VSCODE and USE_REUSE_WINDOW:
        print(f"{Colors.BLUE}    Using VS Code --reuse-window (not closing instances){Colors.END}")    
    if cleanup_success:
        print(f"{Colors.GREEN}Cleanup completed{Colors.END}")
    else:
        print(f"{Colors.BLUE} No cleanup actions needed{Colors.END}")    
    print()  

def open_resources(url):
    if url and url.strip():
        print(f"{Colors.CYAN}Opening URL: {url}{Colors.END}")
        try:
            webbrowser.open(url)
            return True
        except Exception as e:
            print(f"{Colors.RED}Failed to open URL: {e}{Colors.END}")
            return False
    else:
        print(f"{Colors.YELLOW} No URL provided{Colors.END}")
        return False

def open_folder(folder_path):
    if folder_path and folder_path.strip():
        expanded_path = os.path.expandvars(os.path.expanduser(folder_path))        
        if not os.path.isabs(expanded_path):
            expanded_path = os.path.abspath(expanded_path)        
        print(f"{Colors.CYAN}Opening folder: {expanded_path}{Colors.END}")        
        try:
            if os.path.exists(expanded_path):
                if sys.platform == 'win32':
                    os.startfile(expanded_path)
                elif sys.platform == 'darwin':  
                    subprocess.run(['open', expanded_path])
                else:  
                    subprocess.run(['xdg-open', expanded_path])
                return True
            else:
                print(f"{Colors.RED}Folder does not exist: {expanded_path}{Colors.END}")                
                response = input(f"{Colors.YELLOW}Folder doesn't exist. Create it? (y/n): {Colors.END}")
                if response.lower() in ['y', 'yes']:
                    os.makedirs(expanded_path, exist_ok=True)
                    print(f"{Colors.GREEN}Created folder: {expanded_path}{Colors.END}")
                    if sys.platform == 'win32':
                        os.startfile(expanded_path)
                    return True
                return False
        except Exception as e:
            print(f"{Colors.RED}Failed to open folder: {e}{Colors.END}")
            return False
    else:
        print(f"{Colors.YELLOW} No folder path provided{Colors.END}")
        return False

def open_vscode(folder_path):
    if folder_path and folder_path.strip():
        expanded_path = os.path.expandvars(os.path.expanduser(folder_path))        
        if not os.path.isabs(expanded_path):
            expanded_path = os.path.abspath(expanded_path)        
        print(f"{Colors.PURPLE}Opening VS Code in: {expanded_path}{Colors.END}")        
        try:
            if os.path.exists(expanded_path):
                try:
                    subprocess.run(['code', '--version'], capture_output=True, check=True)
                except (subprocess.CalledProcessError, FileNotFoundError):
                    print(f"{Colors.YELLOW} 'code' command not found in PATH{Colors.END}")
                    if sys.platform == 'win32':
                        possible_paths = [
                            r"C:\Program Files\Microsoft VS Code\bin\code.cmd",
                            r"C:\Program Files (x86)\Microsoft VS Code\bin\code.cmd",
                            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\bin\code.cmd")
                        ]                        
                        for code_path in possible_paths:
                            if os.path.exists(code_path):
                                cmd = [code_path, '.']
                                if USE_REUSE_WINDOW:
                                    cmd.insert(1, '--reuse-window')
                                subprocess.run(cmd, cwd=expanded_path)
                                print(f"{Colors.GREEN}VS Code opened successfully{Colors.END}")
                                return True                        
                        print(f"{Colors.RED}Could not find VS Code executable{Colors.END}")
                        return False               

                cmd = ['code', '.']
                if USE_REUSE_WINDOW:
                    cmd.insert(1, '--reuse-window')
                    print(f"{Colors.BLUE}   Using --reuse-window flag{Colors.END}")                
                result = subprocess.run(
                    cmd,
                    cwd=expanded_path,
                    capture_output=True,
                    text=True,
                    shell=True
                )                
                if result.returncode == 0:
                    print(f"{Colors.GREEN}VS Code opened successfully{Colors.END}")
                    return True
                else:
                    print(f"{Colors.RED}Failed to open VS Code{Colors.END}")
                    return False
            else:
                print(f"{Colors.RED}Cannot open VS Code - folder does not exist: {expanded_path}{Colors.END}")
                
                response = input(f"{Colors.YELLOW}Folder doesn't exist. Create it? (y/n): {Colors.END}")
                if response.lower() in ['y', 'yes']:
                    os.makedirs(expanded_path, exist_ok=True)
                    print(f"{Colors.GREEN}Created folder: {expanded_path}{Colors.END}")
                    return open_vscode(expanded_path)
                return False
        except Exception as e:
            print(f"{Colors.RED}Failed to open VS Code: {e}{Colors.END}")
            return False
    else:
        print(f"{Colors.YELLOW} No folder path provided for VS Code{Colors.END}")
        return False


def launch_environment_manager(page_data):
    properties = page_data.get('properties', {})
    task_name = extract_page_title(properties)
    status = extract_status(properties)
    resources_url = extract_resources_url(properties)
    folder_path = extract_folder_path(properties)    
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}ENVIRONMENT MANAGER - Launching: {task_name}{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"Status: {status}")
    print(f"Resources URL: {resources_url if resources_url else 'Not set'}")
    print(f"Folder Path: {folder_path if folder_path else 'Not set'}")
    print(f"{'-'*60}")
    if status != "Focusing":
        print(f"{Colors.YELLOW} Status is '{status}', not 'Focusing'. Environment manager requires 'Focusing' status.{Colors.END}")
        return False    
    print(f"{Colors.GREEN}Status is 'Focusing' - launching environment...{Colors.END}\n")
    if resources_url:
        open_resources(resources_url)
    else:
        print(f"{Colors.YELLOW} Skipping browser - no Resources URL{Colors.END}")
    if folder_path:
        open_folder(folder_path)
    else:
        print(f"{Colors.YELLOW} Skipping folder open - no Folder Path{Colors.END}")
    if folder_path:
        open_vscode(folder_path)
    else:
        print(f"{Colors.YELLOW} Skipping VS Code - no Folder Path{Colors.END}")    
    print(f"\n{Colors.GREEN}Environment launch complete!{Colors.END}")
    return True


def find_focusing_page(results):
    focusing_pages = []    
    for page in results:
        properties = page.get('properties', {})
        status = extract_status(properties)        
        if status == "Focusing":
            focusing_pages.append(page)    
    if len(focusing_pages) == 0:
        return None
    elif len(focusing_pages) == 1:
        return focusing_pages[0]
    else:
        current_time = datetime.now().strftime("%H:%M:%S")
        print(f"[{current_time}] {Colors.RED} WARNING: Multiple ({len(focusing_pages)}) 'Focusing' tasks found!{Colors.END}")
        print(f"{Colors.YELLOW}   Only one task should be set to 'Focusing' at a time.{Colors.END}")        
        for idx, page in enumerate(focusing_pages, 1):
            properties = page.get('properties', {})
            task_name = extract_page_title(properties)
            page_id = page.get('id', 'unknown')[:8]
            print(f"   {idx}. {task_name} (ID: {page_id}...)")        
        return None  
def countdown_timer(seconds):
    for i in range(seconds, 0, -1):
        if not running:
            return False
        print(f"{Colors.BLUE}Next scan in {i} seconds...   \r{Colors.END}", end="", flush=True)
        time.sleep(1)
    print(" " * 30, end="\r")  
    return True
def print_cleanup_config():
    print(f"\n{Colors.BOLD}🧹 Cleanup Configuration:{Colors.END}")
    print(f"  ENABLE_CLEANUP: {Colors.GREEN if ENABLE_CLEANUP else Colors.RED}{ENABLE_CLEANUP}{Colors.END}")
    if ENABLE_CLEANUP:
        print(f"  CLOSE_BROWSER: {Colors.GREEN if CLOSE_BROWSER else Colors.RED}{CLOSE_BROWSER}{Colors.END}")
        print(f"  CLOSE_VSCODE: {Colors.GREEN if CLOSE_VSCODE else Colors.RED}{CLOSE_VSCODE}{Colors.END}")
        print(f"  USE_REUSE_WINDOW: {Colors.GREEN if USE_REUSE_WINDOW else Colors.RED}{USE_REUSE_WINDOW}{Colors.END}")
        if CLOSE_BROWSER:
            print(f"  Browser targets: {', '.join(BROWSER_PROCESS_NAMES)}")
def watch_database():
    global last_active_page_id, running
    print_cleanup_config()    
    print(f"\n{Colors.BOLD}BACKGROUND WATCHER ACTIVE{Colors.END}")
    print(f"{Colors.CYAN}Monitoring database: {DATABASE_ID}{Colors.END}")
    print(f"{Colors.CYAN} Polling every {POLL_INTERVAL} seconds{Colors.END}")
    print(f"{Colors.YELLOW}Press Ctrl+C to stop{Colors.END}")
    print("-" * 60)    
    loop_count = 0    
    while running:
        loop_count += 1
        current_time = datetime.now().strftime("%H:%M:%S")
        
        try:
            results = query_database()
            if not results:
                print(f"[{current_time}] {Colors.YELLOW} No results found in database{Colors.END}")
                if last_active_page_id is not None:
                    print(f"[{current_time}] {Colors.BLUE} Clearing last active page ID{Colors.END}")
                    last_active_page_id = None
            else:
                focusing_page = find_focusing_page(results)
                
                if focusing_page is None:
                    if last_active_page_id is not None:
                        print(f"[{current_time}] {Colors.BLUE} No 'Focusing' task. Clearing last active page ID.{Colors.END}")
                        last_active_page_id = None
                    else:
                        print(f"[{current_time}] {Colors.BLUE}Scanning... No active context{Colors.END}")
                else:
                    current_page_id = focusing_page.get('id')
                    task_name = extract_page_title(focusing_page.get('properties', {}))
                    display_name = task_name if len(task_name) <= 30 else task_name[:27] + "..."                    
                    if current_page_id != last_active_page_id:
                        print(f"[{current_time}] {Colors.GREEN}NEW FOCUSING TASK DETECTED: {display_name}{Colors.END}")
                        print(f"[{current_time}] {Colors.GREEN}   ID: {current_page_id}{Colors.END}")
                        cleanup_previous_session()
                        success = launch_environment_manager(focusing_page)
                        if success:
                            last_active_page_id = current_page_id
                            print(f"[{current_time}] {Colors.GREEN}Environment launched successfully{Colors.END}")
                        else:
                            print(f"[{current_time}] {Colors.RED}Failed to launch environment{Colors.END}")
                    else:
                        print(f"[{current_time}] {Colors.CYAN}Scanning... Environment is currently synced for: {display_name}{Colors.END}")
        
        except Exception as e:
            print(f"[{current_time}] {Colors.RED}Error in watcher loop: {e}{Colors.END}")       

        if running:
            print(f"{Colors.BLUE}Still watching... Next scan in {POLL_INTERVAL} seconds{Colors.END}")        

            if not countdown_timer(POLL_INTERVAL):
                break  

def main():
    global running
    signal.signal(signal.SIGINT, signal_handler)    
    print(f"{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}NOTION CONTEXT SWITCHER - BACKGROUND WATCHER{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}")
    

    if not validate_config():
        return
    

    print(f"{Colors.BOLD}Testing connection to Notion API...{Colors.END}")
    if not test_connection():
        print(f"\n{Colors.BOLD}Troubleshooting tips:{Colors.END}")
        print(f"  1. Make sure your NOTION_TOKEN is correct in the .env file")
        print(f"  2. Go to your Notion database and click 'Share'")
        print(f"  3. Make sure you've invited your integration")
        print(f"  4. Verify the database ID: {DATABASE_ID}")
        return
    
    print(f"{Colors.GREEN}Connected to Notion API{Colors.END}")  

    try:
        watch_database()
    except KeyboardInterrupt:
        pass
    finally:
        print(f"\n{Colors.GREEN}Background watcher stopped. Goodbye!{Colors.END}")


if __name__ == "__main__":
    main()
