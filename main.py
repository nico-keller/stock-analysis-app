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
        df = df.head(12)
        return df
    else:
        print("Error fetching data:", data)
        return None

# Function to fetch company overview data
def fetch_company_overview(symbol):
    params = {
        'function': 'OVERVIEW',
        'symbol': symbol,
        'apikey': API_KEY
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()

    return data

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/stock-data', methods=['POST'])
def get_stock_data():
    symbol = request.form['symbol'].upper()

    # Fetch stock data
    df = fetch_stock_data(symbol)

    if df is not None:
        # Convert DataFrame to JSON format and return
        return jsonify({
            'dates': df.index.strftime('%Y-%m-%d').tolist(),
            'closing_prices': df['4. close'].tolist(),
            'open_prices': df['1. open'].tolist(),
            'high_prices': df['2. high'].tolist(),
            'low_prices': df['3. low'].tolist(),
            'volumes': df['5. volume'].tolist()
        })
    else:
        return jsonify({'error': 'Data not available'}), 400

@app.route('/company-overview', methods=['POST'])
def get_company_overview():
    symbol = request.form['symbol'].upper()
    data = fetch_company_overview(symbol)

    if data:
        return jsonify({
            'company_name': data.get('Name', 'N/A'),
            'asset_type': data.get('AssetType', 'N/A'),
            'exchange': data.get('Exchange', 'N/A'),
            'country': data.get('Country', 'N/A'),
            'sector': data.get('Sector', 'N/A'),
            'industry': data.get('Industry', 'N/A'),
            'revenue_per_share': data.get('RevenuePerShareTTM', 'N/A'),
            'dividend_per_share': data.get('DividendPerShare', 'N/A')
        })
    else:
        return jsonify({'error': 'Company Overview not available'}), 400

if __name__ == '__main__':
    app.run(debug=False)
