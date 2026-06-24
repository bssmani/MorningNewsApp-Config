import requests
import json
import uuid

def build_json():
    with open('registry.txt', 'r') as f:
        lines = f.readlines()

    results = []
    for line in lines:
        if line.startswith("#") or not line.strip(): continue
        cat, reg, url = [x.strip() for x in line.split('|')]
        
        # Validate reachability
        try:
            req = requests.get(url, timeout=5)
            if req.status_code == 200:
                results.append({
                    "id": str(uuid.uuid4())[:8],
                    "name": url.split('//')[-1].split('/')[0], # Simplified naming
                    "url": url,
                    "category": cat.lower(),
                    "region": reg.upper(),
                    "priority": 90,
                    "active": True
                })
        except:
            print(f"Dead feed detected: {url}")

    with open('gistfile1.json', 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    build_json()
