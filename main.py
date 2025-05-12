import logging
import time
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import datetime
from src.database.storage import AlertDatabase
from src.mcp.context import NewsContext
from src.mcp.controller import MCPController
from src.mcp.operators import (
    NewsCollectionOperator,
    DatabaseStorageOperator,
    SentimentAnalysisOperator,
    AlertGenerationOperator
)
from src.collectors.finviz_scraper import get_finviz_news

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting stock news scan using MCP architecture")
    
    # Load configuration
    try:
        with open('config/stocks.json', 'r') as f:
            config = json.load(f)
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        return
    
    # Initialize database
    db = AlertDatabase('data/alert_history.db')
    db.initialize()
    
    # Initialize MCP controller
    controller = MCPController()
    
    # Register operators
    controller.register_operator(NewsCollectionOperator())
    controller.register_operator(DatabaseStorageOperator(db))
    controller.register_operator(SentimentAnalysisOperator())
    controller.register_operator(AlertGenerationOperator(db))
    
    try:
        # Define the standard processing pipeline
        pipeline = [
            "news_collection",
            "database_storage",
            "sentiment_analysis",
            "alert_generation"
        ]
        
        # Process each stock in watchlist
        for i, stock in enumerate(config['watchlist']):
            # Add delay between stocks (except the first one)
            if i > 0:
                time.sleep(5)  # 5 second delay between stocks
            ticker = stock['ticker']
            threshold = stock.get('threshold', 0.7)
            logger.info(f"Processing stock: {ticker}")
            
            # Create context for this stock
            context = NewsContext(ticker, threshold)
            
            # Process the context through the pipeline
            processed_context = controller.process(context, pipeline)
            
            # Log the final state
            summary = processed_context.get_summary()
            logger.info(f"Completed processing for {ticker}: {summary}")
        
        logger.info("Completed stock news scan")
    
    finally:
        # Ensure database connection is closed
        db.close()

if __name__ == "__main__":
    main()