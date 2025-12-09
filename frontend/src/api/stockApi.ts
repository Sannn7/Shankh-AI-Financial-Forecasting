
import { toast } from "sonner";

// Define types for our API responses
export interface StockDataPoint {
  Date: string;
  Open: number;
  High: number;
  Low: number;
  Close: number;
  Volume: number;
  Dividends: number;
  "Stock Splits": number;
}

export interface StockDataResponse {
  status: string;
  ticker: string;
  data: StockDataPoint[];
}

export interface PredictionResponse {
  ticker: string;
  previous_day_price: number;
  signal: number;
  predicted_price: number;
}

export interface Tweet {
  "Tweet ID": number;
  User: string;
  Text: string;
  "Created At": string;
  tweet_url: string;
}

export interface SentimentResponse {
  ticker: string;
  sentiment_score: number; // Raw score from -1 to 1
  signal: string; // "Positive", "Negative", "Neutral"
  tweets: Tweet[];
}

export interface FinancialData {
  date: string;
  total_revenue: number;
  net_income: number;
  ebitda: number;
  gross_profit: number;
  operating_income: number;
  operating_expense: number;
  interest_expense: number;
  pretax_income: number;
  tax_provision: number;
  diluted_eps: number;
  basic_eps: number;
}

export interface FinancialDataResponse {
  ticker: string;
  financial_data: FinancialData;
}

export interface StockSearchResult {
  ticker: string;
  name: string;
}

// Mock data for company search
export const NIFTY_500_COMPANIES: StockSearchResult[] = [
  { ticker: "RELIANCE.NS", name: "Reliance Industries Ltd." },
  { ticker: "INFY.NS", name: "Infosys Ltd." },
  { ticker: "TCS.NS", name: "Tata Consultancy Services Ltd." },
  { ticker: "HDFCBANK.NS", name: "HDFC Bank Ltd." },
  { ticker: "ICICIBANK.NS", name: "ICICI Bank Ltd." },
  { ticker: "KOTAKBANK.NS", name: "Kotak Mahindra Bank Ltd." },
  { ticker: "HINDUNILVR.NS", name: "Hindustan Unilever Ltd." },
  { ticker: "ITC.NS", name: "ITC Ltd." },
  { ticker: "SBIN.NS", name: "State Bank of India" },
  { ticker: "BHARTIARTL.NS", name: "Bharti Airtel Ltd." },
  { ticker: "BAJFINANCE.NS", name: "Bajaj Finance Ltd." },
  { ticker: "ASIANPAINT.NS", name: "Asian Paints Ltd." },
  { ticker: "AXISBANK.NS", name: "Axis Bank Ltd." },
  { ticker: "AARTIDRUGS.NS", name: "Aarti Drugs Ltd." },
  { ticker: "INDIGO.NS", name: "InterGlobe Aviation Ltd." },
];

// Base API URL - would be replaced with real API endpoint
// const API_BASE_URL = "https://fork-fcrit-2025-stockprediction.onrender.com";
const API_BASE_URL = "http://localhost:8000";

/**
 * Fetch stock data for a given ticker
 */
export const fetchStockData = async (
  ticker: string,
  period: string = "1y",
  interval: string = "1d"
): Promise<StockDataResponse> => {
  try {
    // In a real app, this would be an actual API call
    const response = await fetch(`${API_BASE_URL}/fetch-data`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ticker, period, interval }),
    });
    return await response.json();

    // // For now, return mock data
    // return {
    //   status: "success",
    //   ticker,
    //   data: generateMockStockData(ticker, 365),
    // };
  } catch (error) {
    console.error("Error fetching stock data:", error);
    toast.error("Failed to fetch stock data");
    throw error;
  }
};

/**
 * Get price prediction for a given ticker
 */
export const getPrediction = async (
  ticker: string
): Promise<PredictionResponse> => {
  try {
    // In a real app, this would be an actual API call
    const response = await fetch(`${API_BASE_URL}/next_day_pred`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ticker }),
    });
    return await response.json();

    // For now, return mock data
    // const mockPreviousPrice = Math.round(Math.random() * 500) + 100;
    // let percentChange = (Math.random() * 20) - 10; // -10% to +10%
    // const mockPredictedPrice = mockPreviousPrice * (1 + percentChange / 100);
    
    // return {
    //   ticker,
    //   previous_day_price: mockPreviousPrice,
    //   predicted_price: Math.round(mockPredictedPrice * 100) / 100,
    // };
  } catch (error) {
    console.error("Error getting prediction:", error);
    toast.error("Failed to get prediction");
    throw error;
  }
};

/**
 * Get sentiment data for a given ticker
 */
export const getSentiment = async (
  ticker: string
): Promise<SentimentResponse> => {
  try {
    // In a real app, this would be an actual API call
    const response = await fetch(`${API_BASE_URL}/sentiment-and-tweets/${ticker}/`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    });
    return await response.json();

    // // For now, return mock data
    // const sentiments = [-1, 0, 1];
    // const randomSentiment = sentiments[Math.floor(Math.random() * sentiments.length)];
    
    // return {
    //   ticker,
    //   sentiment: randomSentiment,
    // };
  } catch (error) {
    console.error("Error getting sentiment:", error);
    toast.error("Failed to get sentiment data");
    throw error;
  }
};

/**
 * Get financial data for a given ticker
 */
export const getFinancialData = async (
  ticker: string
): Promise<FinancialDataResponse> => {
  try {
    // In a real app, this would be an actual API call
    const response = await fetch(`${API_BASE_URL}/get-financial-data/${ticker}`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    });
    return await response.json();

    // For now, return mock data
    // return {
    //   ticker,
    //   financial_data: {
    //     date: new Date().toISOString().split('T')[0],
    //     total_revenue: Math.random() * 1000000000000,
    //     net_income: Math.random() * 100000000000,
    //     ebitda: Math.random() * 300000000000,
    //     gross_profit: Math.random() * 200000000000,
    //     operating_income: Math.random() * 150000000000,
    //     operating_expense: Math.random() * 50000000000,
    //     interest_expense: Math.random() * 50000000000,
    //     pretax_income: Math.random() * 100000000000,
    //     tax_provision: Math.random() * 20000000000 * (Math.random() > 0.5 ? 1 : -1),
    //     diluted_eps: Math.random() * 500,
    //     basic_eps: Math.random() * 500,
    //   },
    // };
  } catch (error) {
    console.error("Error getting financial data:", error);
    toast.error("Failed to get financial data");
    throw error;
  }
};

/**
 * Generate mock stock data
 */
function generateMockStockData(ticker: string, days: number): StockDataPoint[] {
  const data: StockDataPoint[] = [];
  const today = new Date();
  let price = Math.random() * 500 + 100; // Starting price between 100 and 600
  
  for (let i = days; i > 0; i--) {
    const date = new Date(today);
    date.setDate(today.getDate() - i);
    
    // Random daily change (-3% to +3%)
    const dailyChange = (Math.random() * 6) - 3;
    price = price * (1 + dailyChange / 100);
    
    const open = price;
    const close = price * (1 + (Math.random() * 2 - 1) / 100);
    const high = Math.max(open, close) * (1 + Math.random() / 100);
    const low = Math.min(open, close) * (1 - Math.random() / 100);
    
    data.push({
      Date: date.toISOString(),
      Open: open,
      High: high,
      Low: low,
      Close: close,
      Volume: Math.floor(Math.random() * 10000000),
      Dividends: 0,
      "Stock Splits": 0,
    });
  }
  
  return data;
}
