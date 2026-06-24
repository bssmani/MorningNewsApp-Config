import requests
import json
import uuid
import xml.etree.ElementTree as ET

def build_json():
    with open('registry.txt', 'r') as f:
        lines = f.readlines()

    results = []
    for line in lines:
        if line.startswith("#") or not line.strip(): continue
        cat, reg, url = [x.strip() for x in line.split('|')]
        
        try:
            req = requests.get(url, timeout=10)
            if req.status_code == 200:
                # 1. PEER INSIDE THE XML
                root = ET.fromstring(req.content)
                
                # 2. Extract title from channel, fallback to a clean domain name
                channel = root.find(".//channel")
                if channel is not None and channel.find("title") is not None:
                    # Clean the name (remove trailing spaces or unexpected chars)
                    pub_name = channel.find("title").text.split('|')[0].strip()
                else:
                    # Fallback if XML structure is weird
                    pub_name = url.split('//')[-1].split('/')[0].replace('feeds.', '').replace('www.', '')

                results.append({
                    "id": str(uuid.uuid4())[:8],
                    "name": pub_name, 
                    "url": url,
                    "category": cat.lower(),
                    "region": reg.upper(),
                    "priority": 90,
                    "active": True
                })
        except Exception as e:
            print(f"Failed to process {url}: {e}")

    with open('gistfile1.json', 'w') as f:
        json.dump(results, f, indent=2)
