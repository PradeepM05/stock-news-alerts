import sqlite3
import logging
import os
from datetime import datetime
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)

class AlertDatabase:
    """
    SQLite database for storing news items and tracking alert history.
    """
    
    def __init__(self, db_path):
        """
        Initialize database connection.
        
        Args:
            db_path (str): Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self.ensure_dir_exists()
    
    def ensure_dir_exists(self):
        """Ensure the directory for the database file exists."""
        directory = os.path.dirname(self.db_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
    
    def initialize(self):
        """
        Initialize the database schema if it doesn't exist.
        """
        try:
            self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()
            
            # Create news_items table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS news_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id TEXT UNIQUE,
                ticker TEXT NOT NULL,
                source TEXT NOT NULL,
                title TEXT NOT NULL,
                summary TEXT,
                url TEXT NOT NULL,
                published TIMESTAMP NOT NULL,
                sentiment_score REAL,
                is_negative BOOLEAN,
                processed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Create alerts table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                news_id INTEGER NOT NULL,
                ticker TEXT NOT NULL,
                title TEXT NOT NULL,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                github_issue_url TEXT,
                FOREIGN KEY (news_id) REFERENCES news_items (id)
            )
            ''')
            
            self.conn.commit()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            if self.conn:
                self.conn.close()
                self.conn = None
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def store_news_item(self, news_item):
        """
        Store a news item in the database if it doesn't exist.
        
        Args:
            news_item (dict): News item dictionary
            
        Returns:
            int: ID of the inserted or existing news item, or None on error
        """
        if not self.conn:
            self.initialize()
            
        try:
            cursor = self.conn.cursor()
            
            # Check if the news item already exists
            cursor.execute(
                "SELECT id FROM news_items WHERE source_id = ?",
                (news_item['source_id'],)
            )
            
            existing = cursor.fetchone()
            if existing:
                logger.debug(f"News item already exists: {news_item['title']}")
                return existing[0]
            
            # Insert the news item
            cursor.execute('''
            INSERT INTO news_items (
                source_id, ticker, source, title, summary, url, published,
                sentiment_score, is_negative, processed
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                news_item['source_id'],
                news_item['ticker'],
                news_item['source'],
                news_item['title'],
                news_item['summary'],
                news_item['url'],
                news_item['published'],
                news_item.get('sentiment_score', None),
                news_item.get('is_negative', False),
                False
            ))
            
            self.conn.commit()
            news_id = cursor.lastrowid
            logger.info(f"Stored news item (ID: {news_id}): {news_item['title']}")
            
            return news_id
            
        except Exception as e:
            logger.error(f"Error storing news item: {e}")
            self.conn.rollback()
            return None
    
    def mark_as_processed(self, news_id, sentiment_score=None, is_negative=None):
        """
        Mark a news item as processed with sentiment analysis results.
        
        Args:
            news_id (int): ID of the news item
            sentiment_score (float): Sentiment score from analysis
            is_negative (bool): Whether the news is classified as negative
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.conn:
            self.initialize()
            
        try:
            cursor = self.conn.cursor()
            
            update_fields = ["processed = TRUE"]
            update_values = []
            
            if sentiment_score is not None:
                update_fields.append("sentiment_score = ?")
                update_values.append(sentiment_score)
                
            if is_negative is not None:
                update_fields.append("is_negative = ?")
                update_values.append(is_negative)
            
            update_query = f'''
            UPDATE news_items SET {', '.join(update_fields)}
            WHERE id = ?
            '''
            
            update_values.append(news_id)
            cursor.execute(update_query, update_values)
            
            self.conn.commit()
            logger.info(f"Marked news item (ID: {news_id}) as processed")
            
            return True
            
        except Exception as e:
            logger.error(f"Error marking news item as processed: {e}")
            self.conn.rollback()
            return False
    
    def store_alert(self, news_id, ticker, title, github_issue_url=None):
        """
        Store an alert for a negative news item.
        
        Args:
            news_id (int): ID of the news item
            ticker (str): Stock ticker symbol
            title (str): Alert title
            github_issue_url (str): URL of the GitHub issue created
            
        Returns:
            int: ID of the inserted alert, or None on error
        """
        if not self.conn:
            self.initialize()
            
        try:
            cursor = self.conn.cursor()
            
            cursor.execute('''
            INSERT INTO alerts (news_id, ticker, title, github_issue_url)
            VALUES (?, ?, ?, ?)
            ''', (news_id, ticker, title, github_issue_url))
            
            self.conn.commit()
            alert_id = cursor.lastrowid
            logger.info(f"Stored alert (ID: {alert_id}): {title}")
            
            return alert_id
            
        except Exception as e:
            logger.error(f"Error storing alert: {e}")
            self.conn.rollback()
            return None
    
    def get_unprocessed_news(self, ticker=None):
        """
        Get unprocessed news items for a ticker or all tickers.
        
        Args:
            ticker (str, optional): Stock ticker symbol
            
        Returns:
            list: List of unprocessed news items
        """
        if not self.conn:
            self.initialize()
            
        try:
            cursor = self.conn.cursor()
            
            if ticker:
                cursor.execute('''
                SELECT id, source_id, ticker, source, title, summary, url, published
                FROM news_items
                WHERE ticker = ? AND processed = FALSE
                ORDER BY published DESC
                ''', (ticker,))
            else:
                cursor.execute('''
                SELECT id, source_id, ticker, source, title, summary, url, published
                FROM news_items
                WHERE processed = FALSE
                ORDER BY published DESC
                ''')
            
            rows = cursor.fetchall()
            
            news_items = []
            for row in rows:
                news_items.append({
                    'id': row[0],
                    'source_id': row[1],
                    'ticker': row[2],
                    'source': row[3],
                    'title': row[4],
                    'summary': row[5],
                    'url': row[6],
                    'published': row[7]
                })
            
            return news_items
            
        except Exception as e:
            logger.error(f"Error retrieving unprocessed news: {e}")
            return []
    
    def get_negative_news(self, ticker=None, days=1):
        """
        Get negative news items for a ticker or all tickers from the last N days.
        
        Args:
            ticker (str, optional): Stock ticker symbol
            days (int): Number of days to look back
            
        Returns:
            list: List of negative news items
        """
        if not self.conn:
            self.initialize()
            
        try:
            cursor = self.conn.cursor()
            
            if ticker:
                cursor.execute('''
                SELECT id, ticker, source, title, summary, url, published, sentiment_score
                FROM news_items
                WHERE ticker = ? AND is_negative = TRUE AND
                      datetime(published) > datetime('now', '-' || ? || ' days')
                ORDER BY published DESC
                ''', (ticker, days))
            else:
                cursor.execute('''
                SELECT id, ticker, source, title, summary, url, published, sentiment_score
                FROM news_items
                WHERE is_negative = TRUE AND
                      datetime(published) > datetime('now', '-' || ? || ' days')
                ORDER BY published DESC
                ''', (days,))
            
            rows = cursor.fetchall()
            
            news_items = []
            for row in rows:
                news_items.append({
                    'id': row[0],
                    'ticker': row[1],
                    'source': row[2],
                    'title': row[3],
                    'summary': row[4],
                    'url': row[5],
                    'published': row[6],
                    'sentiment_score': row[7]
                })
            
            return news_items
            
        except Exception as e:
            logger.error(f"Error retrieving negative news: {e}")
            return []
        
    def clean_old_data(self, days_to_keep=30):
        """
        Remove news items and alerts older than the specified number of days.
        
        Args:
            days_to_keep (int): Number of days of data to retain
            
        Returns:
            int: Number of records deleted
        """
        if not self.conn:
            self.initialize()
            
        try:
            cursor = self.conn.cursor()
            
            # First, delete old alerts
            cursor.execute('''
            DELETE FROM alerts 
            WHERE news_id IN (
                SELECT id FROM news_items
                WHERE datetime(published) < datetime('now', '-' || ? || ' days')
            )
            ''', (days_to_keep,))
            
            alerts_deleted = cursor.rowcount
            
            # Then delete old news items
            cursor.execute('''
            DELETE FROM news_items
            WHERE datetime(published) < datetime('now', '-' || ? || ' days')
            ''', (days_to_keep,))
            
            news_deleted = cursor.rowcount
            
            self.conn.commit()
            logger.info(f"Cleaned {alerts_deleted} old alerts and {news_deleted} old news items")
            
            return alerts_deleted + news_deleted
            
        except Exception as e:
            logger.error(f"Error cleaning old data: {e}")
            self.conn.rollback()
            return 0
        
    def alert_exists_for_news(self, news_id):
        """
        Check if an alert already exists for a news item.
        
        Args:
            news_id (int): ID of the news item
            
        Returns:
            bool: True if an alert exists, False otherwise
        """
        if not self.conn:
            self.initialize()
            
        try:
            cursor = self.conn.cursor()
            
            cursor.execute(
                "SELECT COUNT(*) FROM alerts WHERE news_id = ?",
                (news_id,)
            )
            
            count = cursor.fetchone()[0]
            return count > 0
            
        except Exception as e:
            logger.error(f"Error checking for existing alert: {e}")
            return False