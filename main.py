import requests
import pandas as pd
import matplotlib.pyplot as plt
import time
import json

# Load API key and base URL from the 'data.json' file
with open('config.json', 'r') as file:
    data = json.load(file)

API_KEY = data['api_key']
BASE_URL = data['base_url']


# Function to fetch stock data from Alpha Vantage API
def fetch_stock_data(symbol, interval='1min'):
    params = {
        'function': 'TIME_SERIES_INTRADAY',
        'symbol': symbol,
        'interval': interval,
        'apikey': API_KEY
    }

    response = requests.get(BASE_URL, params=params)
    data = response.json()

    # Extracting time series data
    if f'Time Series ({interval})' in data:
        time_series = data[f'Time Series ({interval})']
        df = pd.DataFrame.from_dict(time_series, orient='index')
        df = df.astype(float)
        df.index = pd.to_datetime(df.index)
        return df
    else:
        print("Error fetching data:", data)
        return None


# Function to plot stock data using Matplotlib
def plot_stock_data(df, symbol):
    plt.figure(figsize=(10, 6))
    plt.plot(df.index, df['4. close'], label='Closing Price', color='blue')
    plt.title(f'{symbol} Stock Price')
    plt.xlabel('Date')
    plt.ylabel('Price (USD)')
    plt.grid(True)
    plt.legend()
    plt.show()


# Optimize API calls by introducing delay (as per Alpha Vantage limits)
def optimized_data_retrieval(symbol, interval='1min'):
    start_time = time.time()

    # Fetch data
    df = fetch_stock_data(symbol, interval)

    # Calculate time taken to complete the API call
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f'API call completed in {elapsed_time:.2f} seconds')

    # Optimization: If API call was too fast, wait for some time
    if elapsed_time < 12:  # Alpha Vantage limits 5 API requests per minute
        wait_time = 12 - elapsed_time
        print(f'Waiting for {wait_time:.2f} seconds to avoid API limit...')
        time.sleep(wait_time)

    return df


# Main function
def main():
    symbol = input("Enter the stock symbol (e.g., AAPL for Apple): ").upper()
    interval = '5min'  # You can choose '1min', '5min', etc.

    # Retrieve and optimize data retrieval
    df = optimized_data_retrieval(symbol, interval)

    if df is not None:
        # Plot stock data
        plot_stock_data(df, symbol)
    else:
        print("No data to plot.")


if __name__ == '__main__':
    main()
