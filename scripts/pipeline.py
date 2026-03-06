import os
import sys
import json
import shutil
from pathlib import Path

# Import our existing scripts
sys.path.append(os.path.dirname(__file__))

# We'll need to import the functions from our scripts
import requests
from datetime import datetime, timezone

def call_ollama(prompt, model="llama3.2:3b"):
    """Call local Ollama API"""
    response = requests.post(
        'http://localhost:11434/api/generate',
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {"temperature": 0}
        }
    )
    return response.json()['response']

def extract_account_memo(transcript_path, output_path, schema_path, prompt_template_path):
    """Extract structured data from transcript"""
    print(f"\n Reading transcript: {transcript_path}")
    
    with open(transcript_path, 'r') as f:
        transcript = f.read()
    
    with open(schema_path, 'r') as f:
        schema = json.load(f)
    
    with open(prompt_template_path, 'r') as f:
        prompt_template = f.read()
    
    full_prompt = prompt_template.replace('{TRANSCRIPT_TEXT}', transcript)
    
    print(" Extracting account data with Ollama...")
    result = call_ollama(full_prompt)
    
    account_data = json.loads(result)
    
    with open(output_path, 'w') as f:
        json.dump(account_data, f, indent=2)
    
    print(f" Account memo saved: {output_path}")
    return account_data

def generate_agent_spec(account_memo_path, output_path, prompt_template_path):
    """Generate agent spec from account memo"""
    print(f"\n Reading account memo: {account_memo_path}")
    
    with open(account_memo_path, 'r') as f:
        account_data = json.load(f)
    
    with open(prompt_template_path, 'r') as f:
        prompt_template = f.read()
    
    full_prompt = prompt_template.replace(
        '{ACCOUNT_DATA}', 
        json.dumps(account_data, indent=2)
    )
    
    print(" Generating agent prompt with Ollama...")
    system_prompt = call_ollama(full_prompt, model="llama3.2:3b")
    
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
            "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "source": "demo_call" if account_data['version'] == 'v1' else "onboarding_call",
            "integration_constraints": account_data.get('integration_constraints', [])
        }
    }
    
    
    with open(output_path, 'w') as f:
        json.dump(agent_spec, f, indent=2)
    
    print(f" Agent spec saved: {output_path}")
    return agent_spec

def process_demo_call(transcript_path, account_id, output_dir):
    """Process demo call: extract data + generate v1 agent"""
    print(f"\n{'='*60}")
    print(f"PROCESSING DEMO CALL: {account_id}")
    print(f"{'='*60}")
    
    # Create output directory
    v1_dir = Path(output_dir) / account_id / "v1"
    v1_dir.mkdir(parents=True, exist_ok=True)
    
    # Extract account memo
    memo_path = v1_dir / "account_memo.json"
    extract_account_memo(
        transcript_path,
        str(memo_path),
        "schemas/account_memo_schema.json",
        "prompts/extract_account_memo_prompt.txt"
    )
    
    # Generate agent spec
    spec_path = v1_dir / "agent_spec.json"
    generate_agent_spec(
        str(memo_path),
        str(spec_path),
        "prompts/generate_agent_prompt.txt"
    )
    
    print(f"\n v1 complete for {account_id}")
    print(f"   Outputs: {v1_dir}")
    
    return str(memo_path), str(spec_path)

def process_onboarding_call(transcript_path, account_id, output_dir):
    """Process onboarding call: extract updates + merge to v2 + regenerate agent"""
    print(f"\n{'='*60}")
    print(f"PROCESSING ONBOARDING CALL: {account_id}")
    print(f"{'='*60}")
    
    # Find v1 memo
    v1_memo_path = Path(output_dir) / account_id / "v1" / "account_memo.json"
    if not v1_memo_path.exists():
        print(f" Error: v1 not found for {account_id}. Run demo first.")
        return None
    
    # Create v2 directory
    v2_dir = Path(output_dir) / account_id / "v2"
    v2_dir.mkdir(parents=True, exist_ok=True)
    
    # Extract onboarding updates
    updates_path = v2_dir / "onboarding_updates.json"
    extract_account_memo(
        transcript_path,
        str(updates_path),
        "schemas/account_memo_schema.json",
        "prompts/extract_account_memo_prompt.txt"
    )
    
    # Merge with v1
    print("\n Merging updates with v1...")
    from merge_account_updates import merge_account_updates
    
    v2_memo_path = v2_dir / "account_memo.json"
    changelog_path = v2_dir / "changelog.json"
    
    merge_account_updates(
        str(v1_memo_path),
        str(updates_path),
        str(v2_memo_path),
        str(changelog_path)
    )
    
    # Generate v2 agent spec
    v2_spec_path = v2_dir / "agent_spec.json"
    generate_agent_spec(
        str(v2_memo_path),
        str(v2_spec_path),
        "prompts/generate_agent_prompt.txt"
    )
    
    print(f"\n v2 complete for {account_id}")
    print(f"   Outputs: {v2_dir}")
    
    return str(v2_memo_path), str(v2_spec_path)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage:")
        print("  Demo:      python pipeline.py demo <transcript.txt> <account_id>")
        print("  Onboarding: python pipeline.py onboard <transcript.txt> <account_id>")
        sys.exit(1)
    
    mode = sys.argv[1]
    transcript = sys.argv[2]
    account_id = sys.argv[3]
    output_dir = "outputs/accounts"
    
    if mode == "demo":
        process_demo_call(transcript, account_id, output_dir)
    elif mode == "onboard":
        process_onboarding_call(transcript, account_id, output_dir)
    else:
        print(f"Unknown mode: {mode}")
        sys.exit(1)