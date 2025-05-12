# src/analysis/sentiment.py
import logging
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

# Download NLTK data if not already present
try:
    nltk.data.find('vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')

class SentimentAnalyzer:
    """Simple VADER-based sentiment analyzer for financial news"""
    
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()
    
    def analyze(self, news_item: Dict[str, Any], threshold: float = 0.7) -> Dict[str, Any]:
        """Analyze sentiment of a news item"""
        title = news_item.get('title', '')
        summary = news_item.get('summary', '')
        
        # Use title twice to give it more weight, plus summary
        text = f"{title}. {title}. {summary}"
        
        # Get VADER sentiment
        vader_scores = self.vader.polarity_scores(text)
        compound_score = vader_scores['compound']
        
        # Determine sentiment and confidence
        if compound_score >= 0.3:
            sentiment = "positive"
            confidence = min(0.9, 0.5 + compound_score * 0.5)
        elif compound_score <= -0.2:
            sentiment = "negative"
            confidence = min(0.9, 0.5 + abs(compound_score) * 0.5)
        else:
            sentiment = "neutral"
            confidence = 0.6
        
        # Determine if positive/negative based on threshold
        is_positive = sentiment == "positive" and confidence >= threshold
        is_negative = sentiment == "negative" and confidence >= threshold
        
        # Log significant sentiment
        if is_positive or is_negative:
            logger.info(f"{sentiment.upper()} news ({confidence:.2f}): {title}")
        
        # Create result
        result = {
            "sentiment": sentiment,
            "confidence": confidence,
            "sentiment_score": compound_score,
            "is_positive": is_positive,
            "is_negative": is_negative,
            "reasoning": f"VADER compound score: {compound_score:.2f}",
            "key_factors": [f"VADER scores: {vader_scores}"],
            "market_impact": "Potential market impact" if is_positive or is_negative else "Minimal market impact",
            "action_recommendation": "Review for opportunity" if is_positive else "Monitor closely" if is_negative else "No action needed",
            "time_horizon": "short-term" if abs(compound_score) > 0.5 else "medium-term"
        }
        
        return result
    
    def analyze_batch(self, news_items: List[Dict[str, Any]], threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Analyze a batch of news items"""
        results = []
        
        for item in news_items:
            # Add sentiment analysis results
            enhanced_item = item.copy()
            sentiment_results = self.analyze(item, threshold)
            enhanced_item.update(sentiment_results)
            results.append(enhanced_item)
        
        # Log batch summary
        positive_count = sum(1 for item in results if item.get('is_positive', False))
        negative_count = sum(1 for item in results if item.get('is_negative', False))
        
        logger.info(f"Batch analysis results: {positive_count} positive, {negative_count} negative, {len(results)-positive_count-negative_count} neutral items")
        
        return results