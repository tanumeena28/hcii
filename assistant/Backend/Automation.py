import threading
import webbrowser
import keyboard
import requests
import subprocess
import os
from bs4 import BeautifulSoup
from dotenv import dotenv_values
from groq import Groq
from AppOpener import open as appopen, close as appclose
from pywhatkit import playonyt, search

# --- Configuration ---
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GROQ_API_KEY")
client = Groq(api_key=GroqAPIKey)
useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

# --- Core Functions ---
def OpenApp(app: str):
    try:
        appopen(app, match_closest=True, output=False, throw_error=True)
    except Exception:
        try:
            url = f"https://www.google.com/search?q={app}"
            webbrowser.open(url)
        except Exception as e:
            print(f"Error opening app or searching web: {e}")

def CloseApp(app: str):
    try:
        appclose(app, match_closest=True, output=False, throw_error=True)
    except Exception as e:
        print(f"Could not close app {app}: {e}")

def PlayYoutube(query: str):
    playonyt(query)

# ... (Include your other functions like GoogleSearch, YouTubeSearch, Content, System here) ...

# In Backend/Automation.py, replace the old function with this new one

def TranslateAndExecute(commands: list[str]):
    threads = []
    # List of common website endings
    tlds = ['.com', '.org', '.in', '.net', '.edu', '.gov', '.co', '.io']

    for command in commands:
        command = command.strip()
        target_func = None
        args = ()

        if command.startswith("open"):
            target = command.removeprefix("open").strip().lower()

            # --- NEW SMART LOGIC ---
            # 1. Check for specific known site names first
            if target == "instagram":
                target_func = webbrowser.open
                args = ("https://www.instagram.com",)
            elif target == "facebook":
                target_func = webbrowser.open
                args = ("https://www.facebook.com",)
            
            # 2. Else, check if the target looks like a URL
            elif any(tld in target for tld in tlds):
                url = target if target.startswith("http") else f"https://{target}"
                target_func = webbrowser.open
                args = (url,)
            
            # 3. If it's not a URL or a special name, fall back to searching for a local app
            else:
                target_func = OpenApp
                args = (target,)
        
        elif command.startswith("close"):
            target_func = CloseApp
            args = (command.removeprefix("close").strip(),)

        elif command.startswith("play"):
            target_func = PlayYoutube
            args = (command.removeprefix("play").strip(),)
        
        # (Add your other elif conditions here for Content, System, etc.)

        if target_func:
            thread = threading.Thread(target=target_func, args=args)
            threads.append(thread)
            thread.start()

    # Wait for all commands to finish before returning
    for thread in threads:
        thread.join()

def Automation(commands: list[str]):
    TranslateAndExecute(commands)
    return True