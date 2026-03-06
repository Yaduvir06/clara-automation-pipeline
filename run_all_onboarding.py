import os
from pathlib import Path
from scripts.pipeline import process_onboarding_call
from scripts.process_onboarding_form import process_onboarding_form

def main():
    # Find all onboarding files
    onboarding_dir = Path("data/onboarding")
    files = sorted(list(onboarding_dir.glob("*.*")))
    
    if not files:
        print("❌ No onboarding files found in data/onboarding/")
        return
    
    print(f"\n{'='*60}")
    print(f"BATCH PROCESSING: {len(files)} ONBOARDING FILES")
    print(f"{'='*60}\n")
    
    results = {"success": [], "failed": []}
    
    for i, file in enumerate(files, start=1):
        account_id = f"ACC{i:03d}"
        
        try:
            print(f"\n[{i}/{len(files)}] Processing: {file.name}")
            
            if file.suffix == '.json':
                # Process as form
                process_onboarding_form(str(file), account_id)
            else:
                # Process as transcript
                process_onboarding_call(str(file), account_id, "outputs/accounts")
            
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