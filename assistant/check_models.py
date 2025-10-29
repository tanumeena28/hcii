# check_models.py (Updated Code)
import cohere
from dotenv import dotenv_values

print("--- Checking available models for your API Key (Raw Data) ---")

env_vars = dotenv_values(".env")
api_key = env_vars.get("CohereAPIKey")

if not api_key:
    print("ERROR: .env file me 'CohereAPIKey' nahi mila.")
else:
    try:
        co = cohere.Client(api_key=api_key)
        models = co.models.list()
        
        print("\nAapki key ke liye ye models available hain (raw data):")
        # Har model ke raw data ko print karein
        for model_info in models:
            print(model_info)

    except Exception as e:
        print(f"\nEk error aaya: {e}")
        
print("\n--- Test Khatam ---")