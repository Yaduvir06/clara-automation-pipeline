import json
import requests
from datetime import datetime

def call_ollama(prompt, model="llama3.2:3b"):
    """Call local Ollama API"""
    response = requests.post(
        'http://localhost:11434/api/generate',
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3  # Slightly creative for natural language
            }
        }
    )
    return response.json()['response']

def generate_agent_spec(account_memo_path, output_path):
    """Generate Retell agent specification from account memo"""
    
    # Load account memo
    print(f" Reading account memo from: {account_memo_path}")
    with open(account_memo_path, 'r') as f:
        account_data = json.load(f)
    
    # Load prompt template
    with open('prompts/generate_agent_prompt.txt', 'r') as f:
        prompt_template = f.read()
    
    # Build full prompt
    full_prompt = prompt_template.replace(
        '{ACCOUNT_DATA}', 
        json.dumps(account_data, indent=2)
    )
    
    print(" Generating agent system prompt with Ollama...")
    
    # Generate system prompt
    system_prompt = call_ollama(full_prompt)
    
    print(" System prompt generated!\n")
    
    # Build complete agent spec
    agent_spec = {
        "agent_name": f"{account_data['company_name']} - Clara Voice Agent",
        "account_id": account_data['account_id'],
        "version": account_data['version'],
        "voice_style": "professional, warm, and efficient",
        "system_prompt": system_prompt,
        "configuration": {
            "business_hours": account_data.get('business_hours'),
            "emergency_routing": account_data.get('emergency_routing_rules'),
            "non_emergency_routing": account_data.get('non_emergency_routing_rules'),
            "transfer_timeout_seconds": account_data.get('call_transfer_rules', {}).get('timeout_seconds', 60),
            "fallback_protocol": account_data.get('emergency_routing_rules', {}).get('fallback_action', 'Take message and assure callback')
        },
        "metadata": {
            "created_at": datetime.utcnow().isoformat() + "Z",
            "source": "demo_call" if account_data['version'] == 'v1' else "onboarding_call",
            "integration_constraints": account_data.get('integration_constraints', [])
        }
    }
    
    # Save agent spec
    with open(output_path, 'w') as f:
        json.dump(agent_spec, f, indent=2)
    
    print(f" Agent spec saved to: {output_path}")
    print(f"\n Agent Name: {agent_spec['agent_name']}")
    print(f" Version: {agent_spec['version']}")
    print(f" Account ID: {agent_spec['account_id']}")
    
    return agent_spec

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python generate_agent_spec.py <account_memo.json> <output_spec.json>")
        sys.exit(1)
    
    generate_agent_spec(sys.argv[1], sys.argv[2])