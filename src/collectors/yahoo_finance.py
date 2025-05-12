import requests
import logging
import time
from datetime import datetime
import random

logger = logging.getLogger(__name__)

def get_yahoo_news(ticker, max_results=3, max_retries=2):
    """
    Fetch recent news for a specific ticker from Yahoo Finance with conservative rate limiting.
    
    Args:
        ticker (str): Stock ticker symbol
        max_results (int): Maximum number of news items to return (reduced to 3)
        max_retries (int): Maximum number of retry attempts (limited to 2)
        
    Returns:
        list: List of dictionaries containing news items
    """
    logger.info(f"Fetching Yahoo Finance news for {ticker}")
    
    # Add mandatory delay to prevent rate limiting
    time.sleep(2 + random.random())
    
    base_url = "https://query1.finance.yahoo.com/v1/finance/search"
    
    # Parameters for the API request
    params = {
        'q': ticker,
        'quotesCount': 0,
        'newsCount': max_results,  # Reduced from 5 to 3
        'enableFuzzyQuery': False,
        'quotesQueryId': 'tss_match_phrase_query',
        'multiQuoteQueryId': 'multi_quote_single_token_query',
        'enableCb': True,
    }
    
    # Rotate user agents to avoid detection
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0'
    ]
    
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://finance.yahoo.com/',
        'Origin': 'https://finance.yahoo.com'
    }
    
    news_items = []
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Add progressive delay between retries
            if retry_count > 0:
                delay = 5 + (retry_count * 3) + random.random()
                logger.info(f"Retry {retry_count}: waiting {delay:.2f}s before retrying Yahoo Finance request")
                time.sleep(delay)
            
            response = requests.get(base_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
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
                
                logger.info(f"Found {len(news_items)} news items for {ticker} on Yahoo Finance")
                break  # Success, exit retry loop
            else:
                logger.info(f"No news found for {ticker} on Yahoo Finance")
                break  # No news is not an error, so exit retry loop
                
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:  # Too Many Requests
                retry_count += 1
                logger.warning(f"Rate limited by Yahoo Finance. Will retry ({retry_count}/{max_retries})")
                if retry_count >= max_retries:
                    logger.error(f"Giving up on Yahoo Finance after {max_retries} retries")
            else:
                logger.error(f"HTTP error fetching Yahoo Finance news for {ticker}: {e}")
                break
        except Exception as e:
            logger.error(f"Error fetching Yahoo Finance news for {ticker}: {e}")
            break
    
    return news_items