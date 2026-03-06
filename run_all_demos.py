import os
from pathlib import Path
from scripts.pipeline import process_demo_call

def main():
    # Find all demo transcripts
    demo_dir = Path("data/demo")
    transcripts = sorted(list(demo_dir.glob("*.txt")))
    
    if not transcripts:
        print("❌ No demo transcripts found in data/demo/")
        return
    
    print(f"\n{'='*60}")
    print(f"BATCH PROCESSING: {len(transcripts)} DEMO CALLS")
    print(f"{'='*60}\n")
    
    results = {"success": [], "failed": []}
    
    for i, transcript in enumerate(transcripts, start=1):
        account_id = f"ACC{i:03d}"
        
        try:
            print(f"\n[{i}/{len(transcripts)}] Processing: {transcript.name}")
            process_demo_call(str(transcript), account_id, "outputs/accounts")
            results["success"].append(account_id)
            print(f"✅ Success: {account_id}")
        except Exception as e:
            results["failed"].append((account_id, str(e)))
            print(f"❌ Error in {account_id}: {e}")
    
    # Summary
    print(f"\n{'='*60}")
    print(f"BATCH COMPLETE")
    print(f"{'='*60}")
    print(f"✅ Successful: {len(results['success'])}")
    print(f"❌ Failed: {len(results['failed'])}")
    
    if results['failed']:
        print("\nFailed accounts:")
        for account_id, error in results['failed']:
            print(f"  - {account_id}: {error}")

if __name__ == "__main__":
    main()