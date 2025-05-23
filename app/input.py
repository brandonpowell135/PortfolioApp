#user input
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


