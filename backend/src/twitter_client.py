import tweepy
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict, Optional
import google.generativeai as genai
import logging
from time import time
import json
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# List of Twitter API bearer tokens
BEARER_TOKENS = [
    "AAAAAAAAAAAAAAAAAAAAAH8Y0AEAAAAAvZPyi8OytngrJkw4VnBuEZRvBhg%3DdCdduEiACvAiOXJT2Pa6VmDgCkxkdQk9i3b85RYnMZs08fmZLI",
    "AAAAAAAAAAAAAAAAAAAAALI2ywEAAAAAZdEdqcida20%2B7r26UmLQyAdeNpE%3DtHUf7GjcsYIaUkshREHsZf9x7DzY4PvPuN7Aqrs0sRCIbtfeFg",
    "AAAAAAAAAAAAAAAAAAAAAHUY0AEAAAAA2eutirL%2Fu1H1hUWfNq%2FDuEklLWc%3DGnV1NymhsTR6bK102TVb5PFivhmefh17xLOrfMUdxVdgswOrJu",
    "AAAAAAAAAAAAAAAAAAAAIwY0AEAAAAAnlNzwBuMM4Sktx9Mse%2B%2B4wkiQ00%3DdnN177UyIYsSGCeJIQuLjEjOffuEPdLQlbu819vSckWuRfyVHL"
]

# Configure Gemini API
GEMINI_API_KEY = "AIzaSyBnCSigt4BEork20VgJPEA1Lg4qerCRU2g"
genai.configure(api_key=GEMINI_API_KEY)

# Ensure data/tweets_data directory exists
DATA_DIR = "data/tweets_data"
os.makedirs(DATA_DIR, exist_ok=True)

class TwitterClient:
    def __init__(self):
        self.clients = [(tweepy.Client(bearer_token=token), 0) for token in BEARER_TOKENS]  # (client, last_used_timestamp)
        self.current_token_index = 0
        self.tweet_cache = {}  # Cache: {query: (tweets, timestamp)}
        self.cache_duration = 300  # Cache tweets for 5 minutes
        self.cooldown_duration = 900  # 15 minutes cooldown per token

    def get_client(self) -> tweepy.Client:
        return self.clients[self.current_token_index][0]

    def switch_to_next_token(self) -> bool:
        original_index = self.current_token_index
        current_time = time()
        
        # Try the next token until we find one that is not in cooldown or exhaust all tokens
        for _ in range(len(self.clients)):
            self.current_token_index = (self.current_token_index + 1) % len(self.clients)
            last_used = self.clients[self.current_token_index][1]
            if current_time - last_used >= self.cooldown_duration:
                logger.info(f"Switched to bearer token {self.current_token_index + 1}")
                return True
            if self.current_token_index == original_index:
                break
        
        logger.error("All Twitter API tokens are in cooldown")
        return False

    def update_token_timestamp(self):
        """Update the last used timestamp for the current token."""
        current_time = time()
        self.clients[self.current_token_index] = (self.clients[self.current_token_index][0], current_time)

    def search_tweets(self, query: str, max_results: int = 10) -> Optional[List[Dict]]:
        # Check cache first
        current_time = time()
        if query in self.tweet_cache:
            tweets, cache_time = self.tweet_cache[query]
            if current_time - cache_time < self.cache_duration:
                logger.info(f"Returning cached tweets for query: {query}")
                return tweets

        end_time = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        start_time = end_time - timedelta(days=5)  # Twitter API allows 7-day search
        attempts = 0
        max_attempts = len(self.clients)

        while attempts < max_attempts:
            try:
                client = self.get_client()
                tweets = client.search_recent_tweets(
                    query=query,
                    start_time=start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    end_time=end_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    tweet_fields=["created_at", "text", "source"],
                    user_fields=["name", "username", "location", "verified", "description"],
                    max_results=max_results,
                    expansions='author_id'
                )
                parsed_tweets = self.parse_tweepy_response(tweets) if tweets.data else []
                # Cache the results
                self.tweet_cache[query] = (parsed_tweets, current_time)
                self.update_token_timestamp()
                return parsed_tweets
            except tweepy.TweepyException as e:
                if isinstance(e, tweepy.TooManyRequests):
                    logger.warning(f"Rate limit hit with token {self.current_token_index + 1}")
                    if not self.switch_to_next_token():
                        logger.error("All Twitter API tokens are in cooldown")
                        raise Exception("All Twitter API tokens are in cooldown")
                else:
                    logger.error(f"Twitter API error with token {self.current_token_index + 1}: {e}")
                    if not self.switch_to_next_token():
                        logger.error("All Twitter API tokens exhausted")
                        raise Exception("All Twitter API tokens exhausted")
                attempts += 1
        return []

    def parse_tweepy_response(self, response) -> List[Dict]:
        """Parse Tweepy response into a list of dictionaries."""
        tweets = response.data or []
        users = {user.id: user for user in response.includes['users']} if response.includes.get('users') else {}

        parsed_tweets = []
        for tweet in tweets:
            author = users.get(tweet.author_id, None)
            parsed_tweets.append({
                'Tweet ID': tweet.id,
                'User': f"{author.name} (@{author.username})" if author else "Unknown",
                'Text': tweet.text,
                'Created At': tweet.created_at.isoformat(),  # Convert to string for JSON serialization
                'tweet_url': f"https://twitter.com/{author.username}/status/{tweet.id}" if author else None
            })
        return parsed_tweets

    def generate_sentiment(self, tweet_text: str) -> str:
        """Generate sentiment using Gemini API."""
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"Decide whether a Tweet's sentiment is positive, neutral, or negative. Tweet:\n\n{tweet_text}\n\nSentiment:"
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=100
                )
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Error generating sentiment: {e}")
            return "neutral"  # Default to neutral on failure

    def get_sentiment_score(self, sentiment: str) -> int:
        """Convert sentiment text to numerical score."""
        sentiment = sentiment.lower()
        if "positive" in sentiment:
            return 1
        elif "negative" in sentiment:
            return -1
        else:
            return 0

    def save_to_json(self, data: Dict, ticker: str):
        """Save data to JSON file in data/tweets_data directory."""
        try:
            file_path = os.path.join(DATA_DIR, f"{ticker}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            logger.info(f"Saved data to {file_path}")
        except Exception as e:
            logger.error(f"Error saving data to JSON for ticker {ticker}: {e}")

    def load_from_json(self, ticker: str) -> Optional[Dict]:
        """Load data from JSON file in data/tweets_data directory."""
        try:
            file_path = os.path.join(DATA_DIR, f"{ticker}.json")
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                logger.info(f"Loaded data from {file_path}")
                return data
            else:
                logger.warning(f"No saved data found for ticker {ticker}")
                return None
        except Exception as e:
            logger.error(f"Error loading data from JSON for ticker {ticker}: {e}")
            return None

    def get_sentiment_and_tweets(self, ticker: str, max_results: int = 10) -> Dict:
        """Fetch tweets and calculate average sentiment score for a ticker, with fallback to saved data."""
        company_name = ticker.split(".")[0]
        query = f"#{company_name} #stockmarket"
        
        try:
            tweets = self.search_tweets(query, max_results=max_results)
            print("tweets",tweets)
            if not tweets:
                # Try loading from saved data if no tweets are found
                print("loading from saved ones",ticker)
                saved_data = self.load_from_json(ticker)
                print("saved data",saved_data)
                if saved_data:
                    return saved_data
                return {
                    "ticker": ticker,
                    "sentiment_score": 0.0,
                    "signal": "Neutral",
                    "tweets": [],
                    "message": "No tweets found and no saved data available"
                }

            sentiments = [self.generate_sentiment(tweet['Text']) for tweet in tweets]
            scores = [self.get_sentiment_score(sentiment) for sentiment in sentiments]
            average_sentiment = sum(scores) / len(scores) if scores else 0.0

            result = {
                "ticker": ticker,
                "sentiment_score": average_sentiment,
                "signal": "Positive" if average_sentiment > 0 else "Negative" if average_sentiment < 0 else "Neutral",
                "tweets": tweets,
                "message": "Success"
            }

            # Save the result to JSON
            self.save_to_json(result, ticker)
            return result

        except (tweepy.TweepyException, Exception) as e:
            logger.error(f"API error for ticker {ticker}: {e}")
            # Fallback to saved data
            saved_data = self.load_from_json(ticker)
            if saved_data:
                saved_data["message"] = "Returning saved data due to API error"
                return saved_data
            return {
                "ticker": ticker,
                "sentiment_score": 0.0,
                "signal": "Neutral",
                "tweets": [],
                "message": f"API error: {str(e)}, and no saved data available"
            }

# Example usage
if __name__ == "__main__":
    client = TwitterClient()
    result = client.get_sentiment_and_tweets("TSLA", max_results=5)
    print(json.dumps(result, indent=4, ensure_ascii=False))