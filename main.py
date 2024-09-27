from flask import Flask, render_template, request, jsonify
import requests
import pandas as pd
import json

# Load API key and base URL from the 'config.json' file
with open('config.json', 'r') as file:
    data = json.load(file)

API_KEY = data['api_key']
BASE_URL = data['base_url']

app = Flask(__name__)

# Function to fetch monthly stock data from Alpha Vantage API
def fetch_stock_data(symbol):
    params = {
        'function': 'TIME_SERIES_MONTHLY',
        'symbol': symbol,
        'apikey': API_KEY
    }

    response = requests.get(BASE_URL, params=params)
    data = response.json()

    # Extracting time series data
    if 'Monthly Time Series' in data:
        time_series = data['Monthly Time Series']
        df = pd.DataFrame.from_dict(time_series, orient='index')
        df = df.astype(float)
        df.index = pd.to_datetime(df.index)
        # Keep only the data for the past year (12 months)
        df = df.head(24)
        return df
    else:
        print("Error fetching data:", data)
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stock-data', methods=['POST'])
def get_stock_data():
    symbol = request.form['symbol'].upper()

    df = fetch_stock_data(symbol)

    if df is not None:
        # Convert DataFrame to JSON format that can be used by the frontend
        return jsonify({
            'dates': df.index.strftime('%Y-%m-%d').tolist(),
            'closing_prices': df['4. close'].tolist()
        })
    else:
        return jsonify({'error': 'Data not available'}), 400

if __name__ == '__main__':
    app.run(debug=False)
