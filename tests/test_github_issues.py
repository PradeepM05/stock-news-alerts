import sys
import os
import logging
from datetime import datetime

# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.alerts import GitHubIssueCreator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_github_issues():
    """
    Test GitHub issue creation.
    Note: This requires GITHUB_TOKEN and GITHUB_REPOSITORY env variables.
    """
    # Check if we have the necessary environment variables
    if not os.environ.get('GITHUB_TOKEN') or not os.environ.get('GITHUB_REPOSITORY'):
        logger.warning("GITHUB_TOKEN or GITHUB_REPOSITORY not set. This test will only simulate issue creation.")
    
    # Create the issue creator
    issue_creator = GitHubIssueCreator()
    
    # Sample alert data
    positive_alert = {
        'ticker': 'AAPL',
        'title': 'Apple Reports Record Q3 Revenue',
        'sentiment': 'positive',
        'confidence': 0.92,
        'reasoning': 'Strong iPhone sales and services growth exceeded market expectations.',
        'key_factors': [
            'Revenue up 15% year-over-year',
            'iPhone sales exceeded estimates by 12%',
            'Services grew by 21%',
            'Positive guidance for Q4'
        ],
        'market_impact': 'Likely positive short-term price movement',
        'action_recommendation': 'Consider increasing position if aligned with investment strategy',
        'time_horizon': 'short-term',
        'url': 'https://example.com/apple-q3-earnings',
        'source': 'Financial Times',
        'published': datetime.now()
    }
    
    negative_alert = {
        'ticker': 'MSFT',
        'title': 'Microsoft Cloud Division Growth Slows',
        'sentiment': 'negative',
        'confidence': 0.85,
        'reasoning': 'Azure growth rate declined for the third consecutive quarter, below analyst expectations.',
        'key_factors': [
            'Azure growth at 28%, down from 35% last quarter',
            'Cloud division missed revenue targets',
            'Competitive pressure from AWS cited as a factor',
            'Operating margins decreased by 2 percentage points'
        ],
        'market_impact': 'Expected negative pressure on stock price',
        'action_recommendation': 'Monitor closely for further deterioration',
        'time_horizon': 'medium-term',
        'url': 'https://example.com/microsoft-cloud-slowdown',
        'source': 'Bloomberg',
        'published': datetime.now()
    }
    
    # Test issue creation
    logger.info("Testing positive alert GitHub issue creation")
    positive_url = issue_creator.create_issue(positive_alert)
    
    if positive_url:
        logger.info(f"Created positive alert issue: {positive_url}")
    else:
        logger.info("Simulated positive alert issue creation (no actual issue created)")
    
    logger.info("Testing negative alert GitHub issue creation")
    negative_url = issue_creator.create_issue(negative_alert)
    
    if negative_url:
        logger.info(f"Created negative alert issue: {negative_url}")
    else:
        logger.info("Simulated negative alert issue creation (no actual issue created)")

if __name__ == "__main__":
    test_github_issues()