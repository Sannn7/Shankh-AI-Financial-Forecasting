
import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict
import yfinance as yf
from datetime import datetime
import joblib
import os




def get_plot_data(ticker: str, quarterly_file_path: str, model_path: str = None) -> Dict:
    
    try:
        # Validate quarterly file existence
        if not os.path.exists(quarterly_file_path):
            raise ValueError(f"Quarterly data file not found at {quarterly_file_path}")

        # Load and process quarterly data
        df = pd.read_csv(quarterly_file_path)
        df["Date"] = pd.to_datetime(df["Date"])
        df["Quarter"] = df["Date"].dt.to_period("Q")
        df = df.sort_values("Quarter")

        # Define financial indicators
        financial_indicators = [
            "Total Revenue", "Oper Rev", "Other Income", "Operating Expenses",
            "Operating Profit", "Profit Before Tax", "Tax", "Net Profit",
            "Basic EPS", "Net profit TTM", "Basic EPS TTM", "Qavg_ATR_14"
        ]

        # Validate required columns
        required_columns = financial_indicators + ["Date", "Qavg_Close", "Qstd_Close", "Prev_Qavg_Close", "Prev_Qstd_Close"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if df.columns:
            raise ValueError(f"Missing required columns in quarterly data: {missing_columns}")

        # Create lagged features
        for col in financial_indicators:
            df[f"Lagged_{col}"] = df[col].shift(1)

        # Drop NA
        df = df.dropna()

        # Define features and target
        features = [f"Lagged_{col}" for col in financial_indicators] + ["Prev_Qavg_Close", "Prev_Qstd_Close"]
        target = "Qavg_Close"

        # Split train and test
        train_df = df.iloc[:-1]
        test_df = df.iloc[-1:]

        X_train = train_df[features]
        y_train = train_df[target]
        X_test = test_df[features]

        # Load or train XGBoost model
        if model_path and os.path.exists(model_path):
            model = joblib.load(model_path)
        else:
            model = XGBRegressor(n_estimators=50, max_depth=2, learning_rate=0.05, random_state=42)
            model.fit(X_train, y_train)

        # Predict for all historical quarters
        df["Predicted_Qavg_Close"] = model.predict(df[features])

        # Calculate ranges
        df["Lower_Bound"] = df["Predicted_Qavg_Close"] - df["Qstd_Close"]
        df["Upper_Bound"] = df["Predicted_Qavg_Close"] + df["Qstd_Close"]

        # Predict for next quarter
        last_quarter = df.iloc[-1]
        next_quarter = pd.DataFrame({
            "Quarter": [last_quarter["Quarter"] + 1],
            "Prev_Qavg_Close": [last_quarter["Qavg_Close"]],
            "Prev_Qstd_Close": [last_quarter["Qstd_Close"]],
            **{f"Lagged_{col}": [last_quarter[col]] for col in financial_indicators}
        })

        next_quarter["Predicted_Qavg_Close"] = model.predict(next_quarter[features])
        next_quarter["Lower_Bound"] = next_quarter["Predicted_Qavg_Close"] - last_quarter["Qstd_Close"]
        next_quarter["Upper_Bound"] = next_quarter["Predicted_Qavg_Close"] + last_quarter["Qstd_Close"]
        next_quarter["Qstd_Close"] = last_quarter["Qstd_Close"]

        # Append next quarter
        df = pd.concat([df, next_quarter], ignore_index=True)

        # Determine yfinance ticker format
        yf_ticker = ticker
        if not yf_ticker.endswith((".NS", ".BO")):  # Assume NSE if no suffix provided
            yf_ticker = f"{yf_ticker}.NS"

        # Fetch daily data from yfinance
        stock = yf.Ticker(yf_ticker)
        df_daily = stock.history(start="2021-01-01", end=datetime.now().strftime("%Y-%m-%d"))
        if df_daily.empty:
            raise ValueError(f"No daily data found for ticker {yf_ticker} on yfinance")
        
        df_daily = df_daily.reset_index()
        df_daily["Date"] = pd.to_datetime(df_daily["Date"])
        df_daily["Quarter"] = df_daily["Date"].dt.to_period("Q")
        df_daily = df_daily[["Date", "Close"]]  # Select only required columns

        # Prepare daily data for plotting
        daily_data = [
            {"date": row["Date"].strftime("%Y-%m-%d"), "close": float(row["Close"])}
            for _, row in df_daily.iterrows()
        ]

        # Prepare quarterly data for plotting
        quarterly_data = []
        for _, row in df.iterrows():
            # Get start and end dates for the quarter
            quarter_daily = df_daily[df_daily["Quarter"] == row["Quarter"]]
            start_date = quarter_daily["Date"].min().strftime("%Y-%m-%d") if not quarter_daily.empty else None
            end_date = quarter_daily["Date"].max().strftime("%Y-%m-%d") if not quarter_daily.empty else None

            # For future quarters, estimate dates
            if pd.isna(start_date) or pd.isna(end_date):
                quarter_str = str(row["Quarter"])
                year, q = int(quarter_str[:4]), int(quarter_str[-1])
                start_month = (q - 1) * 3 + 1
                start_date = f"{year}-{start_month:02d}-01"
                end_month = start_month + 2
                end_date = f"{year}-{end_month:02d}-28"  # Approximate end of quarter

            quarterly_data.append({
                "quarter": str(row["Quarter"]),
                "predicted_close": float(row["Predicted_Qavg_Close"]),
                "lower_bound": float(row["Lower_Bound"]),
                "upper_bound": float(row["Upper_Bound"]),
                "start_date": start_date,
                "end_date": end_date
            })

        return {
            "ticker": ticker,
            "daily_data": daily_data,
            "quarterly_data": quarterly_data
        }

    except Exception as e:
        print("error",e)
        raise e