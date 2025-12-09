
import { useEffect, useRef, useState } from 'react';
import { 
  ResponsiveContainer, 
  ComposedChart, 
  Line, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend,
  Area,
  ReferenceLine
} from 'recharts';
import { StockDataPoint } from '@/api/stockApi';
import { CalendarRange, TrendingUp, ZoomIn } from 'lucide-react';
import { cn } from '@/lib/utils';

interface StockChartProps {
  data: StockDataPoint[];
  ticker: string;
  className?: string;
}

type TimeRange = '1M' | '3M' | '6M' | '1Y' | 'ALL';

export default function StockChart({ data, ticker, className }: StockChartProps) {
  const [timeRange, setTimeRange] = useState<TimeRange>('1M');
  const [chartData, setChartData] = useState<any[]>([]);
  const [showCandlestick, setShowCandlestick] = useState(true);
  const [lastClosePrice, setLastClosePrice] = useState<number | null>(null);
  
  // Format data for chart
  useEffect(() => {
    if (!data || data.length === 0) return;
    
    // Filter data based on selected time range
    let filteredData: StockDataPoint[] = [];
    const today = new Date();
    
    switch (timeRange) {
      case '1M':
        const oneMonthAgo = new Date();
        oneMonthAgo.setMonth(today.getMonth() - 1);
        filteredData = data.filter(item => new Date(item.Date) >= oneMonthAgo);
        break;
      case '3M':
        const threeMonthsAgo = new Date();
        threeMonthsAgo.setMonth(today.getMonth() - 3);
        filteredData = data.filter(item => new Date(item.Date) >= threeMonthsAgo);
        break;
      case '6M':
        const sixMonthsAgo = new Date();
        sixMonthsAgo.setMonth(today.getMonth() - 6);
        filteredData = data.filter(item => new Date(item.Date) >= sixMonthsAgo);
        break;
      case '1Y':
        const oneYearAgo = new Date();
        oneYearAgo.setFullYear(today.getFullYear() - 1);
        filteredData = data.filter(item => new Date(item.Date) >= oneYearAgo);
        break;
      case 'ALL':
      default:
        filteredData = [...data];
        break;
    }
    
    // Format data for chart
    const formattedData = filteredData.map(item => {
      // Format date for display
      const date = new Date(item.Date);
      const formattedDate = date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
      });
      
      // Calculate if it's an up or down day
      const isUp = item.Close >= item.Open;
      
      return {
        date: formattedDate,
        fullDate: date,
        open: item.Open,
        high: item.High,
        low: item.Low,
        close: item.Close,
        volume: item.Volume,
        isUp,
      };
    });
    
    setChartData(formattedData);
    
    // Set last close price
    if (filteredData.length > 0) {
      const lastData = filteredData[filteredData.length - 1];
      setLastClosePrice(lastData.Close);
    }
  }, [data, timeRange]);
  
  // Custom tooltip for the chart
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      
      return (
        <div className="glass-dark dark:glass-dark glass-light light:glass-light p-3 rounded-md border border-border shadow-md">
          <p className="label font-semibold">{label}</p>
          <div className="mt-2 space-y-1">
            <p className="text-sm">
              <span className="text-muted-foreground">Open: </span>
              <span className="font-medium">{data.open.toFixed(2)}</span>
            </p>
            <p className="text-sm">
              <span className="text-muted-foreground">High: </span>
              <span className="font-medium">{data.high.toFixed(2)}</span>
            </p>
            <p className="text-sm">
              <span className="text-muted-foreground">Low: </span>
              <span className="font-medium">{data.low.toFixed(2)}</span>
            </p>
            <p className="text-sm">
              <span className="text-muted-foreground">Close: </span>
              <span className={cn(
                "font-medium",
                data.isUp ? "text-success" : "text-destructive"
              )}>
                {data.close.toFixed(2)}
              </span>
            </p>
            <p className="text-sm">
              <span className="text-muted-foreground">Volume: </span>
              <span className="font-medium">{data.volume.toLocaleString()}</span>
            </p>
          </div>
        </div>
      );
    }
  
    return null;
  };
  
  // Render candlestick bar
  const renderCandlestick = (props: any) => {
    const { x, y, width, height, open, close } = props;
    const isUp = close > open;
    
    return (
      <rect
        x={x - width / 2}
        y={y}
        width={width}
        height={Math.abs(height)}
        fill={isUp ? 'hsl(var(--success))' : 'hsl(var(--destructive))'}
      />
    );
  };
  
  return (
    <div className={cn("p-4 rounded-xl bg-card", className)}>
      <div className="flex flex-col">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-2xl font-bold animate-fade-in">{ticker}</h3>
            {lastClosePrice && (
              <div className="text-xl font-medium mt-2 flex items-center gap-2 animate-fade-in">
                <span>{lastClosePrice.toFixed(2)}</span>
                <TrendingUp className="h-5 w-5 text-success" />
              </div>
            )}
          </div>
          
          <div className="flex space-x-2">
            <button
              onClick={() => setShowCandlestick(!showCandlestick)}
              className={`px-3 py-1.5 rounded-md text-sm font-medium ${
                showCandlestick 
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-muted text-muted-foreground hover:bg-muted/80'
              }`}
            >
              <div className="flex items-center gap-1">
                <CalendarRange className="h-4 w-4" />
                <span>{showCandlestick ? 'Candlestick' : 'Line Only'}</span>
              </div>
            </button>
          </div>
        </div>
      
        <div className="bg-card/50 p-1 mb-4 rounded-lg flex justify-between">
          {(['1M', '3M', '6M', '1Y', 'ALL'] as TimeRange[]).map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all ${
                timeRange === range
                  ? 'bg-primary text-primary-foreground shadow-sm'
                  : 'hover:bg-muted/50'
              }`}
            >
              {range}
            </button>
          ))}
        </div>

        <div className="h-[300px] w-full animate-fade-in" style={{ overflow: 'visible' }}>
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart
              data={chartData}
              margin={{ top: 20, right: 20, bottom: 20, left: 20 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" opacity={0.3} />
              <XAxis 
                dataKey="date" 
                tickLine={false} 
                axisLine={{ stroke: 'hsl(var(--border))' }}
                tick={{ fill: 'hsl(var(--muted-foreground))' }}
              />
              <YAxis 
                yAxisId="left"
                domain={['auto', 'auto']}
                tickLine={false}
                axisLine={{ stroke: 'hsl(var(--border))' }}
                tick={{ fill: 'hsl(var(--muted-foreground))' }}
              />
              <YAxis 
                yAxisId="right"
                orientation="right"
                domain={['auto', 'auto']}
                tickLine={false}
                axisLine={{ stroke: 'hsl(var(--border))' }}
                tick={{ fill: 'hsl(var(--muted-foreground))' }}
              />
              
              <Tooltip content={<CustomTooltip />} />
              
              {showCandlestick && (
                <>
                  {/* High-Low lines */}
                  {chartData.map((entry, index) => (
                    <line
                      key={`line-${index}`}
                      x1={index * (100 / chartData.length) + (100 / chartData.length) / 2 + '%'}
                      x2={index * (100 / chartData.length) + (100 / chartData.length) / 2 + '%'}
                      y1={entry.low}
                      y2={entry.high}
                      stroke={entry.isUp ? 'hsl(var(--success))' : 'hsl(var(--destructive))'}
                      strokeWidth={1}
                    />
                  ))}
                  
                  {/* Candlesticks */}
                  <Bar
                    dataKey="open"
                    yAxisId="left"
                    barSize={8}
                    shape={renderCandlestick}
                  />
                </>
              )}
              
              <Line
                type="monotone"
                dataKey="close"
                yAxisId="left"
                stroke="hsl(var(--accent))"
                dot={false}
                strokeWidth={2}
                style={{ filter: 'drop-shadow(0 0 2px hsl(var(--accent-foreground)))' }}
              />
              
              <Legend />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
