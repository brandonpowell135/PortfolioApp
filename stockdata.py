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
def simulate_profile_return(combined_data, tickers, weekly_investment, stock_allocation):
    for ticker in tickers:
        if f"{ticker} Daily Return" not in combined_data:
            continue  # Skip tickers with missing data

        portfolio_stock_return = 0
        portfolio_stock_value = []

        # Loop through each day in the dataset
        for i in range(len(combined_data)):
            # Weekly investments are added every Monday
            if combined_data.index[i].weekday() == 0:  # Monday
                portfolio_stock_return += weekly_investment * stock_allocation

            # Apply daily returns
            if i > 0:  
                portfolio_stock_return *= (1 + combined_data[f"{ticker} Daily Return"].iloc[i])

            # Store portfolio value
            portfolio_stock_value.append(portfolio_stock_return)

        combined_data[f"{ticker} Portfolio Value"] = portfolio_stock_value

    # Add cumulative contributions
    combined_data["Contributions"] = (combined_data.index.weekday == 0).cumsum() * weekly_investment

    return combined_data

# Get user input for tickers (up to 10)
tickers_input = input("Enter up to 10 stock tickers, separated by spaces: ")
tickers = tickers_input.upper().split()[:10]  # Convert to uppercase and limit to 10 tickers

# Ensure at least one ticker is entered
if not tickers:
    print("No tickers entered. Exiting...")
    exit()

# Specify the time range
start_date = "2020-01-01"
end_date = "2020-12-01"
weekly_investment = 100
stock_allocation = 0.7

# Calculate stock data
stock_data = calculate_stock_data(tickers=tickers, start_date=start_date, end_date=end_date)

# Ensure stock_data is not empty before proceeding
if stock_data.empty:
    print("No valid stock data retrieved. Exiting...")
    exit()

# Simulate portfolio returns
upro_data = simulate_profile_return(stock_data, tickers, weekly_investment, stock_allocation)

# Save to CSV
stock_data.to_csv("Portfolio.csv")
print("Portfolio data saved to Portfolio.csv")
