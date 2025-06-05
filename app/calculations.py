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
        combined_data["UPROM Cumulative"] = (1 + combined_data["UPROM Daily Return"]).cumprod() * 100
        combined_data = combined_data[combined_data.index >= current_start_date]

    else:
        for ticker in tickers:

            stock_data = yf.download(ticker, start=start_date, end=end_date)
            if stock_data.empty:
                print(f"Warning: No data found for {ticker}. Skipping...")
                continue  

            stock_data["Daily Return"] = stock_data["Close"].pct_change()
            combined_data[f"{ticker} Daily Return"] = stock_data["Daily Return"]
            combined_data[f"{ticker} Cumulative"] = (1 + combined_data[f"{ticker} Daily Return"]).cumprod() * 100
            current_start_date = max(current_start_date, stock_data.index[0])
            combined_data = combined_data[combined_data.index >= current_start_date]

    return combined_data, current_start_date




def simulate_holdings_return(combined_data, profile_results, initial_investment, daily_investment):


    if "Contributions" not in combined_data.columns:
        combined_data["Contributions"] = 0.0  # initialize with zeros    

    #                            (all tickers,        all allocation)  
    for ticker, allocation in zip(profile_results[0], profile_results[1]):
        
        daily_value = initial_investment * allocation
        daily_returns = combined_data[f"{ticker} Daily Return"].fillna(0)
        
        # Make sure the column exists (create if not)
        if f"{ticker} Portfolio Value" not in combined_data.columns:
            combined_data[f"{ticker} Portfolio Value"] = 0.0  # initialize with zeros
        
        for i in range(len(daily_returns)):
            r = daily_returns.iloc[i]
            daily_value = (daily_value + (daily_investment * allocation)) * (1 + r)
            combined_data.at[combined_data.index[i], f"{ticker} Portfolio Value"] = daily_value
            combined_data.at[combined_data.index[i], "Contributions"] = daily_investment

    return combined_data

def profile_portfolio_calc(combined_data):
    pass



def max_drawdown_calc(combined_data):

    profile_return = combined_data['Profile Portfolio Value'] - combined_data['Contributions']
    combined_data["Profile Portfolio Return"] = profile_return

    peak_return = profile_return.iloc[0]  # Start with the first value as the peak
    peak_value = combined_data["Profile Portfolio Return"].iloc[0]
    drawdowns = []  # Store drawdown values
    down_days = []  # Store consecutive down days
    drawdown_counter = 0

    for i in range(len(combined_data)):
        current_value = profile_return.iloc[i]

        if current_value > peak_return:
            peak_return = current_value  # Update peak if a new high is reached
            peak_value = combined_data["Profile Portfolio Value"].iloc[i]

            drawdown_counter = 0  # Reset down days counter
        else:
            drawdown_counter += 1  # Count consecutive down days
        
        # Calculate drawdown as a percentage
        drawdown = (peak_return - current_value) / peak_value if peak_return != 0 else 0
        drawdowns.append(drawdown)
        down_days.append(drawdown_counter)

    combined_data["Max Drawdown"] = drawdowns
    combined_data["Down Days"] = down_days
    
    return combined_data

