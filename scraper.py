import feedparser
import requests
from bs4 import BeautifulSoup
import time
import logging
import ssl

logger = logging.getLogger(__name__)

def get_tech_news():
    """Get latest AI/tech news from RSS feeds"""
    sources = {
        "TechCrunch AI": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "MIT Tech Review": "https://www.technologyreview.com/topic/artificial-intelligence/feed",
        "Ars Technica AI": "https://arstechnica.com/ai/feed/",
    }
    
    articles = []

    for name, url in sources.items():
        try:
            logger.info(f"Fetching from {name}...")
            
            if hasattr(ssl, '_create_unverified_context'):
                ssl._create_default_https_context = ssl._create_unverified_context
            
            headers = {'User-Agent': 'Mozilla/5.0'}
            feed = feedparser.parse(url, request_headers=headers)
            
            logger.info(f"Found {len(feed.entries)} entries")
            
            for entry in feed.entries[:5]:
                try:
                    title = getattr(entry, 'title', '')
                    link = getattr(entry, 'link', '')
                    summary = getattr(entry, 'summary', '')
                    
                    if not title or not summary:
                        continue
                    
                    # Clean HTML from summary
                    soup = BeautifulSoup(summary, 'html.parser')
                    clean_summary = soup.get_text(separator=' ', strip=True)
                    
                    articles.append({
                        'source': name,
                        'title': title,
                        'url': link,
                        'summary': clean_summary,
                        'content': clean_summary  # Use summary as content
                    })
                    logger.info(f"Added: {title[:80]}")
                    
                except Exception as e:
                    logger.error(f"Error processing entry: {e}")
            
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"Error fetching {name}: {e}")
    
    logger.info(f"Total articles found: {len(articles)}")
    return articles


def get_article_content(url):
    """Deprecated - using RSS summaries instead"""
    return None