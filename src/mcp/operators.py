import logging
from typing import Dict, List, Any, Optional
from src.collectors import get_yahoo_news, get_rss_news, get_finviz_news
from src.database import AlertDatabase
from src.alerts import GitHubIssueCreator


logger = logging.getLogger(__name__)

class ContextOperator:
    """Base class for all context operators in the MCP architecture."""
    
    def __init__(self, name: str):
        self.name = name
    
    def execute(self, context):
        """
        Execute the operator on the given context.
        This method must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement execute()")


class NewsCollectionOperator(ContextOperator):
    """Operator that collects news items for a given ticker."""
    
    def __init__(self):
        super().__init__("news_collection")
        
    def execute(self, context):
        """Collect news items for the ticker in the context."""
        context.update_state(current_operation="collecting_news")
        
        # Use dictionary for automatic deduplication by source_id
        news_dict = {}
        
        # Add each source's results to the dictionary
        for item in get_yahoo_news(context.ticker):
            news_dict[item['source_id']] = item
            
        for item in get_rss_news(context.ticker):
            news_dict[item['source_id']] = item
            
        for item in get_finviz_news(context.ticker):
            news_dict[item['source_id']] = item
        
        # Convert to list and sort by published date
        all_news = list(news_dict.values())
        all_news.sort(key=lambda x: x['published'], reverse=True)
        
        # Add to context
        context.add_news_items(all_news)
        logger.info(f"Collected {len(all_news)} news items for {context.ticker}")
        return context


class DatabaseStorageOperator(ContextOperator):
    """Operator that stores news items in the database."""
    
    def __init__(self, database: AlertDatabase):
        super().__init__("database_storage")
        self.db = database
        
    def execute(self, context):
        """Store news items in the database."""
        context.update_state(current_operation="storing_in_database")
        
        # Store all news items
        for item in context.news_items:
            if not hasattr(item, 'db_id'):  # Only store if not already stored
                news_id = self.db.store_news_item(item)
                if news_id:
                    item['db_id'] = news_id
        
        logger.info(f"Stored news items in database for {context.ticker}")
        return context


class SentimentAnalysisOperator(ContextOperator):
    """Operator that analyzes sentiment of news items."""
    
    def __init__(self):
        super().__init__("sentiment_analysis")
        # We'll implement the actual sentiment analysis in Step 4
        
    def execute(self, context):
        """Analyze sentiment of unprocessed news items."""
        context.update_state(current_operation="analyzing_sentiment")
        
        # Get unprocessed items
        unprocessed = context.get_unprocessed_items()
        logger.info(f"Analyzing sentiment for {len(unprocessed)} news items")
        
        # Placeholder for sentiment analysis
        # We'll implement this in the next step
        
        return context


class AlertGenerationOperator(ContextOperator):
    """Operator that generates alerts for negative news."""
    
    def __init__(self, database: AlertDatabase):
        super().__init__("alert_generation")
        self.db = database
        
    def execute(self, context):
        """Generate alerts for negative news items."""
        context.update_state(current_operation="generating_alerts")
        
        # Get negative items
        negative_items = context.get_negative_items()
        logger.info(f"Found {len(negative_items)} negative news items for {context.ticker}")
        
        # Placeholder for alert generation
        # We'll implement this in a later step
        
        return context
        

class AlertGenerationOperator(ContextOperator):
    """Operator that generates alerts for significant news items."""
    
    def __init__(self, database):
        super().__init__("alert_generation")
        self.db = database
        self.issue_creator = GitHubIssueCreator()
        
    def execute(self, context):
        """Generate alerts for both negative and positive news items."""
        context.update_state(current_operation="generating_alerts")
        
        # Get negative items
        negative_items = context.get_negative_items()
        
        # Get positive items
        positive_items = context.get_positive_items()
        
        # Process both types of alerts
        items_to_alert = negative_items + positive_items
        
        if not items_to_alert:
            logger.info(f"No significant news items to alert for {context.ticker}")
            return context
        
        logger.info(f"Generating alerts for {len(items_to_alert)} significant news items")
        
        # Create GitHub issues for each item
        for item in items_to_alert:
            # Check if we have already created an alert for this item
            # (In a real system, we would check the database here)
            
            if 'db_id' in item and self.db.alert_exists_for_news(item['db_id']):
                logger.info(f"Alert already exists for news item (ID: {item['db_id']})")
                continue

            # Create the issue
            issue_url = self.issue_creator.create_issue(item)
            
            if issue_url:
                # Store the alert in the database
                if 'db_id' in item:
                    alert_title = f"{'Positive' if item.get('is_positive', False) else 'Negative'} Alert: {item.get('title', 'Untitled')}"
                    self.db.store_alert(
                        news_id=item['db_id'],
                        ticker=item['ticker'],
                        title=alert_title,
                        github_issue_url=issue_url
                    )
                
                # Add the alert to the context
                context.add_alert({
                    'news_id': item.get('db_id'),
                    'ticker': item['ticker'],
                    'title': item['title'],
                    'sentiment': item.get('sentiment', 'unknown'),
                    'github_issue_url': issue_url
                })
        
        return context