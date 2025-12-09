import yfinance as yf
import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
import ta
from datetime import datetime, timedelta
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense, LSTM, Bidirectional, Dot, Activation
import os
import io


def format_float(value):
    if np.isnan(value):
        return None  # Replace NaN with None
    if np.isinf(value):
        return None  # Replace inf/-inf with None
    return round(float(value), 3)


def get_stocks_data(ticker, start_date, end_date):
    try:
        ticker_symbol = ticker
        # Convert dates to string format
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')

        print("Start Date:", start_date_str)
        print("End Date:", end_date_str)

        # Fetch the data using yfinance
        ticker_obj = yf.Ticker(ticker_symbol)
        df = ticker_obj.history(start=start_date_str, end=end_date_str)

        # Select only OHLC columns and reset index to include Date as a column
        ohlc_data = df[['Open', 'High', 'Low', 'Close', 'Volume']].reset_index()

        # Rename 'Date' column to ensure consistency
        ohlc_data.rename(columns={'Date': 'Date'}, inplace=True)

        # Save to CSV
        output_path = f"data/{ticker}_OHLCV.csv"  # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        ohlc_data.to_csv(output_path, index=False)
        print("end",ohlc_data.tail(2));
        print("start",ohlc_data.head(2));
        
        print(f"OHLC data for {ticker_symbol} saved to {output_path}")
        return ohlc_data
    
    except Exception as e:
        print(f"Error in get_stocks_data: {e}")
        raise e


def get_quarter(date):
    """Convert a date to its corresponding quarter (e.g., '2023Q1')."""
    year = date.year
    quarter = (date.month - 1) // 3 + 1
    return f"{year}Q{quarter}"


def load_financial_signals(ticker):
    """Load financial signals from CSV for the given ticker."""
    try:
        company_name = ticker.split(".")[0]
        signals_file = os.path.join("financial_signals", f"{company_name}_predictions_signals.csv")
        if not os.path.exists(signals_file):
            print(f"Financial signals file not found: {signals_file}")
            return None
        signals_df = pd.read_csv(signals_file)
        # Create a dictionary mapping quarters to signals
        signals_dict = dict(zip(signals_df['Quarter'], signals_df['Signal']))
        return signals_dict
    except Exception as e:
        print(f"Error loading financial signals: {e}")
        return None


def technical_predictions(ticker, OHLCV_DATA):
    try:
        # Paths and inputs
        output_folder = "outputs"
        models_folder = "models"
        company_name = ticker.split(".")[0]

        # Load financial signals
        financial_signals = load_financial_signals(ticker)

        # Attention layer (needed to load the model)
        def attention_layer(lstm_output):
            attention = Dense(1, activation='tanh')(lstm_output)
            attention = Activation('sigmoid')(attention)
            context = Dot(axes=1)([attention, lstm_output])
            return context

        # Load data
        df = OHLCV_DATA
        df.set_index('Date', inplace=True)
        print(df.tail())

        # Add Adj Close (approximate as Close if not available)
        df['Adj Close'] = df['Close']  # Assuming no adjustments; replace with actual data if available

        # Add technical indicators (consistent with training)
        df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()
        stochastic = ta.momentum.StochasticOscillator(df['High'], df['Low'], df['Close'], window=14, smooth_window=3)
        df['Stochastic_K'] = stochastic.stoch()
        df['Stochastic_D'] = stochastic.stoch_signal()
        df['Williams_%R'] = ta.momentum.WilliamsRIndicator(df['High'], df['Low'], df['Close'], lbp=14).williams_r()
        df['MFI'] = ta.volume.MFIIndicator(df['High'], df['Low'], df['Close'], df['Volume'], window=14).money_flow_index()
        df['AD_Line'] = ta.volume.AccDistIndexIndicator(df['High'], df['Low'], df['Close'], df['Volume']).acc_dist_index()
        df['OBV'] = ta.volume.OnBalanceVolumeIndicator(df['Close'], df['Volume']).on_balance_volume()
        df.dropna(inplace=True)

        # Prepare X and y
        X = df.drop(columns=['Close']).values  # Shape: (n_rows, 12) with Adj Close
        y = df['Close'].values

        # Scale features
        scaler_X = MinMaxScaler()
        X_scaled = scaler_X.fit_transform(X)  # Shape: (n_rows, 12)
        scaler_y = MinMaxScaler()
        y_scaled = scaler_y.fit_transform(y.reshape(-1, 1))

        # Load selected features
        selected_features_path = os.path.join(models_folder, f"{company_name}_features.npy")
        if not os.path.exists(selected_features_path):
            raise FileNotFoundError(f"Selected features file not found: {selected_features_path}")
        selected_features = np.load(selected_features_path)

        # Debugging
        print("X_scaled shape:", X_scaled.shape)
        print("Selected features:", selected_features)
        print("Max index in selected_features:", selected_features.max())

        # Ensure all indices are valid
        n_features = X_scaled.shape[1]
        if selected_features.max() >= n_features:
            raise ValueError(f"Feature mismatch: Selected features index ({selected_features.max()}) exceeds available columns ({n_features}).")

        X_selected = X_scaled[:, selected_features]  # Shape: (n_rows, 10)

        # Create sequences (time_steps=10, consistent with training)
        time_steps = 10
        X_seq = []
        for i in range(len(X_selected) - time_steps):
            X_seq.append(X_selected[i:i + time_steps])
        X_seq = np.array(X_seq)  # Shape: (n_rows - 10, 10, 10)

        # Load model
        model_path = os.path.join(models_folder, f"{company_name}.h5")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        model = tf.keras.models.load_model(
            model_path,
            custom_objects={'attention_layer': attention_layer, 'mse': tf.keras.losses.MeanSquaredError()}
        )

        # Predict
        y_pred_scaled = model.predict(X_seq)  # Shape: (samples, timesteps, 1)
        y_pred_scaled = y_pred_scaled[:, -1, :]  # Take last timestep: (samples, 1)
        y_pred = scaler_y.inverse_transform(y_pred_scaled).flatten()

        # Load standard deviation and mean residuals
        predicted_df_path = os.path.join(models_folder, "predicted.csv")
        if not os.path.exists(predicted_df_path):
            raise FileNotFoundError(f"Predicted CSV file not found: {predicted_df_path}")
        predicted_df = pd.read_csv(predicted_df_path)
        company_stats = predicted_df[predicted_df['Company'] == company_name]
        if company_stats.empty:
            raise ValueError(f"No stats found for company: {company_name}")
        std_dev = company_stats['Std_Dev'].values[0]
        mean_residuals = company_stats['Mean_Residuals'].values[0]

        # Adjust predictions based on mean residuals
        if mean_residuals > 0:
            adjusted_pred = y_pred + std_dev
            adjustment_direction = "added"
        else:
            adjusted_pred = y_pred - std_dev
            adjustment_direction = "subtracted"

        print(f"Mean Residuals: {mean_residuals:.4f}, Std_Dev: {std_dev:.4f}, Adjustment: {adjustment_direction}")

        # Generate results
        results = []
        backtest_results = []
        for i in range(time_steps, len(df)):
            date = df.index[i]
            actual_close = y[i - time_steps]
            pred_idx = i - time_steps
            predicted_close = y_pred[pred_idx]
            adjusted_predicted_close = adjusted_pred[pred_idx]
            prev_actual_close = y[i - time_steps - 1] if i > time_steps else np.nan

            if np.isnan(prev_actual_close):
                technical_signal = None  # Replace NaN with None for JSON compatibility
            else:
                diff = abs(adjusted_predicted_close - prev_actual_close)
                if diff <= 0.05 * prev_actual_close:
                    technical_signal = 0  # Hold
                elif adjusted_predicted_close > prev_actual_close:
                    technical_signal = 1  # Buy
                else:
                    technical_signal = -1  # Sell

            # Get financial signal for the date's quarter
            financial_signal = None
            if financial_signals:
                quarter = get_quarter(date)
                financial_signal = financial_signals.get(quarter)

            # Calculate final signal (80% technical, 20% financial)
            final_signal = technical_signal
            if financial_signal is not None and technical_signal is not None:
                # Ensure signals are numeric for weighting
                weighted_signal = (0.8 * technical_signal) + (0.2 * financial_signal)
                # Round to nearest signal value (-1, 0, 1)
                if weighted_signal > 0.5:
                    final_signal = 1
                elif weighted_signal < -0.5:
                    final_signal = -1
                else:
                    final_signal = 0

            # Convert date to timezone-naive string
            date_str = date.strftime('%Y-%m-%d %H:%M:%S') if isinstance(date, pd.Timestamp) else str(date)

            results.append({
                'Date': date_str,
                'Actual_Close': format_float(actual_close),
                'Predicted_Close': format_float(predicted_close),
                'prev_actual_close': format_float(prev_actual_close),
                'Adjusted_Predicted_Close': format_float(adjusted_predicted_close),
                'Technical_Signal': technical_signal,
                'Financial_Signal': financial_signal,
                'Final_Signal': final_signal
            })

            if (final_signal):
                backtest_results.append({
                    'Date': date_str.split(" ")[0],f"{ticker}": final_signal
                })

        # Save results
        os.makedirs(output_folder, exist_ok=True)
        results_df = pd.DataFrame(backtest_results)
        output_file = os.path.join(output_folder, f"technical_{ticker}_predictions.csv")
        results_df.to_csv(output_file, index=False, na_rep='')  # Use empty string for None/NaN in CSV

        print(f"Predictions saved to {output_file}")
        return backtest_results  # Return as list of dicts for JSON compatibility

    except Exception as e:
        print(f"Error in technical_predictions: {e}")
        raise e
    

def signal_generate(ticker):
    try:
        # Fetch stock data
        start_date = datetime(2021, 7, 7)
        # Define today's date
        today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        # Calculate the previous quarter's end date
        def get_previous_quarter_end(date):
            month = (date.month - 1) // 3 * 3
            if month == 0:
                return datetime(date.year - 1, 12, 31)
            else:
                return datetime(date.year, month, 1) - timedelta(days=1)

        end_date = get_previous_quarter_end(today)

        input_data = get_stocks_data(ticker, start_date, end_date)
        # Generate signals using technical predictions
        signals = technical_predictions(ticker, input_data)
        return signals
    except Exception as e:
        print(f"Error in signal_generate: {e}")
        raise e


def next_day_pred(ticker):
    try:
        # Paths and inputs
        output_folder = "outputs"  # Path to model, features, and metrics
        models_folder = "models"

        company_name = ticker.split(".")[0]  # Replace with your company name
        today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        # Set end_date as the previous day's date
        # end_date = today + timedelta(days=1)
        end_date = today 

        # Set start_date as 100 days before end_date
        start_date = end_date - timedelta(days=100)
        
        ohlcv_data = get_stocks_data(ticker, start_date, end_date)  # Path to input OHLCV CSV

        # Attention layer (needed to load the model)
        def attention_layer(lstm_output):
            attention = Dense(1, activation='tanh')(lstm_output)
            attention = Activation('sigmoid')(attention)
            context = Dot(axes=1)([attention, lstm_output])
            return context

        # Load data
        df = ohlcv_data
        df.set_index('Date', inplace=True)

        # Add technical indicators (consistent with training)
        df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()
        stochastic = ta.momentum.StochasticOscillator(df['High'], df['Low'], df['Close'], window=14, smooth_window=3)
        df['Stochastic_K'] = stochastic.stoch()
        df['Stochastic_D'] = stochastic.stoch_signal()
        df['Williams_%R'] = ta.momentum.WilliamsRIndicator(df['High'], df['Low'], df['Close'], lbp=14).williams_r()
        df['MFI'] = ta.volume.MFIIndicator(df['High'], df['Low'], df['Close'], df['Volume'], window=14).money_flow_index()
        df['AD_Line'] = ta.volume.AccDistIndexIndicator(df['High'], df['Low'], df['Close'], df['Volume']).acc_dist_index()
        df['OBV'] = ta.volume.OnBalanceVolumeIndicator(df['Close'], df['Volume']).on_balance_volume()

        # Add Adj Close to match training data structure
        df['Adj Close'] = df['Close']  # Approximate; replace with actual data if available
        df.dropna(inplace=True)

        # Prepare X
        X = df.drop(columns=['Close']).values  # Shape: (n_rows, 12) with Adj Close

        # Scale features
        scaler_X = MinMaxScaler()
        X_scaled = scaler_X.fit_transform(X)  # Note: Ideally, load training scaler

        # Load selected features
        selected_features = np.load(os.path.join(models_folder, f"{company_name}_features.npy"))

        # Validate features
        n_features = X_scaled.shape[1]
        if selected_features.max() >= n_features:
            raise ValueError(f"Feature indices ({selected_features.max()}) exceed available columns ({n_features}).")

        X_selected = X_scaled[:, selected_features]  # Shape: (n_rows, 10)

        # Create sequence for the last time_steps days
        time_steps = 10
        if len(X_selected) < time_steps:
            raise ValueError(f"Input data has {len(X_selected)} rows, but at least {time_steps} are required.")

        # Take the last time_steps rows for prediction
        X_seq = X_selected[-time_steps:].reshape(1, time_steps, X_selected.shape[1])  # Shape: (1, 10, 10)

        # Load model
        model_path = os.path.join(models_folder, f"{company_name}.h5")
        model = tf.keras.models.load_model(
            model_path,
            custom_objects={'attention_layer': attention_layer, 'mse': tf.keras.losses.MeanSquaredError()}
        )

        # Predict next day's close
        y_pred_scaled = model.predict(X_seq)  # Shape: (1, timesteps, 1)
        y_pred_scaled = y_pred_scaled[0, -1, :]  # Take last timestep: (1,)
        scaler_y = MinMaxScaler()
        scaler_y.fit(df['Close'].values.reshape(-1, 1))  # Fit scaler for inverse transform
        y_pred = scaler_y.inverse_transform(y_pred_scaled.reshape(1, -1))[0, 0]  # Scalar value

        # Load standard deviation and mean residuals
        predicted_df = pd.read_csv(os.path.join(models_folder, "predicted.csv"))
        std_dev = predicted_df[predicted_df['Company'] == company_name]['Std_Dev'].values[0]
        mean_residuals = predicted_df[predicted_df['Company'] == company_name]['Mean_Residuals'].values[0]

        # Adjust prediction
        if mean_residuals > 0:
            adjusted_pred = y_pred + std_dev
            adjustment_direction = "added"
        else:
            adjusted_pred = y_pred - std_dev
            adjustment_direction = "subtracted"

        # Generate trading signal
        last_close = df['Close'].iloc[-1]
        diff = abs(adjusted_pred - last_close)
        if diff <= 0.034 * last_close:
            signal = 0  # HOLD
        elif adjusted_pred > last_close:
            signal = 1  # BUy
        else:
            signal = -1  # Sell

        # Output results
        result = {
            'Company': company_name,
            'Date': df.index[-1],  # Last date in input
            'Next_Day_Predicted_Close': float(y_pred),
            'Next_Day_Adjusted_Predicted_Close': float(adjusted_pred),
            'Signal': signal,
            'Adjustment': adjustment_direction
        }

        print("Prediction Result:",result)
        
        apiResult={
            "predicted_price":float(adjusted_pred),
            "previous_day_price":float(last_close),
            "signal":signal,
            "ticker":ticker
        }


        return apiResult
    except Exception as e:
        print("error in next_day_pred", e)
        raise e