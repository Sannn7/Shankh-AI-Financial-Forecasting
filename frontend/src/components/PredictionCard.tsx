import { ArrowDownIcon, ArrowUpIcon, TrendingUp, TrendingDown } from 'lucide-react';
import { cn } from '@/lib/utils';
import { PredictionResponse } from '@/api/stockApi';

interface PredictionCardProps {
  prediction: PredictionResponse;
  className?: string;
  currencySymbol?: string; // New prop for currency symbol
}

export default function PredictionCard({
  prediction,
  className,
  currencySymbol = '₹'
}: PredictionCardProps) {
  const { previous_day_price, predicted_price, signal } = prediction;
  console.log(predicted_price,previous_day_price,)
  // Calculate percentage change
  const percentChange = ((predicted_price - previous_day_price) / previous_day_price) * 100;
  const isPositive = signal === 1;
  const isSignificant = signal !== 0;

  // Unified color mapping based on signal
  const getColorStyles = () => {
    switch (signal) {
      case 1: // Buy
        return {
          bg: 'bg-green-100 dark:bg-green-900/30',
          text: 'text-green-700 dark:text-green-300',
          border: 'border-green-200 dark:border-green-800',
          shadow: 'shadow-lg shadow-green-200/50 dark:shadow-green-900/50'
        };
      case -1: // Sell
        return {
          bg: 'bg-red-100 dark:bg-red-900/30',
          text: 'text-red-700 dark:text-red-300',
          border: 'border-red-200 dark:border-red-800',
          shadow: 'shadow-lg shadow-red-200/50 dark:shadow-red-900/50'
        };
      default: // Hold (0)
        return {
          bg: 'bg-yellow-100 dark:bg-yellow-900/30',
          text: 'text-yellow-700 dark:text-yellow-300',
          border: 'border-yellow-200 dark:border-yellow-800',
          shadow: 'shadow-lg shadow-yellow-200/50 dark:shadow-yellow-900/50'
        };
    }
  };

  const { bg, text, border, shadow } = getColorStyles();

  // Signal text and description
  const signalText = isSignificant ? (isPositive ? 'Buy Signal' : 'Sell Signal') : 'Hold Position';
  const signalDescription = isSignificant
    ? isPositive
      ? 'Significant upward movement predicted'
      : 'Significant downward movement predicted'
    : 'Minimal price movement expected';

  return (
    <div
      className={cn(
        'rounded-xl border p-5 transition-all duration-300 hover:scale-105',
        bg,
        border,
        shadow,
        'animate-fade-in',
        className
      )}
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Price Prediction</h3>
        {isSignificant ? (
          isPositive ? (
            <TrendingUp className={cn('h-6 w-6', text)} />
          ) : (
            <TrendingDown className={cn('h-6 w-6', text)} />
          )
        ) : (
          <span className={cn('text-sm font-medium', text)}>↔</span>
        )}
      </div>

      <div className="space-y-3">
        <div className="flex justify-between items-center">
          <span className="text-sm text-muted-foreground">Predicted Price</span>
          <span className={cn('font-bold text-lg', text)}>
            {currencySymbol}{predicted_price.toFixed(2)}
          </span>
        </div>

        <div className="flex justify-between items-center">
          <span className="text-sm text-muted-foreground">Change</span>
          <div className={cn('flex items-center gap-1', text)}>
            <span className="font-semibold">
              {percentChange >= 0 ? '+' : ''}{percentChange.toFixed(2)}%
            </span>
            {percentChange !== 0 && (
              percentChange > 0 ? (
                <ArrowUpIcon className="h-4 w-4" />
              ) : (
                <ArrowDownIcon className="h-4 w-4" />
              )
            )}
          </div>
        </div>
      </div>

      <div className={cn('mt-4 rounded-lg p-3', "bg-white")}>
        <div className="flex flex-col">
          <p className={cn('font-medium', text)}>{signalText}</p>
          <p className="text-xs text-muted-foreground">{signalDescription}</p>
        </div>
      </div>
    </div>
  );
}