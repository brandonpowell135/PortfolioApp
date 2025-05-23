import yfinance as yf
import pandas as pd

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




def simulate_holdings_return(combined_data, tickers, initial_investment, weekly_investment, allocation, rebalance):

    portfolio_stock_value = {ticker: [] for ticker in tickers}
    portfolio_value = []
    total_contributions = []
    new_contributions = initial_investment  # Start with initial investment
    total_portfolio_value = initial_investment

    # Allocate initial investment based on allocation
    portfolio_stock_return = {ticker: initial_investment * allocation[i] for i, ticker in enumerate(tickers)}

    # Ensure first week's investment is added
    last_week = combined_data.index[0].isocalendar()[1]  # Get week number of first data point

    for i in range(len(combined_data)):
        current_week = combined_data.index[i].isocalendar()[1]  # Get week number

        # Detect new week (including first entry)
        if i == 0 or current_week != last_week:
            new_contributions += weekly_investment  # Add weekly investment
            for ticker in tickers:
                portfolio_stock_return[ticker] += weekly_investment * allocation[tickers.index(ticker)]
            last_week = current_week  # Update last processed week

        # Apply daily returns
        for ticker in tickers:
            if i > 0:
                portfolio_stock_return[ticker] *= (1 + combined_data[f"{ticker} Daily Return"].iloc[i])

        # Rebalancing logic
        if i % rebalance == 0 and i > 0:
            total_portfolio_value = sum(portfolio_stock_return.values())
            for ticker in tickers:
                target_value = total_portfolio_value * allocation[tickers.index(ticker)]
                portfolio_stock_return[ticker] = target_value

        # Track portfolio values
        total_portfolio_value = sum(portfolio_stock_return.values())
        portfolio_value.append(total_portfolio_value)
        total_contributions.append(new_contributions)

        for ticker in tickers:
            portfolio_stock_value[ticker].append(portfolio_stock_return[ticker])

    # Store values in DataFrame
    for ticker in tickers:
        combined_data[f"{ticker} Portfolio Value"] = portfolio_stock_value[ticker]

    combined_data["Profile Portfolio Value"] = portfolio_value
    combined_data["Contributions"] = total_contributions

    return combined_data




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

