import yfinance as yf
import pandas as pd


# Function to calculate daily returns and cumulative returns for multiple stocks
def calculate_stock_data(tickers, start_date, end_date):
    combined_data = pd.DataFrame()  # Create an empty DataFrame to store results

    for ticker in tickers:
        # Download stock historical data
        stock_data = yf.download(ticker, start=start_date, end=end_date)
        if stock_data.empty:
            print(f"Warning: No data found for {ticker}. Skipping...")
            continue  # Skip if no data is found

        # Calculate daily returns for the stock
        stock_data["Daily Return"] = stock_data["Close"].pct_change()
        
        # Store daily returns in combined data
        combined_data[f"{ticker} Daily Return"] = stock_data["Daily Return"]

        # Add cumulative returns for each stock, starting with a value of 100
        initial_value = 100
        combined_data[f"{ticker} Cumulative"] = (1 + combined_data[f"{ticker} Daily Return"]).cumprod() * initial_value

    return combined_data

# Function to simulate portfolio return
def simulate_holdings_return(combined_data, tickers, weekly_investment, allocation, rebalance=30):
    portfolio_stock_value = {ticker: [] for ticker in tickers}
    portfolio_value = []
    portfolio_stock_return = {ticker: 0 for ticker in tickers}  # Initial returns

    # Get the corresponding allocation for the stock ticker
    ticker_allocation = {tickers[i]: allocation[i] for i in range(len(tickers))}

    # Loop through each day in the dataset
    for i in range(len(combined_data)):
        # Weekly investments are added every Monday
        if combined_data.index[i].weekday() == 0:  # Monday
            for ticker in tickers:
                portfolio_stock_return[ticker] += weekly_investment * ticker_allocation[ticker]

        # Apply daily returns for each stock
        for ticker in tickers:
            if i > 0:
                portfolio_stock_return[ticker] *= (1 + combined_data[f"{ticker} Daily Return"].iloc[i])

        # Rebalance each stock holdings at the specified interval (e.g., every 30 days)
        if i % rebalance == 0 and i > 0:  # Avoid rebalancing on the first day
            total_portfolio_value = sum(portfolio_stock_return[ticker] for ticker in tickers)
            for ticker in tickers:
                target_value = total_portfolio_value * ticker_allocation[ticker]
                portfolio_stock_return[ticker] = target_value

        # Store portfolio value
        total_portfolio_value = sum(portfolio_stock_return[ticker] for ticker in tickers)
        portfolio_value.append(total_portfolio_value)

        # Store individual stock values for later analysis
        for ticker in tickers:
            portfolio_stock_value[ticker].append(portfolio_stock_return[ticker])

    # Store portfolio value and individual stock values in the combined data
    for ticker in tickers:
        combined_data[f"{ticker} Portfolio Value"] = portfolio_stock_value[ticker]

    # Add profile portfolio value (sum of all stock portfolio values)
    combined_data["Profile Portfolio Value"] = portfolio_value
    # Add cumulative contributions
    combined_data["Contributions"] = (combined_data.index.weekday == 0).cumsum() * weekly_investment

    return combined_data

def max_drawdown_calc(combined_data):
    
    profile_high = []
    counter_max = []
    profile_max = combined_data['Profile Portfolio Value'].iloc[0]
    drawdown_counter = 0

    for i in range(len(combined_data)):


        if combined_data['Profile Portfolio Value'].iloc[i] >= profile_max:
            profile_max = combined_data['Profile Portfolio Value'].iloc[i]
            drawdown_counter = 1
        else:
            drawdown_counter  += 1

        profile_high.append(profile_max)
        counter_max.append(drawdown_counter)

    combined_data["Profile High"] = profile_high
    combined_data["Down Days"] = counter_max


    return combined_data



# Get user input for tickers (up to 10)
tickers_input = input("Enter up to 10 stock tickers, separated by spaces: ")
tickers = tickers_input.upper().split()[:10]  # Convert to uppercase and limit to 10 tickers
# Ensure at least one ticker is entered
if not tickers:
    print("No tickers entered. Exiting...")
    exit()

allocation_input = input("Enter the allocation for each stock, separated by spaces: ")
allocation = allocation_input.split()[:10]  # Convert to uppercase and limit to 10 tickers
try:
    allocation = [float(x) for x in allocation]
    allocation = [value / 100 for value in allocation]

except ValueError:
    print("Invalid input! Please enter numbers only.")
    exit()

allocation_total = sum(allocation)
if allocation_total > 1:
    print("Allocation is greater than 100%")
    exit()
elif allocation_total < 1:
    print("Allocation is less than 100%")
    exit()

# Specify the time range
start_date = "2020-01-01"
end_date = "2020-12-01"
weekly_investment = 100

# Calculate stock data
stock_data = calculate_stock_data(tickers=tickers, start_date=start_date, end_date=end_date)

# Ensure stock_data is not empty before proceeding
if stock_data.empty:
    print("No valid stock data retrieved. Exiting...")
    exit()

# Simulate portfolio returns
stock_data = simulate_holdings_return(stock_data, tickers, weekly_investment, allocation)

stock_data = max_drawdown_calc(stock_data)

# Save to CSV
stock_data.to_csv("Portfolio.csv")
print("Portfolio data saved to Portfolio.csv")
