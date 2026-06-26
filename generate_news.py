import json
import time
import requests
import feedparser
import re

# The URLs to your current config files
FEED_SOURCES = [
    "https://raw.githubusercontent.com/bssmani/MorningNewsApp-Config/main/gistfile1.json",
    "https://raw.githubusercontent.com/bssmani/MorningNewsApp-Config/main/gistfile2.json"
]

def clean_html(raw_html):
    if not raw_html:
        return ""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext.strip()

def fetch_all_news():
    all_articles = []
    seen_urls = set()

    for source_url in FEED_SOURCES:
        try:
            response = requests.get(source_url, timeout=10)
            feeds = response.json()
            
            for feed in feeds:
                if not feed.get("active", True):
                    continue
                
                print(f"Fetching: {feed['name']}")
                try:
                    parsed_feed = feedparser.parse(feed['url'])
                    # Limit to top 15 articles per feed to keep the file size manageable
                    for entry in parsed_feed.entries[:15]:
                        link = entry.get('link', '')
                        if link in seen_urls:
                            continue
                        
                        seen_urls.add(link)
                        
                        # Extract an image if available (checking standard RSS enclosures/media tags)
                        image_url = ""
                        if 'media_content' in entry and len(entry.media_content) > 0:
                            image_url = entry.media_content[0].get('url', '')
                        elif 'links' in entry:
                            for l in entry.links:
                                if 'image' in l.get('type', ''):
                                    image_url = l.get('href', '')
                        
                        article = {
                            "title": clean_html(entry.get('title', 'No Title')),
                            "description": clean_html(entry.get('summary', '')),
                            "url": link,
                            "urlToImage": image_url,
                            "publishedAt": entry.get('published', ''),
                            "sourceName": feed['name'],
                            "content": clean_html(entry.get('content', [{'value': ''}])[0].get('value', '')),
                            "category": feed['category'].lower(),
                            "region": feed.get('region', 'GLOBAL').upper()
                        }
                        all_articles.append(article)
                except Exception as e:
                    print(f"Failed to parse {feed['name']}: {e}")
        except Exception as e:
            print(f"Failed to fetch source list {source_url}: {e}")

    # Save to a single master file
    with open("latest_news_dump.json", "w", encoding="utf-8") as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=2)
    
    print(f"Successfully generated latest_news_dump.json with {len(all_articles)} articles.")

if __name__ == "__main__":
    fetch_all_news()
