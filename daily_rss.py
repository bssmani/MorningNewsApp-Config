import requests
import feedparser
from bs4 import BeautifulSoup
import json
import datetime
import uuid

# List of Indian publication homepages to scan
PUBLICATIONS = {
  "The Times of India": "https://timesofindia.indiatimes.com",
  "The Economic Times": "https://economictimes.indiatimes.com",
  "Navbharat Times": "https://navbharattimes.indiatimes.com",
  "Maharashtra Times": "https://maharashtratimes.com",
  "Ei Samay": "https://eisamay.com",
  "Vijaya Karnataka": "https://vijaykarnataka.com",
  "Times Now": "https://www.timesnownews.com",
  "ET Now": "https://www.etnownews.com",
  "Zoom Entertainment": "https://www.zoomtventertainment.com",

  "Hindustan Times": "https://www.hindustantimes.com",
  "Mint": "https://www.livemint.com",
  "Hindustan": "https://www.livehindustan.com",

  "Dainik Jagran": "https://www.jagran.com",
  "Naidunia": "https://www.naidunia.com",
  "iNext Live": "https://www.inextlive.com",
  "Punjabi Jagran": "https://www.punjabijagran.com",
  "Gujarati Jagran": "https://www.gujaratijagran.com",
  "OnlyMyHealth": "https://www.onlymyhealth.com",
  "HerZindagi": "https://www.herzindagi.com",

  "Dainik Bhaskar": "https://www.bhaskar.com",
  "Divya Bhaskar": "https://www.divyabhaskar.co.in",
  "Divya Marathi": "https://www.divyamarathi.com",
  "Money Bhaskar": "https://www.bhaskar.com/business",

  "Anandabazar Patrika": "https://www.anandabazar.com",
  "The Telegraph": "https://www.telegraphindia.com",
  "ABP Live": "https://news.abplive.com",
  "Sananda": "https://www.sananda.in",
  "Desh": "https://www.desh.co.in",
  "Anandalok": "https://www.anandalok.in",
  "Anandamela": "https://www.anandamela.in",

  "The Hindu": "https://www.thehindu.com",
  "BusinessLine": "https://www.thehindubusinessline.com",
  "Sportstar": "https://sportstar.thehindu.com",
  "Frontline": "https://frontline.thehindu.com",
  "The Hindu Tamil Thisai": "https://www.hindutamil.in",

  "The Indian Express": "https://indianexpress.com",
  "Financial Express": "https://www.financialexpress.com",
  "Jansatta": "https://www.jansatta.com",
  "Loksatta": "https://www.loksatta.com",

  "India Today": "https://www.indiatoday.in",
  "Aaj Tak": "https://www.aajtak.in",
  "Business Today": "https://www.businesstoday.in",
  "The Lallantop": "https://www.thelallantop.com",
  "Cosmopolitan India": "https://www.cosmopolitan.in",
  "Harper's Bazaar India": "https://www.harpersbazaar.in",
  "Reader's Digest India": "https://www.readersdigest.in",

  "News18": "https://www.news18.com",
  "CNN-News18": "https://www.news18.com/cnn-news18",
  "CNBC-TV18": "https://www.cnbctv18.com",
  "Moneycontrol": "https://www.moneycontrol.com",
  "Firstpost": "https://www.firstpost.com",
  "Forbes India": "https://www.forbesindia.com",

  "Zee News": "https://zeenews.india.com",
  "Zee Business": "https://www.zeebiz.com",
  "WION": "https://www.wionews.com",
  "DNA India": "https://www.dnaindia.com",
  "Zee Bharat": "https://www.zeebharat.com",

  "NDTV": "https://www.ndtv.com",
  "NDTV India": "https://ndtv.in",
  "NDTV Profit": "https://www.ndtvprofit.com",
  "NDTV Food": "https://food.ndtv.com",
  "Gadgets 360": "https://www.gadgets360.com",

  "Eenadu": "https://www.eenadu.net",
  "ETV Bharat": "https://www.etvbharat.com",
  "Sakshi": "https://www.sakshi.com",
  "Sakshi Post": "https://english.sakshi.com",

  "Malayala Manorama": "https://www.manoramaonline.com",
  "The Week": "https://www.theweek.in",
  "Vanitha": "https://www.vanitha.in",
  "Manorama News": "https://www.manoramanews.com",

  "Mathrubhumi": "https://www.mathrubhumi.com",
  "Mathrubhumi News": "https://english.mathrubhumi.com",
  "Grihalakshmi": "https://www.grihalakshmi.com",

  "Daily Thanthi": "https://www.dailythanthi.com",
  "Thanthi TV": "https://www.thanthitv.com",
  "Maalaimalar": "https://www.maalaimalar.com",

  "Dinamalar": "https://www.dinamalar.com",
  "Dinamani": "https://www.dinamani.com",
  "The New Indian Express": "https://www.newindianexpress.com",
  "Dinakaran": "https://www.dinakaran.com",
  "Puthiya Thalaimurai": "https://www.puthiyathalaimurai.com",
  "The Federal": "https://thefederal.com",

  "Deccan Herald": "https://www.deccanherald.com",
  "Prajavani": "https://www.prajavani.net",
  "Udayavani": "https://www.udayavani.com",
  "Kannada Prabha": "https://www.kannadaprabha.com",

  "Lokmat": "https://www.lokmat.com",
  "Lokmat Times": "https://www.lokmattimes.com",
  "Sakal": "https://www.esakal.com",
  "Agrowon": "https://www.agrowon.com",
  "Pudhari": "https://www.pudhari.news",

  "Gujarat Samachar": "https://www.gujaratsamachar.com",
  "Sandesh": "https://sandesh.com",

  "Navabharat": "https://www.enavabharat.com",
  "Central Chronicle": "https://www.centralchronicle.com",

  "Patrika": "https://www.patrika.com",
  "Dainik Navjyoti": "https://www.dainiknavjyoti.com",

  "Amar Ujala": "https://www.amarujala.com",
  "Prabhat Khabar": "https://www.prabhatkhabar.com",

  "Punjab Kesari": "https://www.punjabkesari.in",
  "Jagbani": "https://jagbani.punjabkesari.in",
  "Hind Samachar": "https://epaper.hindsamachar.in",

  "Bartaman Patrika": "https://bartamanpatrika.com",
  "Sangbad Pratidin": "https://www.sangbadpratidin.in",
  "Uttarbanga Sambad": "https://uttarbangasambad.com",

  "Sambad": "https://sambad.in",
  "Dharitri": "https://www.dharitri.com",

  "Asomiya Pratidin": "https://www.asomiyapratidin.in",
  "The Assam Tribune": "https://assamtribune.com",
  "Dainik Asam": "https://www.dainikasam.com",

  "Haribhoomi": "https://www.haribhoomi.com",
  "Deshbandhu": "https://www.deshbandhu.co.in",
  "Rashtriya Sahara": "https://www.rashtriyasahara.com",
  "Inquilab": "https://www.inquilab.com",
  "Roznama Rashtriya Sahara": "https://www.roznamasahara.com",
  "Dainik Savera Times": "https://www.dainiksaveratimes.com",

  "Kutch Mitra": "https://kutchmitradaily.com",
  "Saamana": "https://www.saamana.com",
  "Tarun Bharat": "https://www.tarunbharat.com",
  "Deshdoot": "https://deshdoot.com",

  "Andhra Jyothy": "https://www.andhrajyothy.com",
  "Vaartha": "https://www.vaartha.com",
  "Namasthe Telangana": "https://www.ntnews.com",
  "Suryaa": "https://suryaa.com",

  "Deccan Chronicle": "https://www.deccanchronicle.com",
  "Asianet News": "https://www.asianetnews.com",
  "Deshabhimani": "https://www.deshabhimani.com",
  "Deepika": "https://www.deepika.com",
  "Mangalam": "https://www.mangalam.com",

  "Vartha Bharati": "https://www.varthabharati.in",
  "Vijayavani": "https://www.vijayavani.net",

  "Prameya": "https://www.prameya.com",
  "The Samaja": "https://www.thesamaja.in",

  "Ajit": "https://www.ajitjalandhar.com",
  "Punjabi Tribune": "https://punjabitribuneonline.com",

  "Greater Kashmir": "https://www.greaterkashmir.com",
  "Rising Kashmir": "https://risingkashmir.com",
  "Kashmir Observer": "https://kashmirobserver.net",

  "Filmfare": "https://www.filmfare.com",
  "Femina": "https://www.femina.in"
}

# Simple category detection based on URL keywords
def detect_category(url):
    url_lower = url.lower()
    if "business" in url_lower or "market" in url_lower or "economy" in url_lower:
        return "business"
    elif "tech" in url_lower or "technology" in url_lower or "it" in url_lower:
        return "technology"
    elif "sport" in url_lower or "cricket" in url_lower or "football" in url_lower:
        return "sports"
    elif "health" in url_lower or "wellness" in url_lower or "covid" in url_lower:
        return "health"
    elif "entertainment" in url_lower or "movies" in url_lower or "film" in url_lower:
        return "entertainment"
    elif "world" in url_lower or "international" in url_lower:
        return "world"
    else:
        return "general"

def discover_rss(url):
    """Scrape a site for RSS/Atom feed links"""
    feeds = []
    try:
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        for link in soup.find_all("link", type=["application/rss+xml", "application/atom+xml"]):
            feeds.append(link.get("href"))
    except Exception as e:
        print(f"⚠️ Error scraping {url}: {e}")
    return feeds

def validate_feed(feed_url):
    """Check if feed is functional"""
    try:
        resp = requests.get(feed_url, timeout=5)
        if resp.status_code == 200:
            parsed = feedparser.parse(resp.content)
            if parsed.bozo == 0 and len(parsed.entries) > 0:
                return True
    except Exception:
        pass
    return False

def run_daily_check():
    results = []
    for name, homepage in PUBLICATIONS.items():
        feeds = discover_rss(homepage)
        for f in feeds:
            active = validate_feed(f)
            category = detect_category(f)
            entry = {
                "id": uuid.uuid4().hex[:8],   # unique ID
                "name": name,
                "url": f,
                "category": category,
                "region": "IN",               # default region
                "priority": 90,               # fixed priority
                "active": active
            }
            results.append(entry)

filename = "gistfile2.json"
with open(filename, "w", encoding="utf-8") as out:
    json.dump(results, out, indent=2, ensure_ascii=False)

print(f"✅ Saved {filename} with {len(results)} feeds")

if __name__ == "__main__":
    run_daily_check()
