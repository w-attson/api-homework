#financial-planner

import os
import requests
import pandas as pd
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
from MCForecastTools import MCSimulation

# Load .env enviroment variables
load_dotenv()

# Collect Crypto Prices Using the `requests` Library

# Set current amount of crypto assets
my_btc = 1.2
my_eth = 5.3

# Crypto API URLs
btc_url = "https://api.alternative.me/v2/ticker/Bitcoin/?convert=CAD"
eth_url = "https://api.alternative.me/v2/ticker/Ethereum/?convert=CAD"

# Fetch current BTC price
btc_response = requests.get(btc_url).json()

# Fetch current ETH price
eth_response = requests.get(eth_url).json()

# Compute current value of my crypto
my_btc_value = btc_response['data']['1']['quotes']['USD']['price']
my_eth_value = eth_response['data']['1027']['quotes']['USD']['price']

# Print current crypto wallet balance
print(f"The current value of your {my_btc} BTC is ${my_btc_value:0.2f}")
print(f"The current value of your {my_eth} ETH is ${my_eth_value:0.2f}")

# Collect Investments Data Using Alpaca: `SPY` (stocks) and `AGG` (bonds)

# Set current amount of shares
my_agg = 200
my_spy = 50

# Set Alpaca API key and secret
alpaca_api_key = os.getenv("ALPACA_API_KEY")
alpaca_secret_key = os.getenv("ALPACA_SECRET_KEY")

# Create the Alpaca API object
api = tradeapi.REST(
    alpaca_api_key,
    alpaca_secret_key,
    api_version = "v2"
)

# Format current date as ISO format
current_start_date = pd.Timestamp("2018-08-04", tz="America/New_York").isoformat()
current_end_date = pd.Timestamp("2021-08-04", tz="America/New_York").isoformat()

# Set the tickers
tickers = ['AGG', 'SPY']

# Set timeframe to "1Day" for Alpaca API
timeframe = "1Day"

# Get current closing prices for SPY and AGG
closing_price_data = api.get_bars(
    tickers,
    timeframe,
    start=current_start_date,
    end=current_end_date
).df

# Reorganize the DataFrame
# Separate ticker data
AGG = closing_price_data[closing_price_data["symbol"]=="AGG"].drop("symbol", axis=1)
SPY = closing_price_data[closing_price_data["symbol"]=="SPY"].drop("symbol", axis=1)

#Concatenate dataframes
df_ticker = pd.concat([AGG, SPY], axis=1, keys=["AGG","SPY"])

# Pick AGG and SPY close prices
agg_close_price = float(df_ticker["AGG"]["close"][0])
spy_close_price = float(df_ticker["SPY"]["close"][0])

# Compute the current value of shares
my_agg_value = agg_close_price * my_agg
my_spy_value = spy_close_price * my_spy

# Print current value of shares
print(f"The current value of your {my_spy} SPY shares is ${my_spy_value:0.2f}")
print(f"The current value of your {my_agg} AGG shares is ${my_agg_value:0.2f}")


##Savings Health Analysis

# Set monthly household income
monthly_income = 12000

# Consolidate financial assets data
crypto_value = my_btc_value + my_eth_value
stock_value = my_agg_value + my_spy_value

# Create savings DataFrame
df_savings = pd.DataFrame([crypto_value, stock_value], index=["Crypto", "Shares"], columns=["Amount"])

#Plot savings pie chart
df_savings.plot.pie(y="Amount", title="Investment Portfolio")

# Set ideal emergency fund
emergency_fund = monthly_income * 3

# Calculate total amount of savings
total_savings = crypto_value + stock_value

# Validate saving health
if total_savings > emergency_fund:
    print("Congratulations! You have enough money in your emergency fund.")
elif total_savings == emergency_fund:
    print("Congratulations! You have reached your financial goal.")
elif total_savings < emergency_fund:
    print(f"You are ${emergency_fund - total_savings} away from reaching your financial goal.")
    

##Part 2 - Retirement Planning

# Set start and end dates of five years back from today.
# Sample results may vary from the solution based on the time frame chosen
start_date = pd.Timestamp('2017-07-28', tz='America/New_York').isoformat()
end_date = pd.Timestamp('2023-07-28', tz='America/New_York').isoformat()

# Get 5 years' worth of historical data for SPY and AGG
df_stock_data = api.get_bars(
    tickers,
    timeframe,
    start=start_date,
    end=end_date
).df

df_stock_data
# Reorganize the DataFrame
# Separate ticker data
AGG_historical = df_stock_data[df_stock_data["symbol"]=="AGG"].drop("symbol", axis=1)
SPY_historical = df_stock_data[df_stock_data["symbol"]=="SPY"].drop("symbol", axis=1)

# Concatenate the ticker DataFrames
df_stock_data = pd.concat([AGG_historical, SPY_historical], axis=1, keys=["AGG","SPY"])

# Display sample data
df_stock_data

# Configuring a Monte Carlo simulation to forecast 30 years cumulative returns
MC_even_dist = MCSimulation(
    portfolio_data = df_stock_data,
    weights = [0.4, 0.6],
    num_simulation = 500,
    num_trading_days = 252*30
)
    
# Printing the simulation input data
MC_even_dist.portfolio_data.head()

# Plot simulation outcomes
line_plot = MC_even_dist.plot_simulation()
line_plot

# Plot probability distribution and confidence intervals
dist_plot = MC_even_dist.plot_distribution()
dist_plot

# Fetch summary statistics from the Monte Carlo simulation results
MS_summary = MC_even_dist.summarize_cumulative_return()

# Print summary statistics
print(MS_summary)