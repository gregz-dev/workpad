import requests
import json
import time

BASE_URL = "http://localhost:5000/api/v1"

def print_json(data):
    print(json.dumps(data, indent=2))

def main():
    print("--- Workpad API Client Example ---")
    print(f"Targeting: {BASE_URL}")
    
    # Check health
    try:
        resp = requests.get(f"{BASE_URL}/health")
        if resp.status_code != 200:
            print("Server not running? Please start it with 'flask run' or docker.")
            return
        print("Server is UP.")
    except requests.exceptions.ConnectionError:
        print("Connection failed. Make sure the server is running on port 5000.")
        return

    # 1. Create Entry
    print("\n1. Creating an entry...")
    payload = {
        "type": "observation",
        "content": "Observed via API client",
        "tags": ["api", "client"]
    }
    resp = requests.post(f"{BASE_URL}/entries", json=payload)
    resp.raise_for_status()
    entry = resp.json()
    print(f"   Created: {entry['id']}")
    
    entry_id = entry['id']

    # 2. Add Context
    print("\n2. Adding context...")
    ctx_payload = {
        "type": "link",
        "source": "api_client",
        "content": "http://example.com"
    }
    resp = requests.post(f"{BASE_URL}/entries/{entry_id}/context", json=ctx_payload)
    resp.raise_for_status()
    print("   Context added.")
    
    # 3. Get Entry
    print("\n3. Retrieving entry details...")
    resp = requests.get(f"{BASE_URL}/entries/{entry_id}")
    entry_full = resp.json()
    print_json(entry_full)

    # 4. List Entries
    print("\n4. Listing all entries...")
    resp = requests.get(f"{BASE_URL}/entries")
    entries = resp.json()
    print(f"   Found {len(entries)} entries.")

if __name__ == "__main__":
    main()
