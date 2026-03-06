from google import genai
import os
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    print("ERROR: GEMINI_API_KEY not found in .env file")
    exit()

# 1. Initialize the new client
client = genai.Client(api_key=api_key)

# 2. Test call using the new SDK and a current model
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents="Say 'Gemini is working!' in JSON format"
)

print(" Success! Gemini responded:")
print(response.text)