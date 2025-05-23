import matplotlib.pylab as plt
import pandas as pd


def save_to_csv(combined_data, iteration):
    output_filename = f"Portfolio_{iteration+1}.csv"
    combined_data.to_csv(output_filename)
    print(f"Portfolio data for iteration {iteration+1} saved to {output_filename}")


def plot_results(combined_data, portfolio_stats,val):
    plt.figure(figsize=(11, 7)) #Width, Height
    column_labels = [f"Portfolio #", "Max Drawdown", "Longest Drawdown Duration", "Total Return", "Total Contributions", "End Value"]
    # Add the table below the plot       

    # Plot each profile portfolio value
    for i in range(val):
        plt.plot(combined_data[i]["Profile Portfolio Value"], label=f"Portfolio {i+1}")
        
        plt.plot(combined_data[i]["Contributions"], label="Contributions", color="purple")
        
    table_data = pd.DataFrame(portfolio_stats, columns=column_labels)
                                                                                                      #bbox = [left, bottom, width, height]
    plt.table(cellText=table_data.values, colLabels=table_data.columns, cellLoc='center', loc='bottom', bbox=[0, -0.3, 1, 0.2])

    # Customize the plot
    plt.xlabel('Date')
    plt.ylabel('Profile Portfolio Value')
    plt.title('Profile Portfolio Values for Each Profile')
    plt.legend()  # Show a legend for each profile
    plt.grid(True)  # Show grid lines for better readability
    plt.tight_layout()# Adjust layout to reserve 20% space at the bottom for the table
    plt.show()

    # Save the plot as an image file (PNG format)
    plt.savefig("portfolio_values_plot.png")
