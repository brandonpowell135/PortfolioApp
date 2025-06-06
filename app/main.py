import pandas as pd

from calculations import retrieve_stock_data, simulate_holdings_return, max_drawdown_calc
from input import profile_input
from output import save_to_csv, plot_results


# Specify the time range
start_date = "2000-01-01"
end_date = "2020-03-31"
daily_investment = 25
initial_investment = 100
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
combined_data = []
profile_results = []
real_start_date = pd.Timestamp(start_date)


for i in range(val):
    #Profile results (ticker, allocation)
    profile_results.append(profile_input())
    # Calculate stock data
    stock_calc_data,  current_start_date = retrieve_stock_data(tickers=profile_results[i][0], start_date=start_date, end_date=end_date)
    if current_start_date > real_start_date:
        real_start_date = current_start_date

    if stock_calc_data.empty:
        print("No valid stock data retrieved. Exiting...")
        exit()

    combined_data.append(stock_calc_data)

for i in range(val):
    combined_data[i] = (combined_data[i][combined_data[i].index >= real_start_date])
    combined_data[i].to_csv(f"TEST_Portfolio_{i}.csv")

        # Functions
    combined_data[i] = simulate_holdings_return(combined_data=combined_data[i], 
                                            profile_results=profile_results[i], 
                                            initial_investment=initial_investment, 
                                            daily_investment=daily_investment)
                                            
    combined_data[i], total_contributions, max_drawdown, max_drawdown_duration = max_drawdown_calc(combined_data=combined_data[i], 
                                                                                                   initial_investment=initial_investment)

    save_to_csv(combined_data[i], i)

    # Data for plot
    profile_values.append(combined_data[i])

    # Data for table
    total_return = (combined_data[i]["Profile Portfolio Return"].iloc[-1] / combined_data[i]["Contributions"].sum()) *100
    end_value = (combined_data[i]["Profile Portfolio Value"].iloc[-1])

    portfolio_stats.append([
        f"Portfolio {i+1}", 
        f"{max_drawdown:,.2f}%", 
        f"{max_drawdown_duration} days", 
        f"{total_return:,.2f}%",
        f"${total_contributions:,}", 
        f"${round(end_value):,}"])


plot_results(combined_data, portfolio_stats, val)
