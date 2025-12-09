import { useState, useEffect } from 'react';
import {
  fetchStockData,
  getPrediction,
  getSentiment,
  getFinancialData,
  StockDataResponse,
  PredictionResponse,
  SentimentResponse,
  FinancialDataResponse,
} from '@/api/stockApi';
import { toast } from "sonner";
import { ThemeProvider } from '@/contexts/ThemeContext';
import ThemeToggle from '@/components/ThemeToggle';
import SearchableDropdown from '@/components/SearchableDropdown';
import StockChart from '@/components/StockChart';
import PredictionCard from '@/components/PredictionCard';
import SentimentIndicator from '@/components/SentimentIndicator';
import FinancialMetrics from '@/components/FinancialMetrics';
import { LineChart, Sparkles, Search } from 'lucide-react';

interface SentimentIndicatorProps {
  sentiment: SentimentResponse;
  className?: string;
}





export default function Index() {
  const [selectedTicker, setSelectedTicker] = useState<string | null>(null);
  const [stockData, setStockData] = useState<StockDataResponse | null>(null);
  const [prediction, setPrediction] = useState<PredictionResponse | null>(null);
  const [sentiment, setSentiment] = useState<SentimentResponse | null>(null);
  const [financialData, setFinancialData] = useState<FinancialDataResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const handleTickerSelect = async (ticker: string) => {
    setLoading(true);
    setSelectedTicker(ticker);

    try {
      const [stockDataRes, predictionRes, sentimentRes, financialDataRes] = await Promise.all([
        fetchStockData(ticker),
        getPrediction(ticker),
        getSentiment(ticker),
        getFinancialData(ticker),
      ]);

      setStockData(stockDataRes);
      setPrediction(predictionRes);
      setSentiment(sentimentRes);
      setFinancialData(financialDataRes);

      toast.success(`Loaded data for ${ticker}`, {
        description: "All market data successfully retrieved",
      });
    } catch (error) {
      console.error("Error fetching stock data:", error);
      toast.error("Failed to load stock data", {
        description: "Please try again or select a different ticker",
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    handleTickerSelect("RELIANCE.NS");
  }, []);

  return (
    <ThemeProvider>
      <div className="min-h-screen bg-background text-foreground transition-colors duration-300">
        <header className="border-b border-border">
          <div className="container mx-auto px-4 py-4 flex justify-between items-center">
            <div className="flex items-center gap-2">
              <Sparkles className="h-6 w-6 text-primary" />
              <h1 className="text-2xl font-bold">ShankhAI</h1>
            </div>
            <ThemeToggle />
          </div>
        </header>

        <main className="container mx-auto px-4 py-6">
          <div className="max-w-2xl mx-auto mb-8">
            <div className="bg-card rounded-xl p-6 border border-border shadow-sm">
              <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                <Search className="h-5 w-5 text-primary" />
                Search For any Nifty 500 stocks
              </h2>
              <SearchableDropdown onSelect={handleTickerSelect} />
            </div>
          </div>

          {loading && (
            <div className="flex justify-center items-center py-20">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
            </div>
          )}

          {!loading && selectedTicker && stockData && (
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              <div className="lg:col-span-8 space-y-6">
                <StockChart data={stockData.data} ticker={selectedTicker} className="shadow-sm" />
                {financialData && (
                  <FinancialMetrics financialData={financialData} className="shadow-sm" />
                )}
              </div>

              <div className="lg:col-span-4 space-y-6">
                {prediction && (
                  <PredictionCard prediction={prediction} />
                )}

                {sentiment && (
                  <SentimentIndicator sentiment={sentiment} />
                )}

                <div className="rounded-xl border bg-card p-6 shadow-sm">
                  <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
                    <LineChart className="h-5 w-5 text-primary" />
                    Market Insights
                  </h3>
                  <ul className="space-y-3 ">
                    {sentiment.tweets.slice(5).map((tweet) => (
                      <li
                        key={tweet["Tweet ID"]}
                        className="group relative flex items-start gap-2 cursor-pointer hover:bg-muted p-2 rounded-md transition-colors"
                        onClick={() => window.open(tweet.tweet_url, '_blank')}
                      >
                        <span className="h-5 w-5 text-primary shrink-0 mt-0.5">•</span>
                        <p className="text-sm">{tweet.Text}</p>
                        <div className="absolute invisible group-hover:visible bg-background border border-border text-muted-foreground text-xs rounded px-2 py-1 -top-6 left-1/2 transform -translate-x-1/2">
                          {tweet.User}
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </ThemeProvider>
  );
}