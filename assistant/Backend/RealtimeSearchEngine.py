from groq import Groq
import json
import datetime
import requests
from bs4 import BeautifulSoup
from dotenv import dotenv_values

# Load environment variables from a .env file.
env_vars = dotenv_values(".env")

# Retrieve environment variables for the chatbot configuration.
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GROQ_API_KEY")

# Initialize the Groq client with the provided API key.
client = Groq(api_key=GroqAPIKey)

# Define the system instructions for the chatbot.
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

# Try to load the chat log from a JSON file, or create an empty one if it doesn't exist.
try:
    with open("Data/ChatLog.json", "r") as f:
        messages = json.load(f)
except FileNotFoundError:
    with open("Data/ChatLog.json", "w") as f:
        json.dump([], f)

# Function to perform a Google search and format the results.
def GoogleSearch(query):
    search_url = f"https://www.google.com/search?q={query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        results = []
        for g in soup.find_all('div', class_='tF2Cxc'):
            title = g.find('h3').text
            description_elem = g.find('div', class_='VwiC3b')
            description = description_elem.text if description_elem else "No description available."
            results.append({"title": title, "description": description})

        Answer = f"The search results for '{query}' are:\n\n[start]\n"
        for result in results[:5]:  # Limit to 5 results
            Answer += f"Title: {result['title']}\nDescription: {result['description']}\n\n"
        Answer += "[end]\n"
        return Answer

    except requests.exceptions.RequestException as e:
        return f"Error performing Google search: {e}"

# Function to clean up the answer by removing empty lines.
def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

# Predefined chatbot conversation system message and an initial user message.
SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can I help you?"}
]

# Function to get real-time information like the current date and time
def Information():
    current_date_time = datetime.datetime.now()
    data = f"Use This Real-time Information if needed:\n"
    data += f"Day: {current_date_time.strftime('%A')}\n"
    data += f"Date: {current_date_time.strftime('%d')}\n"
    data += f"Month: {current_date_time.strftime('%B')}\n"
    data += f"Year: {current_date_time.strftime('%Y')}\n"
    data += f"Time: {current_date_time.strftime('%H')} hours, {current_date_time.strftime('%M')} minutes, {current_date_time.strftime('%S')} seconds.\n"
    return data

# Function to handle real-time search and response generation.
def RealtimeSearchEngine(prompt):
    global SystemChatBot, messages

    try:
        # Load the chat log from the JSON file.
        with open("Data/ChatLog.json", "r") as f:
            messages = json.load(f)
    except FileNotFoundError:
        messages = []

    messages.append({"role": "user", "content": f"{prompt}"})

    # Add Google search results to the system chatbot messages.
    SystemChatBot.append({"role": "system", "content": GoogleSearch(prompt)})

    # Generate a response using the Groq client.
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",  # Changed to a currently supported model
        messages=SystemChatBot + [{"role": "system", "content": Information()}] + messages,
        temperature=0.7,
        max_tokens=2048,
        top_p=1,
        stream=True,
        stop=None
    )

    Answer = ""
    # Concatenate response chunks from the streaming output.
    for chunk in completion:
        if chunk.choices[0].delta.content:
            Answer += chunk.choices[0].delta.content

    # Clean up the response.
    Answer = Answer.strip().replace("</s>", "")
    messages.append({"role": "assistant", "content": Answer})

    # Save the updated chat log back to the JSON file.
    with open("Data/ChatLog.json", "w") as f:
        json.dump(messages, f, indent=4)

    # Remove the most recent system message from the chatbot conversation.
    SystemChatBot.pop()
    return AnswerModifier(Answer=Answer)

# Main entry point of the program for interactive querying.
if __name__ == "__main__":
    while True:
        prompt = input("Enter your query: ")
        print(RealtimeSearchEngine(prompt))
        