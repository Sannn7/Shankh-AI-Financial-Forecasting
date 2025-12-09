
import { BarChart3, DollarSign,IndianRupeeIcon, TrendingUp, Activity } from "lucide-react";
import { FinancialDataResponse } from "@/api/stockApi";
import { cn } from "@/lib/utils";

interface FinancialMetricsProps {
  financialData: FinancialDataResponse;
  className?: string;
}

export default function FinancialMetrics({ financialData, className }: FinancialMetricsProps) {
  const { financial_data } = financialData;
  
  const formatCurrency = (value: number): string => {
    if (value >= 1_00_00_00_000) {
      return `₹${(value / 1_00_00_00_000).toFixed(2)}T`; // Trillion
    } else if (value >= 1_00_00_000) {
      return `₹${(value / 1_00_00_000).toFixed(2)}C`; // Crore
    } else if (value >= 1_00_000) {
      return `₹${(value / 1_00_000).toFixed(2)}L`; // Lakh
    } else {
      return `₹${value?.toLocaleString("en-IN", { minimumFractionDigits: 2 })}`;
    }
  };

  
  // Group metrics into cards
  const metrics = [
    {
      title: "Revenue & Income",
      icon: IndianRupeeIcon,
      color: "text-info",
      bgColor: "bg-info/10",
      items: [
        { label: "Total Revenue", value: formatCurrency(financial_data.total_revenue) },
        { label: "Net Income", value: formatCurrency(financial_data.net_income) },
        { label: "Gross Profit", value: formatCurrency(financial_data.gross_profit) },
      ],
    },
    {
      title: "Operational Metrics",
      icon: Activity,
      color: "text-success",
      bgColor: "bg-success/10",
      items: [
        { label: "EBITDA", value: formatCurrency(financial_data.ebitda) },
        { label: "Operating Income", value: formatCurrency(financial_data.operating_income) },
        { label: "Operating Expense", value: formatCurrency(financial_data.operating_expense) },
      ],
    },
    {
      title: "Profit Metrics",
      icon: TrendingUp,
      color: "text-warning",
      bgColor: "bg-warning/10",
      items: [
        { label: "Pretax Income", value: formatCurrency(financial_data.pretax_income) },
        { label: "Tax Provision", value: formatCurrency(financial_data.tax_provision) },
        { label: "Interest Expense", value: formatCurrency(financial_data.interest_expense) },
      ],
    },
    {
      title: "Per Share Data",
      icon: BarChart3,
      color: "text-primary",
      bgColor: "bg-primary/10",
      items: [
        { label: "Diluted EPS", value: `₹${financial_data.diluted_eps.toFixed(2)}` },
        { label: "Basic EPS", value: `₹${financial_data.basic_eps.toFixed(2)}` },
        { label: "Report Date", value: financial_data.date },
      ],
    },
  ];
  
  return (
    <div className={cn("rounded-xl border bg-card p-6", className)}>
      <h3 className="text-xl font-semibold mb-4">Financial Metrics</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {metrics.map((metric, index) => (
          <div 
            key={metric.title}
            className={cn(
              "rounded-lg border p-4 animate-fade-in",
              metric.bgColor,
              "border-border/50 card-hover",
              { "animation-delay-200": index === 1 },
              { "animation-delay-400": index === 2 },
              { "animation-delay-600": index === 3 },
            )}
            style={{ 
              animationDelay: `${index * 150}ms`,
              animationFillMode: "backwards" 
            }}
          >
            <div className="flex items-center gap-2 mb-3">
              <div className={cn(
                "p-2 rounded-full",
                metric.bgColor
              )}>
                <metric.icon className={cn("h-5 w-5", metric.color)} />
              </div>
              <h4 className="font-medium">{metric.title}</h4>
            </div>
            
            <div className="space-y-2">
              {metric.items.map((item) => (
                <div key={item.label} className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">{item.label}</span>
                  <span className="font-medium text-right">{item.value}</span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
