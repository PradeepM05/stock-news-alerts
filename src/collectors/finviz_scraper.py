# src/collectors/finviz_scraper.py
import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime
import time
import hashlib

logger = logging.getLogger(__name__)

def get_finviz_news(ticker):
    """
    Scrape news for a specific ticker from Finviz.
    
    Args:
        ticker (str): Stock ticker symbol
        
    Returns:
        list: List of dictionaries containing news items
    """
    logger.info(f"Fetching Finviz news for {ticker}")
    
    url = f"https://finviz.com/quote.ashx?t={ticker}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    news_items = []
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the news table
        news_table = soup.find('table', {'class': 'fullview-news-outer'})
        
        if not news_table:
            logger.warning(f"No news table found for {ticker}")
            return news_items
            
        rows = news_table.find_all('tr')
        
        for row in rows:
            date_td = row.find('td', {'align': 'right'})
            news_td = row.find('td', {'align': 'left'})
            
            if date_td and news_td:
                date_str = date_td.text.strip()
                
                # Convert relative date to datetime
                if "Today" in date_str:
                    published = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                else:
                    try:
                        # Format could be "May-05-24" or similar
                        published = datetime.strptime(date_str, "%b-%d-%y")
                    except ValueError:
                        published = datetime.now()  # Fallback
                
                # Get news link and title
                news_link = news_td.find('a')
                if news_link:
                    title = news_link.text.strip()
                    url = news_link.get('href', '')
                    
                    # Create unique ID using hash of title and URL
                    unique_id = hashlib.md5(f"{title}{url}".encode()).hexdigest()
                    
                    news_items.append({
                        'source': 'Finviz',
                        'title': title,
                        'summary': title,  # Finviz only provides titles
                        'url': url,
                        'published': published,
                        'ticker': ticker,
                        'source_id': f"finviz-{unique_id}"
                    })
        
        logger.info(f"Found {len(news_items)} Finviz news items for {ticker}")
        
    except Exception as e:
        logger.error(f"Error fetching Finviz news for {ticker}: {e}")
    
    return news_items