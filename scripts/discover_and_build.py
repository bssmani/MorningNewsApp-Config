import requests
import json
import uuid
import xml.etree.ElementTree as ET

def build_json():
    input_file = 'registry.txt'
    output_file = 'gistfile1.json'
    
    # Check if registry exists
    try:
        with open(input_file, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
        return

    results = []
    for line in lines:
        # Ignore comments and empty lines
        if line.startswith("#") or not line.strip(): 
            continue
        
        # Split by pipe and strip whitespace
        parts = [x.strip() for x in line.split('|')]
        
        # Ensure we have at least 3 parts (cat, reg, url)
        if len(parts) < 3:
            continue
            
        cat, reg, url = parts[0], parts[1], parts[2]
        custom_name = parts[3] if len(parts) > 3 else None
        
        try:
            # Request with timeout to ensure the script doesn't hang
            req = requests.get(url, timeout=10)
            if req.status_code == 200:
                # Attempt to parse XML for the official title
                try:
                    root = ET.fromstring(req.content)
                    channel = root.find(".//channel")
                    extracted_title = channel.find("title").text if channel is not None and channel.find("title") is not None else None
                except:
                    extracted_title = None
                
                # Logic Hierarchy:
                # 1. Custom Name from registry.txt
                # 2. Extracted title from RSS channel
                # 3. Domain name as last resort
                final_name = custom_name if custom_name else (extracted_title or url.split('//')[-1].split('/')[0])
                
                # Sanitize the name (strip unexpected whitespace/chars)
                final_name = final_name.strip()

                results.append({
                    "id": str(uuid.uuid4())[:8],
                    "name": final_name,
                    "url": url,
                    "category": cat.lower(),
                    "region": reg.upper(),
                    "priority": 90,
                    "active": True
                })
                print(f"Successfully processed: {final_name}")
            else:
                print(f"Failed to access {url} (Status: {req.status_code})")
        except Exception as e:
            print(f"Error processing {url}: {e}")

    # Write the formatted JSON to file
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Successfully built {output_file} with {len(results)} feeds.")

if __name__ == "__main__":
    build_json()
