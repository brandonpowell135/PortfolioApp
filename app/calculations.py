import yfinance as yf
import pandas as pd
import numpy as np

def retrieve_stock_data(tickers, start_date, end_date):
    combined_data = pd.DataFrame()
    current_start_date = pd.Timestamp('1900-01-01')  


    if "UPROM" in tickers:
        stock_data = yf.download("^GSPC", start=start_date, end=end_date)
        stock_data["Daily Return"] = stock_data["Close"].pct_change()
        current_start_date = max(current_start_date, stock_data.index[0])
        combined_data["UPROM Daily Return"] = (stock_data["Daily Return"] * 3) + 0.00010
        combined_data = combined_data[combined_data.index >= current_start_date]

    else:
        for ticker in tickers:

            stock_data = yf.download(ticker, start=start_date, end=end_date)
            if stock_data.empty:
                print(f"Warning: No data found for {ticker}. Skipping...")
                continue  

            stock_data["Daily Return"] = stock_data["Close"].pct_change()
            combined_data[f"{ticker} Daily Return"] = stock_data["Daily Return"]
            current_start_date = max(current_start_date, stock_data.index[0])
            combined_data = combined_data[combined_data.index >= current_start_date]

    return combined_data, current_start_date


def simulate_holdings_return(combined_data, profile_results, initial_investment, daily_investment):
   
    combined_data['Contributions'] = daily_investment
    combined_data["Profile Portfolio Value"] = 0.0

    for ticker, allocation in zip(profile_results[0], profile_results[1]):
        
        daily_value = initial_investment * allocation
        daily_returns = combined_data[f"{ticker} Daily Return"].fillna(0)
                
        for i in range(len(daily_returns)):
            r = daily_returns.iloc[i]
            daily_value = (daily_value + (daily_investment * allocation)) * (1 + r)
            combined_data.at[combined_data.index[i], f"{ticker} Portfolio Value"] = daily_value

        combined_data["Profile Portfolio Value"] += combined_data[f"{ticker} Portfolio Value"] 

    return combined_data

def max_drawdown_calc(combined_data, initial_investment):

    total_contributions = initial_investment
    combined_data["Profile Portfolio Return"] = 0.0
    combined_data["Drawdown's"] = 0.0
    combined_data["Down Days"] = 0

    for i in range(len(combined_data)):
        total_contributions += combined_data['Contributions'].iloc[i]
        combined_data.at[combined_data.index[i], "Profile Portfolio Return"] = combined_data["Profile Portfolio Value"].iloc[i] - total_contributions
        combined_data.at[combined_data.index[i], "Drawdown's"] = combined_data["Profile Portfolio Return"].iloc[i] / total_contributions


    peak_return = combined_data["Profile Portfolio Return"].iloc[0]  # Start with the first value as the peak
    peak_value = combined_data["Profile Portfolio Value"].iloc[0]
    drawdown_counter = 0
    max_drawdown = 0

    for i in range(len(combined_data)):
        current_return = combined_data["Profile Portfolio Return"].iloc[i]
        current_value = combined_data["Profile Portfolio Value"].iloc[i]

        if current_return >= peak_return:
            peak_return = current_return  # Update peak if a new high is reached
            drawdown_counter = 0  # Reset down days counter
        else:
            drawdown_counter += 1  # Count consecutive down days

        if current_value >= peak_value:
            peak_value = current_value
        else:
            drawdown = (current_value - peak_value) / peak_value
            max_drawdown = min(drawdown, max_drawdown)

        combined_data.at[combined_data.index[i], "Down Days"] = drawdown_counter

    max_drawdown_duration = combined_data["Down Days"].max()
    max_drawdown=max_drawdown*100
    
    return combined_data, total_contributions, max_drawdown, max_drawdown_duration

