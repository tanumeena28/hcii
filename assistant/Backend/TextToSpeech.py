import pygame
import random
import asyncio
import edge_tts
import os
from dotenv import dotenv_values

# Load environment variables from a .env file.
env_vars = dotenv_values(".env")

# Get the AssistantVoice from the environment variables.
AssistantVoice = env_vars.get("AssistantVoice")

# Asynchronous function to convert text to an audio file.
async def TextToAudioFile(text) -> None:
    file_path = r"Data\speech.mp3"  # Define the path where the speech file will be saved.

    if os.path.exists(file_path):
        os.remove(file_path)  # If it exists, remove it to avoid overwriting errors.

    # Create the communicate object to generate speech.
    communicate = edge_tts.Communicate(text, AssistantVoice, pitch="+5Hz", rate="+13%")
    await communicate.save(r"Data\speech.mp3")  # Save the generated speech as an MP3 file.

# Function to manage Text-to-Speech (TTS) functionality.
def TTS(Text, func=lambda r=None: True):
    try:
        # Convert text to an audio file asynchronously.
        asyncio.run(TextToAudioFile(Text))

        # Initialize pygame mixer for audio playback.
        pygame.mixer.init()

        # Load the generated speech file into pygame mixer.
        pygame.mixer.music.load(r"Data\speech.mp3")

        # Play the audio.
        pygame.mixer.music.play()

        # Loop until the audio is done playing or the function stops.
        while pygame.mixer.music.get_busy():
            if func() == False:  # Check if the external function returns False.
                break
            pygame.time.Clock().tick(10)  # Limit the loop to 10 ticks per second.

        return True  # Return True if the audio played successfully.

    except Exception as e:
        # Handle any exceptions during the process.
        print(f"Error in TTS: {e}")
        return False

    finally:
        try:
            # Call the provided function with False to signal the end of TTS.
            if func is not None:
                func(False)
            pygame.mixer.music.stop()  # Stop the audio playback.
            pygame.mixer.quit()       # Quit the pygame mixer.

        except Exception as e:
            # Handle any exceptions during cleanup.
            print(f"Error in finally block: {e}")

# Function to manage Text-to-Speech with additional responses for long text.
def TextToSpeech(Text, func=lambda r=None: True):
    Data = str(Text).split(".")  # Split the text by periods into a list of sentences.
    responses = ["Okay", "Alright", "Sure", "Right", "Got it"]  # List of predefined responses.

    # If the text is very long (more than 4 sentences and 250 characters), add a response message.
    if len(Data) > 4 and len(Text) >= 250:
        TTS(". ".join(Text.split(".")[:2]) + ". " + random.choice(responses), func)

    # Otherwise, just play the whole text.
    else:
        TTS(Text, func)

# Main execution loop
if __name__ == "__main__":
    while True:
        # Prompt user for input and pass it to TextToSpeech function.
        TTS(input("Enter the text: "))