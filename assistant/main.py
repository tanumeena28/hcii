import os
import threading
from time import sleep
from dotenv import dotenv_values

# --- Import from Project Files ---
from frontend.GUI import (GraphicalUserInterface, SetAssistantStatus, 
                         ShowTextToScreen, GetMicrophoneStatus, GetAssistantStatus, 
                         QueryModifier)
from Backend.Model import FirstlayerDMM
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech

# --- Configuration ---
env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")

# --- Core Functions ---
def MainExecution():
    SetAssistantStatus("Listening...")
    Query = SpeechRecognition()
    if not Query:
        return

    ShowTextToScreen(f"{Username}: {Query}")
    SetAssistantStatus("Thinking...")
    Decision = FirstlayerDMM(Query)
    print(f"Decision: {Decision}")

    automation_tasks = [d for d in Decision if not d.startswith("general") and not d.startswith("realtime")]
    general_tasks = [d for d in Decision if d.startswith("general")]
    
    if automation_tasks:
        Automation(automation_tasks)

    if general_tasks:
        full_query = " and ".join([q.replace("general", "").strip() for q in general_tasks])
        Answer = ChatBot(QueryModifier(full_query))
        ShowTextToScreen(f"{Assistantname}: {Answer}")
        SetAssistantStatus("Answering...")
        TextToSpeech(Answer)

# --- Thread Management ---
def FirstThread():
    while True:
        try:
            if GetMicrophoneStatus() == "True":
                MainExecution()
            else:
                if "Available..." not in GetAssistantStatus():
                    SetAssistantStatus("Available...")
                sleep(0.1)
        except Exception as e:
            print(f"Error in main loop (FirstThread): {e}")
            sleep(1)

# --- Main Execution Block ---
if __name__ == "__main__":
    # Create necessary directories and files on startup
    dirs_to_create = [
        "Data",
        os.path.join("Frontend", "Files"),
        os.path.join("Frontend", "Graphics")
    ]
    for d in dirs_to_create:
        if not os.path.exists(d):
            os.makedirs(d)
    
    files_to_touch = [
        os.path.join("Frontend", "Files", "Mic.data"),
        os.path.join("Frontend", "Files", "Status.data"),
        os.path.join("Frontend", "Files", "Responses.data"),
        os.path.join("Data", "Chatlog.json")
    ]
    for f_path in files_to_touch:
        if not os.path.exists(f_path):
            with open(f_path, 'w') as f:
                if f_path.endswith('.json'):
                    f.write('[]') # Initialize JSON file with an empty list
                else:
                    f.write('')

    # Start the assistant
    thread1 = threading.Thread(target=FirstThread, daemon=True)
    thread1.start()
    GraphicalUserInterface()