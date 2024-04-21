import pandas as pd
import yfinance as yf
from flask import Flask, render_template, request, jsonify, send_from_directory
from yahooquery import search
import json

app = Flask(__name__)
df = pd.DataFrame()
selected_stock = ''
stock_symbol = ''
result_df_same_month = None
result_df_yearly = None
result_info = None
year_income = None

def year_income_statement(stock_symbol):
    try:
        stock = yf.Ticker(stock_symbol)
        # Get stock info
        try:
            income_statement = stock.income_stmt
            print('income_statement')
            print(income_statement)
            print()
        except Exception as e:
            print(f"Error fetching income statement for {stock_symbol}: {e}")

        try:
            quarterly_statement=stock.quarterly_income_stmt
            print(quarterly_statement)
            print()
        except Exception as e:
            print(f"Error fetching quarterly statement for {stock_symbol}: {e}")

        try:
            balance_sheet=stock.balance_sheet
            print("balance_sheet")
            print(balance_sheet)
            print()
        except Exception as e:
            print(f"Error fetching balance sheet for {stock_symbol}: {e}")

        try:
            quarterly_balance=stock.quarterly_balance_sheet
            print(quarterly_balance)
            print()
        except Exception as e:
            print(f"Error fetching quarterly balance for {stock_symbol}: {e}")

        try:
            cashflow=stock.cashflow
            print("cashflow")
            print(cashflow)
            print()
        except Exception as e:
            print(f"Error fetching cashflow for {stock_symbol}: {e}")

        try:
            major_holders=stock.major_holders
            print("major_holders")
            print(major_holders)
            print()
        except Exception as e:
            print(f"Error fetching major holders for {stock_symbol}: {e}")

        try:
            mutualfund_holders=stock.mutualfund_holders
            print("mutualfund_holders")
            print(mutualfund_holders)
            print()
        except Exception as e:
            print(f"Error fetching mutual fund holders for {stock_symbol}: {e}")

        try:
            insider_transactions=stock.insider_transactions
            print("insider_transactions")
            print(insider_transactions)
            print()
        except Exception as e:
            print(f"Error fetching insider transactions for {stock_symbol}: {e}")

        try:
            insider_roster_holders=stock.insider_roster_holders
            print("insider_roster_holders")
            print(insider_roster_holders)
            print()
        except Exception as e:
            print(f"Error fetching insider roster holders for {stock_symbol}: {e}")

    except Exception as e:
        print(f"Error fetching data for {stock_symbol}: {e}")
        return None
        
def fetch_info(stock_symbol):
    try:
        # Create a Ticker object for the stock
        stock_ticker = yf.Ticker(stock_symbol)
        # Get company information
        company_info = stock_ticker.info
        general_info = {
            "Company Name": company_info.get("longName", ""),
            "Industry": company_info.get("industry", ""),
            "Sector": company_info.get("sector", ""),
            "Website": company_info.get("website", ""),
            "Full-Time Employees": company_info.get("fullTimeEmployees", ""),
            "currentPrice": company_info.get("currentPrice", ""),
            "marketCap": company_info.get("marketCap", ""),
            "averageVolume": company_info.get("averageVolume", ""),
            "totalDebt": company_info.get("totalDebt", ""),
            "totalRevenue": company_info.get("totalRevenue", ""),
            "totalCash": company_info.get("totalCash", ""),
            "freeCashflow": company_info.get("freeCashflow", ""),
            "longBusinessSummary": company_info.get("longBusinessSummary", ""),
            "share in Market": company_info.get("floatShares",""),
            "Total Share in Company": company_info.get("sharesOutstanding",""),
            "enterpriseValue": company_info.get("enterpriseValue",""),
        }
        # Fetch company officers data
        company_officers = []
        for officer in company_info.get("companyOfficers", []):
            officer_info = {
                "Name": officer.get("name", ""),
                "Age": officer.get("age", ""),
                "Position": officer.get("title", "")
            }
            company_officers.append(officer_info)

        # Add company officers data to general_info
        general_info["companyOfficers"] = company_officers
        return general_info

    except Exception as e:
        print(f"Error fetching stock information for {stock_symbol}: {e}")
        return None


# Function to fetch historical data using yfinance
def fetch_historical_data(stock_symbol):
    try:
        ticker = yf.Ticker(stock_symbol)
        data = ticker.history(period='max')
        return data
    except Exception as e:
        print(f"Error fetching historical data for {stock_symbol}: {e}")
        return None


# Function to preprocess the data
def preprocess_data(data):
    data = data.drop(columns=["Adj Close"])
    data = data.round(2)
    return data


# Function to handle fetching and preprocessing data for selected stock
def handle_selected_stock(selected_stock):
    global df
    global stock_symbol
    global result_info
    global year_income
    # Fetch stock symbol based on the selected stock
    try:
        result = search(selected_stock)
        if result['quotes']:
            stock_symbol = result['quotes'][0]['symbol']
            print(f"Stock symbol for {selected_stock}: {stock_symbol}")
            year_income = year_income_statement(stock_symbol)
            # Fetch company information
            result_info = fetch_info(stock_symbol)
            # Fetch historical data
            df = fetch_historical_data(stock_symbol)
            if df is not None:
                # Preprocess the data
                df = preprocess_data(df)
            else:
                print("Failed to fetch or preprocess data.")
            return result_info
        else:
            print(f"No stock symbol found for {selected_stock}")
    except Exception as e:
        print(f"Error fetching stock symbol for {selected_stock}: {e}")


# Route to serve the HTML page
@app.route('/')
def index():
    print("Rendering index.html")
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/sign_up')
def sign_up():
    return render_template('sign_up.html')

@app.route('/login')
def login():
    return render_template('Login.html')

@app.route('/stock_names.json')
def get_stock_names():
    # Logic to read and return stock_names.json
    return send_from_directory(app.root_path, 'stock_names.json')


# Route to handle the selected stock and fetch historical data
@app.route('/submit_selected_stock', methods=['POST'])
def submit_selected_stock():
    global selected_stock
    data = request.get_json()
    selected_stock = data.get('selectedStock', '')
    # Handle selected stock
    handle_selected_stock(selected_stock)
    return jsonify({'message': 'Selected stock received successfully'})


# Visualization route to generate and display plots
@app.route('/visualize_data')
def visualize_data():
    global df
    global result_info

    # First visualization
    if df is None or df.empty:
        error_message = "aaj mood nhi hai thoda scroll kr leta hu"
        print(error_message)
        return jsonify({'error': error_message}), 400

    df.index = pd.to_datetime(df.index)
    labels = df.index.strftime('%Y-%m-%d').tolist()

    try:
        # Attempt to access the 'Close' column
        data = df['Close'].tolist()
    except KeyError:
        # Handle the error if the 'Close' column is not found
        error_message = "Error: 'Close' column not found in DataFrame."
        print(error_message)
        return jsonify({'error': error_message}), 400


    # Second visualization
    result_data = []
    for year in df.index.year.unique():
        for month in range(1, 13):
            target_data = df[(df.index.year == year) & (df.index.month == month)]
            if not target_data.empty:
                first_day_high = target_data.iloc[0]['Open']
                last_day_low = target_data.iloc[-1]['Close']
                month_range = last_day_low - first_day_high
                direction = 'Positive' if month_range > 0 else 'Negative'
                percent_change = round((last_day_low - first_day_high) / first_day_high * 100, 1)
                result_data.append({
                    'Year': year,
                    'Month': month,
                    'High': first_day_high,
                    'Low': last_day_low,
                    'Month_range': month_range,
                    'Direction': direction,
                    'Returns': percent_change
                })
    result_df = pd.DataFrame(result_data,
                             columns=['Year', 'Month', 'High', 'Low', 'Month_range', 'Direction', 'Returns'])
    result_df = result_df.round(2)

    # Third visualization
    result_data_yearly = []
    for year in df.index.year.unique():
        year_data = df[df.index.year == year]
        if not year_data.empty:
            first_day_high = year_data.iloc[0]['Open']
            last_day_low = year_data.iloc[-1]['Close']
            year_range = last_day_low - first_day_high
            direction = 'Positive' if year_range > 0 else 'Negative'
            percent_change = round((last_day_low - first_day_high) / first_day_high * 100, 1)
            result_data_yearly.append({
                'Year': year,
                'High': first_day_high,
                'Low': last_day_low,
                'Year_range': year_range,
                'Direction': direction,
                'Returns': percent_change
            })
    result_df_yearly = pd.DataFrame(result_data_yearly,
                                    columns=['Year', 'High', 'Low', 'Year_range', 'Direction', 'Returns'])
    result_df_yearly = result_df_yearly.round(2)

    return render_template('result.html', labels=json.dumps(labels), data=json.dumps(data),
                           data_monthly=result_df.to_dict('records'), data_yearly=result_df_yearly.to_dict('records')
                            , result_info=result_info)

if __name__ == '__main__':
    app.run(debug=True)