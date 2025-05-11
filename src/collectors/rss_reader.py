import feedparser
import logging
from datetime import datetime
import time
from dateutil import parser

logger = logging.getLogger(__name__)

# Updated list without Yahoo Finance RSS
FINANCIAL_RSS_FEEDS = [
    {
        "name": "MarketWatch",
        "url": "http://feeds.marketwatch.com/marketwatch/topstories/",
    },
    {
        "name": "CNBC",
        "url": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    },
    {
        "name": "Seeking Alpha",
        "url": "https://seekingalpha.com/market_currents.xml",
    }
]

def get_rss_news(ticker):
    """
    Fetch recent news for a specific ticker from RSS feeds.
    
    Args:
        ticker (str): Stock ticker symbol
        
    Returns:
        list: List of dictionaries containing news items
    """
    logger.info(f"Fetching RSS news for {ticker}")
    
    news_items = []
    
    for feed_info in FINANCIAL_RSS_FEEDS:
        feed_name = feed_info["name"]
        feed_url = feed_info["url"]
        
        try:
            logger.info(f"Parsing feed: {feed_name}")
            feed = feedparser.parse(feed_url)
            
            if not feed.entries:
                logger.warning(f"No entries found in feed: {feed_name}")
                continue
                
            for entry in feed.entries:
                # Check if the ticker is mentioned in the title or description
                title = entry.get('title', '')
                description = entry.get('description', '')
                
                if ticker.lower() in title.lower() or ticker.lower() in description.lower():
                    # Parse the published date
                    if 'published' in entry:
                        published = parser.parse(entry.published)
                    elif 'pubDate' in entry:
                        published = parser.parse(entry.pubDate)
                    else:
                        published = datetime.now()
                    
                    news_items.append({
                        'source': feed_name,
                        'title': title,
                        'summary': description,
                        'url': entry.get('link', ''),
                        'published': published,
                        'ticker': ticker,
                        'source_id': f"rss-{feed_name}-{hash(title)}"
                    })
            
            # Be nice to the RSS server
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"Error fetching RSS feed {feed_name}: {e}")
    
    logger.info(f"Found {len(news_items)} RSS news items for {ticker}")
    return news_items