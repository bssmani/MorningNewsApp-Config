import requests
import feedparser
import json
import uuid
import datetime

# Example: global feed list source (replace with actual repo/raw file URL)
GLOBAL_FEED_LIST = "https://raw.githubusercontent.com/vandenbroucke/rss-news-list/master/rss_news_list.json"

# Mapping of geographies to output filenames
GEO_FILES = {
    "UK": "gistfileUK.json",
    "US": "gistfileUS.json",
    "IN": "gistfileIN.json",
    "AE": "gistfileAE.json",   # Middle East
    "AU": "gistfileAU.json",
    "EU": "gistfileEU.json",
    "JP": "gistfileJP.json"
}

# Category detection based on URL keywords
def detect_category(url):
    if not url:
        return "general"
    url_lower = url.lower()
    if "business" in url_lower or "market" in url_lower or "economy" in url_lower or "finance" in url_lower:
        return "business"
    elif "tech" in url_lower or "technology" in url_lower or "it" in url_lower:
        return "technology"
    elif "sport" in url_lower or "cricket" in url_lower or "football" in url_lower:
        return "sports"
    elif "health" in url_lower or "wellness" in url_lower or "covid" in url_lower or "medical" in url_lower:
        return "health"
    elif "entertainment" in url_lower or "movies" in url_lower or "film" in url_lower or "tv" in url_lower:
        return "entertainment"
    elif "world" in url_lower or "international" in url_lower:
        return "world"
    else:
        return "general"

# Validate feed
def validate_feed(feed_url):
    try:
        resp = requests.get(feed_url, timeout=8)
        if resp.status_code == 200:
            parsed = feedparser.parse(resp.content)
            if parsed.bozo == 0 and len(parsed.entries) > 0:
                return True
    except Exception:
        pass
    return False

def run_geo_split():
    # Load global feed list
    resp = requests.get(GLOBAL_FEED_LIST, timeout=15)
    feeds = resp.json()

    # Prepare per‑geo results
    geo_results = {geo: [] for geo in GEO_FILES.keys()}

    for feed in feeds:
        url = feed.get("URL")
        name = feed.get("name") or feed.get("src_name_long")
        country = feed.get("src_country", "").upper()

        # Map country to geo bucket
        if country in ["GBR", "UK"]:
            geo = "UK"
        elif country in ["USA", "US"]:
            geo = "US"
        elif country in ["IND", "IN"]:
            geo = "IN"
        elif country in ["ARE", "AE", "SAU", "QAT", "OMN"]:  # Middle East
            geo = "AE"
        elif country in ["AUS", "AU"]:
            geo = "AU"
        elif country in ["EU", "DEU", "FRA", "ITA", "ESP"]:  # Europe
            geo = "EU"
        elif country in ["JPN", "JP"]:
            geo = "JP"
        else:
            continue  # skip if not mapped

        active = validate_feed(url)
        category = detect_category(url)

        entry = {
            "id": uuid.uuid4().hex[:8],
            "name": name,
            "url": url,
            "category": category,
            "region": geo,
            "priority": 90,
            "active": active
        }
        geo_results[geo].append(entry)

    # Write separate JSON files
    for geo, filename in GEO_FILES.items():
        with open(filename, "w", encoding="utf-8") as out:
            json.dump(geo_results[geo], out, indent=2, ensure_ascii=False)
        print(f"✅ Saved {filename} with {len(geo_results[geo])} feeds")

if __name__ == "__main__":
    run_geo_split()
