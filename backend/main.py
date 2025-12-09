from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.sentiment_loader import load_sentiment_data
from src.financial_data_fetcher import fetch_financial_data
from src.data_fetcher import fetch_stock_data
from src.twitter_client import TwitterClient
from src.pydanticModels import StockRequest, Ticker
from src.backtesting_signals import signal_generate, next_day_pred
from src.financial_graph import get_plot_data

# Create FastAPI app
app = FastAPI()

# CORS setup
origins = [
    "*",]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create API router
router = APIRouter()

# Initialize Twitter client
twitter_client = TwitterClient()

@app.get("/")
def root():
    return {"status": "Stock Predictor is running"}

@router.post("/backtestingSignals/")
def backtest(ticker: Ticker):
    try:
        signals = signal_generate(ticker.ticker)
        if signals:
            return signals
        else:
            raise HTTPException(status_code=500, detail="No signals generated")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    

@router.post("/next_day_pred")
def next_day(ticker: Ticker):
    try:
        predictions = next_day_pred(ticker.ticker)
        return predictions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

# @router.get("/get-sentiment/{ticker}/")
# def get_sentiment(ticker: str):
#     try:
#         sentiment_data = load_sentiment_data()
#         if not sentiment_data:
#             raise HTTPException(status_code=500, detail="Sentiment data not loaded")

#         sentiment = sentiment_data.get(ticker)
#         if sentiment is None:
#             raise HTTPException(status_code=404, detail=f"Sentiment for ticker '{ticker}' not found")

#         return {
#             "ticker": ticker,
#             "sentiment": sentiment
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")



@router.get("/get-financial-data/{ticker}")
def get_financial_data(ticker: str):
    try:
        financial_data = fetch_financial_data(ticker)
        if financial_data is None:
            raise HTTPException(status_code=404, detail=f"Financial data for ticker '{ticker}' not found")

        return {
            "ticker": ticker,
            "financial_data": financial_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.post("/fetch-data")
def get_stock_data(request: StockRequest):
    try:
        stock_data = fetch_stock_data(request.ticker, request.period, request.interval)
        if stock_data is None:
            raise HTTPException(status_code=404, detail="Stock data not found")

        return {
            "status": "success",
            "ticker": request.ticker,
            "data": stock_data.to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")



@router.get("/sentiment-and-tweets/{ticker}/")
def get_sentiment_and_tweets(ticker: str):
    try:
        result = twitter_client.get_sentiment_and_tweets(ticker, max_results=10)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch sentiment and tweets: {str(e)}")
    


@router.post("/get-plot-data/")
def get_plot_data_endpoint(ticker: Ticker):
    """
    Fetch data for plotting daily closing prices and quarterly predicted price ranges.
    """
    try:
        # Hardcoded file paths (update as needed or make configurable)
        company_name=ticker.ticker.split(".")[0]
        quarterly_file_path = f"data/Quartely_merged/{company_name}_Final_merged.csv"
        
        plot_data = get_plot_data(ticker.ticker, quarterly_file_path)

        return plot_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch plot data: {str(e)}")


# Include router
app.include_router(router)