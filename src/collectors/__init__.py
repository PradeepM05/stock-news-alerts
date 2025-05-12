# src/collectors/__init__.py
#from .yahoo_finance import get_yahoo_news
from .rss_reader import get_rss_news
from .finviz_scraper import get_finviz_news

def collect_all_news(ticker):
    """
    Collect news from all available sources for a specific ticker
    with automatic deduplication.
    
    Args:
        ticker (str): Stock ticker symbol
        
    Returns:
        list: Combined list of unique news items from all sources
    """
    # Use dictionary for automatic deduplication by source_id
    news_dict = {}
    
    # Add each source's results to the dictionary
    #for item in get_yahoo_news(ticker):
    #    news_dict[item['source_id']] = item
        
    for item in get_rss_news(ticker):
        news_dict[item['source_id']] = item
        
    for item in get_finviz_news(ticker):
        news_dict[item['source_id']] = item
    
    # Convert back to list and sort by publication date (newest first)
    all_news = list(news_dict.values())
    all_news.sort(key=lambda x: x['published'], reverse=True)
    
    return all_news