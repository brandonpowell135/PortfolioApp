import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

real_start_date = pd.Timestamp('1900-01-01')  


def calculate_stock_data(tickers, start_date, end_date):
    combined_data = pd.DataFrame()
    global real_start_date 

    if "UPROM" in tickers:
        stock_data = yf.download("^GSPC", start=start_date, end=end_date)
        stock_data["Daily Return"] = stock_data["Close"].pct_change()
        real_start_date = max(real_start_date, stock_data.index[0])
        combined_data["UPROM Daily Return"] = (stock_data["Daily Return"] * 3) + 0.00010
        combined_data["UPROM Cumulative"] = (1 + combined_data["UPROM Daily Return"]).cumprod() * 100
        combined_data = combined_data[combined_data.index >= real_start_date]

    else:
        for ticker in tickers:

            stock_data = yf.download(ticker, start=start_date, end=end_date)
            if stock_data.empty:
                print(f"Warning: No data found for {ticker}. Skipping...")
                continue  

            stock_data["Daily Return"] = stock_data["Close"].pct_change()
            combined_data[f"{ticker} Daily Return"] = stock_data["Daily Return"]
            combined_data[f"{ticker} Cumulative"] = (1 + combined_data[f"{ticker} Daily Return"]).cumprod() * 100
            real_start_date = max(real_start_date, stock_data.index[0])
            combined_data = combined_data[combined_data.index >= real_start_date]

    return combined_data




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
    if len(tickers) != len(allocation):
        print("Mismatch: Number of allocations does not match number of tickers.")
        exit()

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















def save_to_csv(combined_data, iteration):
    output_filename = f"Portfolio_{iteration+1}.csv"
    combined_data.to_csv(output_filename)
    print(f"Portfolio data for iteration {iteration+1} saved to {output_filename}")

def plot_results(profile_values, portfolio_stats, val):
    plt.figure(figsize=(11, 7)) #Width, Height

    # Plot each profile portfolio value
    for i in range(val):
        plt.plot(profile_values[i], label=f"Portfolio {i+1}")

    table_data = pd.DataFrame(portfolio_stats)

    column_labels = [f"Portfolio #", "Max Drawdown", "Longest Drawdown Duration", "Total Return", "Total Contributions", "End Value"]
    # Add the table below the plot                                                                         bbox = [left, bottom, width, height]
    table = plt.table(cellText=table_data.values, colLabels=column_labels, cellLoc='center', loc='bottom', bbox=[0, -0.3, 1, 0.2])

    plt.plot(combined_data.index, 
    combined_data["Contributions"], 
    label="Contributions", 
    color="purple")

    # Customize the plot
    plt.xlabel('Date')
    plt.ylabel('Profile Portfolio Value')
    plt.title('Profile Portfolio Values for Each Profile')
    plt.legend()  # Show a legend for each profile
    plt.grid(True)  # Show grid lines for better readability
    plt.tight_layout()# Adjust layout to reserve 20% space at the bottom for the table
    plt.show()

    # Save the plot as an image file (PNG format)
    output_filename = "portfolio_values_plot.png"
    plt.savefig(output_filename)


# Specify the time range
start_date = "2000-01-01"
end_date = "2020-03-31"
weekly_investment = 100
initial_investment = 0
rebalance = 30
profile_ammounts = input("How many Profiles would you like to create? [ 5 Max ]: ")


try:
    val = int(profile_ammounts)  # Convert input to integer
    if val < 1 or val > 5:  # Check if it's within the valid range
        print("Please enter a number between 1 and 5.")
        exit()
except ValueError:
    print("Invalid input! Please enter a valid number.")
    exit()

profile_values = []
portfolio_stats = []

for i in range(val):

    #Profile results (ticker, allocation)
    profile_results = profile_input()
    # Calculate stock data
    combined_data = calculate_stock_data(tickers=profile_results[0], start_date=start_date, end_date=end_date)
    if combined_data.empty:
        print("No valid stock data retrieved. Exiting...")
        exit()

    # Functions
    combined_data = simulate_holdings_return(combined_data=combined_data, 
                                             tickers=profile_results[0], 
                                             initial_investment = initial_investment, 
                                             weekly_investment=weekly_investment, 
                                             allocation=profile_results[1], 
                                             rebalance=rebalance)
                                             
    combined_data = max_drawdown_calc(combined_data=combined_data)
    save_to_csv(combined_data, i)

    # Data for plot
    profile_values.append(combined_data['Profile Portfolio Value'])

    # Data for table
    max_drawdown = combined_data["Max Drawdown"].max() * 100
    max_drawdown_duration = combined_data["Down Days"].max()
    total_return = (combined_data["Profile Portfolio Return"].iloc[-1] / combined_data["Contributions"].iloc[-1]) *100
    end_value = combined_data["Profile Portfolio Value"].iloc[-1]
    total_contributions = combined_data["Contributions"].iloc[-1]

    portfolio_stats.append([
        f"Portfolio {i+1}", 
        f"{max_drawdown:,.2f}%", 
        f"{max_drawdown_duration} days", 
        f"{total_return:,.2f}%",
        f"${total_contributions:,}", 
        f"${round(end_value):,}"])


plot_results(profile_values, portfolio_stats, val)

