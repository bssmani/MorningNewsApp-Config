import requests
import feedparser
import json
import uuid

# ---> GOOGLE NEWS RSS ENDPOINTS <---
# These endpoints are highly stable, ultra-fast, and bypass all publisher paywalls/blocks.
GOOGLE_FEEDS = {
    "IN": "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en",
    "US": "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en",
    "UK": "https://news.google.com/rss?hl=en-GB&gl=GB&ceid=GB:en",
    "AU": "https://news.google.com/rss?hl=en-AU&gl=AU&ceid=AU:en",
    "AE": "https://news.google.com/rss?hl=en-AE&gl=AE&ceid=AE:en",
    "World": "https://news.google.com/rss/headlines/section/topic/WORLD?hl=en-US&gl=US&ceid=US:en"
}

# The JSON files you want to generate
GEO_FILES = {
    "IN": "gistfileIN.json",
    "US": "gistfileUS.json",
    "UK": "gistfileUK.json",
    "AU": "gistfileAU.json",
    "AE": "gistfileAE.json",
    "World": "gistfileWorld.json"
}

def process_google_feeds():
    geo_results = {geo: [] for geo in GEO_FILES.keys()}
    
    # Adding a standard User-Agent so we look like a normal web browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for geo, url in GOOGLE_FEEDS.items():
        print(f"\n🌍 Fetching live news for {geo}...")
        
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status() 
            
            parsed = feedparser.parse(resp.content)
            
            # Check if the feed is valid and contains articles
            if parsed.bozo != 0 and len(parsed.entries) == 0:
                print(f"  ❌ Failed to parse XML feed for {geo}.")
                continue
                
            print(f"  -> Successfully fetched {len(parsed.entries)} articles.")
            
            # Limit to top 100 breaking stories per region to keep the JSON lightweight
            for entry in parsed.entries[:100]:
                
                # Google News cleanly packages the original publisher's name in the <source> tag
                source_name = getattr(entry, 'source', {}).get('title', 'Global News')
                
                article = {
                    "id": uuid.uuid4().hex[:8],
                    "sourceName": source_name,
                    "title": entry.get("title", "Untitled"),
                    "description": "", # Google's descriptions are mostly HTML, so we leave this blank for a clean UI
                    "url": entry.get("link", ""),
                    "category": "general" if geo != "World" else "world",
                    "region": geo,
                    "publishedAt": entry.get("published", "")
                }
                geo_results[geo].append(article)
                
        except Exception as e:
            print(f"  ❌ Failed to fetch {geo}. Error: {e}")

    print("\n--- Summary ---")
    for geo, filename in GEO_FILES.items():
        article_count = len(geo_results[geo])
        if article_count > 0:
            with open(filename, "w", encoding="utf-8") as out:
                json.dump(geo_results[geo], out, indent=2, ensure_ascii=False)
            print(f"✅ Saved {filename} with {article_count} breaking stories.")
        else:
            print(f"⚪ No articles found for {geo}, {filename} was not created.")

if __name__ == "__main__":
    process_google_feeds()
