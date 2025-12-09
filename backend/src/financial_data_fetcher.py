import yfinance as yf

def fetch_financial_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        
        # Fetch income statement and get the latest available date
        income_statement = stock.financials
        
        if income_statement.empty:
            raise ValueError(f"❌ No financial data available for '{ticker}'")
        
        # Get the latest available date
        latest_date = income_statement.columns[0]
        latest_data = income_statement[latest_date]

        # Extract only important fields
        financial_data = {
            "date": latest_date.strftime('%Y-%m-%d'),
            "total_revenue": latest_data.get("Total Revenue"),
            "net_income": latest_data.get("Net Income"),
            "ebitda": latest_data.get("EBITDA"),
            "gross_profit": latest_data.get("Gross Profit"),
            "operating_income": latest_data.get("Operating Income"),
            "operating_expense": latest_data.get("Operating Expense"),
            "interest_expense": latest_data.get("Interest Expense"),
            "pretax_income": latest_data.get("Pretax Income"),
            "tax_provision": latest_data.get("Tax Provision"),
            "diluted_eps": latest_data.get("Diluted EPS"),
            "basic_eps": latest_data.get("Basic EPS")
        }

        # Remove any None values (to clean up output)
        financial_data = {k: v for k, v in financial_data.items() if v is not None}

        return financial_data

    except Exception as e:
        print(f"❌ Error fetching financial data: {e}")
        return None
