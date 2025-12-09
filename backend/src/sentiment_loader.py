import os
import pandas as pd

# Path to sentiment data
SENTIMENT_FILE = os.path.join(os.path.dirname(__file__), '../sentiment.csv')

def load_sentiment_data():
    try:
        if not os.path.exists(SENTIMENT_FILE):
            raise FileNotFoundError(f"❌ Sentiment file not found at {SENTIMENT_FILE}")
        
        sentiment_df = pd.read_csv(SENTIMENT_FILE)
        
        if 'ticker' not in sentiment_df.columns or 'Sentiment' not in sentiment_df.columns:
            raise ValueError("❌ Missing required columns in sentiment file (ticker, Sentiment).")
        
        # Convert DataFrame to dictionary
        sentiment_dict = sentiment_df.set_index('ticker')['Sentiment'].to_dict()
        
        return sentiment_dict
    
    except Exception as e:
        print(f"❌ Error loading sentiment data: {e}")
        return None


# def getSentimentAnalysis(ticker):
    