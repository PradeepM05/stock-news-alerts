import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def get_yahoo_news(ticker, max_results=5):
    """
    Fetch recent news for a specific ticker from Yahoo Finance.
    
    Args:
        ticker (str): Stock ticker symbol
        max_results (int): Maximum number of news items to return
        
    Returns:
        list: List of dictionaries containing news items
    """
    logger.info(f"Fetching Yahoo Finance news for {ticker}")
    
    base_url = "https://query1.finance.yahoo.com/v1/finance/search"
    
    # Parameters for the API request
    params = {
        'q': ticker,
        'quotesCount': 0,
        'newsCount': max_results,
        'enableFuzzyQuery': False,
        'quotesQueryId': 'tss_match_phrase_query',
        'multiQuoteQueryId': 'multi_quote_single_token_query',
        'enableCb': True,
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(base_url, params=params, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        news_items = []
        
        if 'news' in data and len(data['news']) > 0:
            for item in data['news']:
                news_items.append({
                    'source': 'Yahoo Finance',
                    'title': item.get('title', ''),
                    'summary': item.get('summary', ''),
                    'url': item.get('link', ''),
                    'published': datetime.fromtimestamp(item.get('providerPublishTime', 0)),
                    'ticker': ticker,
                    'source_id': f"yahoo-{item.get('uuid', '')}"
                })
            
            logger.info(f"Found {len(news_items)} news items for {ticker}")
        else:
            logger.info(f"No news found for {ticker}")
            
        return news_items
        
    except Exception as e:
        logger.error(f"Error fetching Yahoo Finance news for {ticker}: {e}")
        return []