import feedparser
import random
from datetime import datetime, timezone, timedelta

WIRED_RSS = "https://www.wired.com/feed/rss"

def random_wired_articles_today():
    feed = feedparser.parse(WIRED_RSS)
    hoje = datetime.now(timezone.utc).date()
    ontem = hoje - timedelta(days=1)
    artigos = []

    for entry in feed.entries:
        try:
            pub = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        except Exception:
            continue

        pub_date = pub.date()
        if pub_date in {hoje, ontem}:
            titulo = entry.title.lower()
            keywords = ""
            if "media_keywords" in entry:
                keywords = entry.media_keywords.lower()
            elif "media:keywords" in entry:
                keywords = entry["media:keywords"].lower()

            if "shopping" in titulo or "shopping" in keywords:
                continue

            artigos.append({
                "title": entry.title,
                "link": entry.link,
                "published": pub.strftime("%Y-%m-%d %H:%M")
            })

    if not artigos:
        return []

    return random.sample(artigos, k=min(3, len(artigos)))
