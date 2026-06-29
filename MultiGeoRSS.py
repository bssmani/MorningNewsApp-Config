import requests
import xml.etree.ElementTree as ET
import feedparser
import json
import uuid

# ---> MAP YOUR GEOS TO SPECIFIC RAW OPML URLs <---
# You can add as many OPML files as you want to a single Geo bucket
OPML_SOURCES = {
    "IN": [
        "https://raw.githubusercontent.com/plenaryapp/awesome-rss-feeds/master/countries/with_category/India.opml",
        "https://raw.githubusercontent.com/plenaryapp/awesome-rss-feeds/master/countries/without_category/India.opml"
    ],
    "US": [
        "https://raw.githubusercontent.com/plenaryapp/awesome-rss-feeds/master/countries/with_category/United%20States.opml",
        "https://raw.githubusercontent.com/plenaryapp/awesome-rss-feeds/master/countries/without_category/United%20States.opml",
        "https://raw.githubusercontent.com/plenaryapp/awesome-rss-feeds/master/recommended/with_category/Technology.opml"
    ],
    "UK": [
        "https://raw.githubusercontent.com/plenaryapp/awesome-rss-feeds/master/countries/with_category/United%20Kingdom.opml",
        "https://raw.githubusercontent.com/plenaryapp/awesome-rss-feeds/master/countries/without_category/United%20Kingdom.opml"
    ],
    "AU": [
        "https://raw.githubusercontent.com/plenaryapp/awesome-rss-feeds/master/countries/with_category/Australia.opml",
        "https://raw.githubusercontent.com/plenaryapp/awesome-rss-feeds/master/countries/without_category/Australia.opml"
    ],
    "World": [
        # ---> THE FIX: Changed to raw.githubusercontent.com <---
        "https://raw.githubusercontent.com/plenaryapp/awesome-rss-feeds/master/recommended/with_category/News.opml",
        "https://raw.githubusercontent.com/plenaryapp/awesome-rss-feeds/master/recommended/without_category/News.opml"
    ]
}

# The files you want to generate
GEO_FILES = {
    "IN": "gistfileIN.json",
    "US": "gistfileUS.json",
    "UK": "gistfileUK.json",
    "AU": "gistfileAU.json",
    "World": "gistfileWorld.json"
}

def detect_category(url):
    if not url: return "general"
    url_lower = url.lower()
    
    if any(kw in url_lower for kw in ["business", "market", "economy", "finance"]): return "business"
    if any(kw in url_lower for kw in ["tech", "technology", "it"]): return "technology"
    if any(kw in url_lower for kw in ["sport", "cricket", "football"]): return "sports"
    if any(kw in url_lower for kw in ["health", "wellness", "covid", "medical"]): return "health"
    if any(kw in url_lower for kw in ["entertainment", "movies", "film", "tv"]): return "entertainment"
    if any(kw in url_lower for kw in ["world", "international"]): return "world"
    
    return "general"

def validate_feed(feed_url):
    try:
        # User-Agent prevents firewalls from blocking the Python script
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(feed_url, headers=headers, timeout=8)
        if resp.status_code == 200:
            parsed = feedparser.parse(resp.content)
            # Ensure it is a valid feed with at least one article
            if parsed.bozo == 0 and len(parsed.entries) > 0:
                return True
    except Exception:
        pass
    return False

def process_opml_sources():
    geo_results = {geo: [] for geo in GEO_FILES.keys()}
    
    for geo, url_list in OPML_SOURCES.items():
        print(f"\n🌍 Processing feeds for {geo}...")
        
        for opml_url in url_list:
            try:
                resp = requests.get(opml_url, timeout=15)
                
                # ---> THE FIX: Silently skip 404 errors so it can check the next folder path! <---
                if resp.status_code == 404:
                    continue 
                    
                resp.raise_for_status() 
                print(f"  -> Successfully found OPML at: {opml_url}")
                
                root = ET.fromstring(resp.content)
                outlines = root.findall(".//outline[@xmlUrl]")
                
                for outline in outlines:
                    name = outline.get("title") or outline.get("text") or "Unknown Source"
                    feed_url = outline.get("xmlUrl")
                    
                    if not feed_url:
                        continue
                        
                    print(f"     Validating: {name[:30]}...") # Trimmed name for cleaner logs
                    active = validate_feed(feed_url)
                    
                    if active:
                        entry = {
                            "id": uuid.uuid4().hex[:8],
                            "name": name,
                            "url": feed_url,
                            "category": detect_category(feed_url),
                            "region": geo,
                            "priority": 90,
                            "active": True
                        }
                        geo_results[geo].append(entry)
                    else:
                        print(f"     ❌ Feed dead or invalid, skipping.")
                        
            except Exception as e:
                print(f"  ❌ Failed to parse {opml_url}. Error: {e}")

    print("\n--- Summary ---")
    for geo, filename in GEO_FILES.items():
        feed_count = len(geo_results[geo])
        if feed_count > 0:
            with open(filename, "w", encoding="utf-8") as out:
                json.dump(geo_results[geo], out, indent=2, ensure_ascii=False)
            print(f"✅ Saved {filename} with {feed_count} active feeds")
        else:
            print(f"⚪ No active feeds found for {geo}, {filename} was not created.")

if __name__ == "__main__":
    process_opml_sources()
