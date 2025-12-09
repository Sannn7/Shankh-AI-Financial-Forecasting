
import { Heart, ThumbsDown, ThumbsUp } from "lucide-react";
import { cn } from "@/lib/utils";
import { SentimentResponse } from "@/api/stockApi";

interface SentimentIndicatorProps {
  sentiment: SentimentResponse;
  className?: string;
}

export default function SentimentIndicator({ sentiment, className }: SentimentIndicatorProps) {
  let sentimentValue = 0;
  console.log(sentiment.signal);
  

  if (sentiment.signal === "Positive") {
    sentimentValue = 1;
  } else if (sentiment.signal === "Neutral") {
    sentimentValue = 0;
  } else if (sentiment.signal==="Negative") {
    sentimentValue = -1;
  }
  console.log(sentimentValue);
  
  // Determine sentiment styling and text
  let sentimentColor = "";
  let sentimentText = "";
  let sentimentDescription = "";
  let SentimentIcon = Heart;
  
  switch (sentimentValue) {
    case 1:
      sentimentColor = "text-success";
      sentimentText = "Positive";
      sentimentDescription = "Market sentiment is optimistic about this stock";
      SentimentIcon = ThumbsUp;
      break;
    case 0:
      sentimentColor = "text-warning";
      sentimentText = "Neutral";
      sentimentDescription = "Mixed market sentiment for this stock";
      SentimentIcon = Heart;
      break;
    case -1:
      sentimentColor = "text-destructive";
      sentimentText = "Negative";
      sentimentDescription = "Market sentiment is pessimistic about this stock";
      SentimentIcon = ThumbsDown;
      break;
  }
  
  return (
    <div className={cn(
      "rounded-xl border bg-card p-6 card-hover animate-scale-in",
      className
    )}>
      <h3 className="text-xl font-semibold mb-4">Market Sentiment</h3>
      
      <div className="flex flex-col items-center justify-center p-4">
        <div className={cn(
          "w-24 h-24 rounded-full flex items-center justify-center mb-4 animate-pulse-slow",
          sentimentValue === 1 ? "bg-success/20" : 
          sentimentValue === 0 ? "bg-warning/20" : "bg-destructive/20"
        )}>
          <SentimentIcon className={cn(
            "h-12 w-12", 
            sentimentColor
          )} />
        </div>
        
        <div className="text-center">
          <h4 className={cn("text-xl font-bold mb-1", sentimentColor)}>
            {sentimentText}
          </h4>
          <p className="text-sm text-muted-foreground">
            {sentimentDescription}
          </p>
        </div>
      </div>
      
      <div className="mt-4 pt-4 border-t border-border">
        <div className="flex justify-between">
          <span className="text-sm font-medium">Sentiment Score</span>
          <span className={cn(
            "text-sm font-bold",
            sentimentColor
          )}>
            {sentimentValue === 1 ? "+1" : sentimentValue}
          </span>
        </div>
        
        <div className="mt-2 w-full h-2 bg-muted rounded-full overflow-hidden">
          <div 
            className={cn(
              "h-full",
              sentimentValue === 1 ? "bg-success" : 
              sentimentValue === 0 ? "bg-warning" : "bg-destructive"
            )} 
            style={{ 
              width: `${((sentimentValue + 1) / 2) * 100}%`,
              transition: "width 1s ease-in-out"
            }}
          />
        </div>
        
        <div className="flex justify-between mt-1 text-xs text-muted-foreground">
          <span>Bearish</span>
          <span>Neutral</span>
          <span>Bullish</span>
        </div>
      </div>
    </div>
  );
}
