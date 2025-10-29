import asyncio
import random
from PIL import Image
import requests
import os
from time import sleep
from dotenv import dotenv_values

# Load environment variables
env_vars = dotenv_values(".env")
HUGGINGFACE_KEY = env_vars.get("HuggingFaceAPIKey")

API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {HUGGINGFACE_KEY}"}

# Ensure required directories exist
DATA_DIR = os.path.join(os.getcwd(), "Data")
FRONTEND_DIR = os.path.join(os.getcwd(), "frontend", "Files")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(FRONTEND_DIR, exist_ok=True)

# Ensure the ImageGeneration.data file exists
DATA_FILE = os.path.join(FRONTEND_DIR, "ImageGeneration.data")
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        f.write(",False")  # initial empty prompt and False status

# Function to open and display images
def open_images(prompt):
    folder_path = DATA_DIR
    prompt_clean = prompt.replace(" ", "_")
    files = [f"{prompt_clean}_{i+1}.jpg" for i in range(5)]

    for jpg_file in files:
        image_path = os.path.join(folder_path, jpg_file)
        try:
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            sleep(1)
        except IOError:
            print(f"Unable to open {image_path}")

# Async function to query Hugging Face API
async def query(payload):
    response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
    return response.content

# Async function to generate images
async def generate_images(prompt: str):
    tasks = []
    for _ in range(4):
        payload = {
            "inputs": f"{prompt}, quality=4K, sharpness=maximum, Ultra High details, high resolution, seed={random.randint(0, 1000000)}",
        }
        tasks.append(asyncio.create_task(query(payload)))

    image_bytes_list = await asyncio.gather(*tasks)

    for i, image_bytes in enumerate(image_bytes_list):
        with open(os.path.join(DATA_DIR, f"{prompt.replace(' ', '_')}_{i+1}.jpg"), "wb") as f:
            f.write(image_bytes)

# Wrapper function to generate and open images
def GenerateImages(prompt: str):
    asyncio.run(generate_images(prompt))
    open_images(prompt)

# Main loop to monitor for image generation requests
if __name__ == "__main__":
    print("Monitoring for image generation requests...")
    while True:
        try:
            with open(DATA_FILE, "r") as f:
                data = f.read().strip()
            
            if "," in data:
                prompt, status = data.split(",", 1)
                status = status.strip()
            else:
                prompt, status = "", "False"

            if status.lower() == "true" and prompt.strip():
                print(f"Generating images for: {prompt}")
                GenerateImages(prompt.strip())

                # Reset the file after generating images
                with open(DATA_FILE, "w") as f:
                    f.write(",False")
        except Exception as e:
            print(f"Error monitoring file: {e}")
        sleep(1)
