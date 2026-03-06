import json
import sys
from deepdiff import DeepDiff
from datetime import datetime ,timezone

def merge_account_updates(v1_path, updates_path, v2_output_path, changelog_path):
    """
    Merge onboarding updates into existing v1 account memo to create v2.
    Generate a changelog showing what changed.
    """
    
    print(f" Reading v1 account memo from: {v1_path}")
    with open(v1_path, 'r') as f:
        v1_data = json.load(f)
    
    print(f" Reading onboarding updates from: {updates_path}")
    with open(updates_path, 'r') as f:
        updates = json.load(f)
    
    # Create v2 by merging
    print(" Merging updates into v1...")
    v2_data = deep_merge(v1_data, updates)
    
    # Update version
    v2_data['version'] = 'v2'
    
    # Generate changelog
    print(" Generating changelog...")
    diff = DeepDiff(v1_data, v2_data, ignore_order=True)
    
    changelog = {
        "account_id": v2_data.get('account_id', 'Unknown'),
        "company_name": v2_data.get('company_name', 'Unknown'),
        "updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "from_version": "v1",
        "to_version": "v2",
        "summary": generate_summary(diff),
        # Use DeepDiff's native JSON exporter, then load it back as a clean dict!
        "detailed_changes": json.loads(diff.to_json()) if diff else {}
    }
    
    # Save v2
    with open(v2_output_path, 'w') as f:
        json.dump(v2_data, f, indent=2)
    print(f" v2 account memo saved to: {v2_output_path}")
    
    # Save changelog
    with open(changelog_path, 'w') as f:
        json.dump(changelog, f, indent=2)
    print(f" Changelog saved to: {changelog_path}")
    
    return v2_data, changelog

def deep_merge(base, updates):
    """
    Deep merge two dictionaries.
    Updates override base values, but only if updates value is not None/empty.
    """
    result = base.copy()
    
    for key, value in updates.items():
        if key in result:
            # If both are dictionaries, merge recursively
            if isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = deep_merge(result[key], value)
            # If value is not None/empty, override
            elif value is not None and value != "" and value != []:
                result[key] = value
        else:
            # New key from updates
            if value is not None and value != "" and value != []:
                result[key] = value
    
    return result

def generate_summary(diff):
    """Generate human-readable summary of changes"""
    changes = []
    
    if not diff:
        return ["No changes detected"]
    
    try:
        diff_dict = diff.to_dict()
        
        # Values changed
        if 'values_changed' in diff_dict:
            for path, change in diff_dict['values_changed'].items():
                # Extract field name from path
                field = path.replace("root['", "").replace("']", "").replace("']['", ".")
                old_val = change.get('old_value', 'N/A')
                new_val = change.get('new_value', 'N/A')
                changes.append(f"Updated {field}: '{old_val}' → '{new_val}'")
        
        # New items added
        if 'dictionary_item_added' in diff_dict:
            for path in diff_dict['dictionary_item_added']:
                field = path.replace("root['", "").replace("']", "").replace("']['", ".")
                changes.append(f"Added {field}")
        
        # Items removed
        if 'dictionary_item_removed' in diff_dict:
            for path in diff_dict['dictionary_item_removed']:
                field = path.replace("root['", "").replace("']", "").replace("']['", ".")
                changes.append(f"Removed {field}")
        
        # Type changes
        if 'type_changes' in diff_dict:
            for path, change in diff_dict['type_changes'].items():
                field = path.replace("root['", "").replace("']", "").replace("']['", ".")
                changes.append(f"Changed type of {field}")
    
    except Exception as e:
        changes.append(f"Changes detected but could not parse: {str(e)}")
    
    return changes if changes else ["No significant changes detected"]
if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python merge_account_updates.py <v1.json> <updates.json> <v2_output.json> <changelog.json>")
        sys.exit(1)
    
    merge_account_updates(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])