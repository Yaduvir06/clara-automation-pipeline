import json
import sys
from pathlib import Path
from merge_account_updates import merge_account_updates
from datetime import datetime
import requests

def call_ollama(prompt, model="llama3.2:3b"):
    """Call local Ollama API"""
    response = requests.post(
        'http://localhost:11434/api/generate',
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.3}
        }
    )
    return response.json()['response']

def process_onboarding_form(form_json_path, account_id):
    """
    Process structured onboarding form (already JSON).
    Merge with v1 and regenerate agent.
    """
    print(f"\n{'='*60}")
    print(f"PROCESSING ONBOARDING FORM: {account_id}")
    print(f"{'='*60}")
    
    # Find v1 memo
    v1_memo_path = Path("outputs/accounts") / account_id / "v1" / "account_memo.json"
    if not v1_memo_path.exists():
        print(f" Error: v1 not found for {account_id}. Run demo first.")
        sys.exit(1)
    
    # Create v2 directory
    v2_dir = Path("outputs/accounts") / account_id / "v2"
    v2_dir.mkdir(parents=True, exist_ok=True)
    
    # The form is already structured JSON - just use it as updates
    print(f" Reading onboarding form: {form_json_path}")
    with open(form_json_path, 'r') as f:
        updates = json.load(f)
    
    # Save updates for record
    updates_path = v2_dir / "onboarding_form.json"
    with open(updates_path, 'w') as f:
        json.dump(updates, f, indent=2)
    print(f" Form saved: {updates_path}")
    
    # Merge with v1
    print("\n Merging form data with v1...")
    v2_memo_path = v2_dir / "account_memo.json"
    changelog_path = v2_dir / "changelog.json"
    
    merge_account_updates(
        str(v1_memo_path),
        str(updates_path),
        str(v2_memo_path),
        str(changelog_path)
    )
    
    # Generate v2 agent spec
    print("\n Generating v2 agent spec...")
    with open(v2_memo_path, 'r') as f:
        account_data = json.load(f)
    
    with open('prompts/generate_agent_prompt.txt', 'r') as f:
        prompt_template = f.read()
    
    full_prompt = prompt_template.replace(
        '{ACCOUNT_DATA}', 
        json.dumps(account_data, indent=2)
    )
    
    system_prompt = call_ollama(full_prompt)
    
    agent_spec = {
        "agent_name": f"{account_data['company_name']} - Clara Voice Agent",
        "account_id": account_data['account_id'],
        "version": "v2",
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
            "source": "onboarding_form",
            "integration_constraints": account_data.get('integration_constraints', [])
        }
    }
    
    v2_spec_path = v2_dir / "agent_spec.json"
    with open(v2_spec_path, 'w') as f:
        json.dump(agent_spec, f, indent=2)
    
    print(f" v2 agent spec saved: {v2_spec_path}")
    print(f"\n v2 complete for {account_id}")
    print(f"   Outputs: {v2_dir}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python process_onboarding_form.py <form.json> <account_id>")
        sys.exit(1)
    
    process_onboarding_form(sys.argv[1], sys.argv[2])