import json
import requests

def call_ollama(prompt, model="llama3.2:3b"):
    """Call local Ollama API"""
    response = requests.post(
        'http://localhost:11434/api/generate',
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "format": "json",  # Forces JSON output
            "options": {
                "temperature": 0  # Deterministic
            }
        }
    )
    return response.json()['response']

# Read the prompt template
with open('prompts/extract_account_memo_prompt.txt', 'r') as f:
    prompt_template = f.read()

# Read the sample transcript
with open('data/demo/sample_demo_transcript.txt', 'r') as f:
    transcript = f.read()

# Build the full prompt
full_prompt = prompt_template.replace('{TRANSCRIPT_TEXT}', transcript)

print(" Calling Ollama to extract data...\n")

# Call Ollama (local, free, unlimited)
result = call_ollama(full_prompt)

print(" Ollama Response:\n")
print(result)

# Validate JSON
try:
    parsed = json.loads(result)
    print("\n Valid JSON! Keys found:")
    for key in parsed.keys():
        print(f"   - {key}")
    
    # Save the output
    with open('test_output.json', 'w') as f:
        json.dump(parsed, f, indent=2)
    print("\n Saved to test_output.json")
    
except json.JSONDecodeError as e:
    print(f"\n Invalid JSON! Error: {e}")
    print("Raw response:", result)