from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import mtranslate as mt
import time

# Load environment variables from the .env file.
env_vars = dotenv_values(".env")

# Get the input language setting from the environment variables.
InputLanguage = env_vars.get("InputLanguage", "en")  # Default to 'en' if not set

# Define the HTML code for the speech recognition interface.
HtmlCode = f"""
<!DOCTYPE html>
<html lang="{InputLanguage}">
<body>
    <button id="start">Start</button>
    <button id="end">End</button>
    <p id="output"></p>
    <script>
        const outputParagraph = document.getElementById('output');
        const startButton = document.getElementById('start');
        const endButton = document.getElementById('end');
        
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        recognition.lang = '{InputLanguage}'; 
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;

        recognition.onresult = (event) => {{
            const speechResult = event.results[0][0].transcript;
            outputParagraph.textContent = speechResult;
        }};

        recognition.onspeechend = () => {{
            recognition.stop();
        }};
        
        recognition.onerror = (event) => {{
            outputParagraph.textContent = 'Error: ' + event.error;
        }};
        
        startButton.onclick = () => {{
            recognition.start();
        }};
        
        endButton.onclick = () => {{
            recognition.stop();
        }};
    </script>
</body>
</html>
"""

# Create Data folder if it doesn't exist
data_dir = os.path.join(os.getcwd(), "Data")
os.makedirs(data_dir, exist_ok=True)

# Write HTML file
voice_file_path = os.path.join(data_dir, "Voice.html")
with open(voice_file_path, "w", encoding="utf-8") as f:
    f.write(HtmlCode)

# Chrome WebDriver setup
chrome_options = Options()
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
chrome_options.add_argument("--headless=new")  # Optional: remove if you want to see the browser

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Temp folder for status files
temp_dir = os.path.join(os.getcwd(), "Frontend", "Files")
os.makedirs(temp_dir, exist_ok=True)

# Functions
def SetAssistantStatus(Status):
    with open(os.path.join(temp_dir, "Status.data"), "w", encoding="utf-8") as f:
        f.write(Status)

def QueryModifier(Query):
    new_query = Query.lower().strip()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's"]
    if any(word + " " in new_query for word in question_words):
        if new_query[-1] not in ['?', '.', '!']:
            new_query += "?"
    else:
        if new_query[-1] not in ['.', '?', '!']:
            new_query += "."
    return new_query.capitalize()

def UniversalTranslator(Text):
    return mt.translate(Text, "en", "auto").capitalize()

def SpeechRecognition():
    driver.get(voice_file_path)
    driver.find_element(By.ID, "start").click()
    while True:
        try:
            text = driver.find_element(By.ID, "output").text
            if text:
                driver.find_element(By.ID, "end").click()
                if "en" in InputLanguage.lower():
                    return QueryModifier(text)
                else:
                    SetAssistantStatus("Translating...")
                    return QueryModifier(UniversalTranslator(text))
        except:
            pass

# Main execution
if __name__ == "__main__":
    while True:
        result = SpeechRecognition()
        print(result)
