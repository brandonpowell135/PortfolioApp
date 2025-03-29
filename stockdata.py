import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt


def calculate_stock_data(tickers, start_date, end_date):
    combined_data = pd.DataFrame()  

    for ticker in tickers:

        stock_data = yf.download(ticker, start=start_date, end=end_date)
        if stock_data.empty:
            print(f"Warning: No data found for {ticker}. Skipping...")
            continue  

        stock_data["Daily Return"] = stock_data["Close"].pct_change()
        combined_data[f"{ticker} Daily Return"] = stock_data["Daily Return"]

        initial_value = 100
        combined_data[f"{ticker} Cumulative"] = (1 + combined_data[f"{ticker} Daily Return"]).cumprod() * initial_value

    return combined_data

def simulate_holdings_return(combined_data, tickers, weekly_investment, allocation, rebalance=30):
    portfolio_stock_value = {ticker: [] for ticker in tickers}
    portfolio_value = []
    portfolio_stock_return = {ticker: 0 for ticker in tickers} 

    ticker_allocation = {tickers[i]: allocation[i] for i in range(len(tickers))}

    for i in range(len(combined_data)):

        if combined_data.index[i].weekday() == 0:  # Monday
            for ticker in tickers:
                portfolio_stock_return[ticker] += weekly_investment * ticker_allocation[ticker]

        for ticker in tickers:
            if i > 0:
                portfolio_stock_return[ticker] *= (1 + combined_data[f"{ticker} Daily Return"].iloc[i])

        if i % rebalance == 0 and i > 0:  # Avoid rebalancing on the first day
            total_portfolio_value = sum(portfolio_stock_return[ticker] for ticker in tickers)
            for ticker in tickers:
                target_value = total_portfolio_value * ticker_allocation[ticker]
                portfolio_stock_return[ticker] = target_value

        total_portfolio_value = sum(portfolio_stock_return[ticker] for ticker in tickers)
        portfolio_value.append(total_portfolio_value)

        for ticker in tickers:
            portfolio_stock_value[ticker].append(portfolio_stock_return[ticker])

    for ticker in tickers:
        combined_data[f"{ticker} Portfolio Value"] = portfolio_stock_value[ticker]

    combined_data["Profile Portfolio Value"] = portfolio_value
    combined_data["Contributions"] = (combined_data.index.weekday == 0).cumsum() * weekly_investment

    return combined_data

def max_drawdown_calc(combined_data):

    profile_return = combined_data['Profile Portfolio Value'] - combined_data['Contributions']
    combined_data["Profile Portfolio Return"] = profile_return

    down_days = []
    return_max = 0
    drawdown_counter = 0

    for i in range(len(combined_data)):
        if  combined_data["Profile Portfolio Return"].iloc[i] >= return_max:
            return_max = combined_data["Profile Portfolio Return"].iloc[i]
            drawdown_counter = 0
        else:
            drawdown_counter  += 1

        down_days.append(drawdown_counter)

    combined_data["Down Days"] = down_days
    return combined_data


def profile_input():

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

    return tickers, allocation



# Specify the time range
start_date = "2020-01-01"
end_date = "2020-12-31"
weekly_investment = 100

profile_ammounts = input("How many Profiles would you like to create? [5 Max]: ")
try:
    val = int(profile_ammounts)
except ValueError:
    print("Invalid input! Please enter numbers only.")
    exit()

profile_values = []

for i in range(val):

    #Profile results (ticker, allocation)
    profile_results = profile_input()
    # Calculate stock data
    stock_data = calculate_stock_data(tickers=profile_results[0], start_date=start_date, end_date=end_date)

    if stock_data.empty:
        print("No valid stock data retrieved. Exiting...")
        exit()

    # Simulate portfolio returns
    stock_data = simulate_holdings_return(combined_data=stock_data, tickers=profile_results[0], weekly_investment=weekly_investment, allocation=profile_results[1])
    # Calculate max drawdowns
    stock_data = max_drawdown_calc(combined_data=stock_data)

    # Save to CSV
    output_filename = f"Portfolio_{i+1}.csv"
    stock_data.to_csv(output_filename)
    print(f"Portfolio data for iteration {i+1} saved to {output_filename}")

    # Append the Profile Portfolio Value for this iteration
    profile_values.append(stock_data['Profile Portfolio Value'])
    
# Plotting Profile Portfolio Values for each iteration
plt.figure(figsize=(10, 6))

# Plot each profile portfolio value
for i in range(val):
    plt.plot(profile_values[i], label=f"Portfolio {i+1}")

# Customize the plot
plt.xlabel('Date')
plt.ylabel('Profile Portfolio Value')
plt.title('Profile Portfolio Values for Each Profile')
plt.legend()  # Show a legend for each profile
plt.grid(True)  # Show grid lines for better readability
plt.show()

# Save the plot as an image file (PNG format)
output_filename = "portfolio_values_plot.png"
plt.savefig(output_filename)