import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class NewsContext:
    """
    Context object that stores and manages news data throughout the system.
    This serves as the primary context structure in our MCP implementation.
    """
    
    def __init__(self, ticker: str, threshold: float):
        self.ticker = ticker
        self.threshold = threshold
        self.news_items = []
        self.processed_items = []
        self.alerts = []
        self.state = {
            "last_request_time": None,
            "last_processed_id": None,
            "current_operation": None
        }
    
    def add_news_items(self, items: List[Dict[str, Any]]) -> None:
        """Add news items to the context."""
        self.news_items.extend(items)
        logger.debug(f"Added {len(items)} news items to context for {self.ticker}")
    
    def mark_item_processed(self, item_id: str, results: Dict[str, Any]) -> None:
        """Mark an item as processed with analysis results."""
        for item in self.news_items:
            if item['source_id'] == item_id:
                item.update(results)
                self.processed_items.append(item)
                self.state["last_processed_id"] = item_id
                break
    
    def add_alert(self, alert: Dict[str, Any]) -> None:
        """Add an alert to the context."""
        self.alerts.append(alert)
        logger.info(f"Added alert for {self.ticker}: {alert['title']}")
    
    def get_unprocessed_items(self) -> List[Dict[str, Any]]:
        """Get news items that haven't been processed yet."""
        processed_ids = {item['source_id'] for item in self.processed_items}
        return [item for item in self.news_items if item['source_id'] not in processed_ids]
    
    def get_negative_items(self) -> List[Dict[str, Any]]:
        """Get news items classified as negative."""
        return [item for item in self.processed_items if item.get('is_negative', False)]
    
    def update_state(self, **kwargs) -> None:
        """Update context state with new values."""
        self.state.update(kwargs)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the current context state."""
        return {
            "ticker": self.ticker,
            "total_items": len(self.news_items),
            "processed_items": len(self.processed_items),
            "negative_items": len(self.get_negative_items()),
            "alerts": len(self.alerts),
            "current_operation": self.state["current_operation"]
        }