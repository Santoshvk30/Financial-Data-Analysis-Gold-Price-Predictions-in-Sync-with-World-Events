import requests
import plotly
import plotly.express as px
import pandas as pd
import json
from flask import Flask, render_template, request, redirect, flash
import psycopg2

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Required for flash messages

# Database connection parameters
DB_NAME = "gold_prices"
DB_USER = "postgres"  # Replace with your PostgreSQL username
DB_PASSWORD = "Chinnu@220412"  # Replace with your PostgreSQL password
DB_HOST = "localhost"  # Or your DB host
DB_PORT = "5432"  # Default PostgreSQL port

# Function to fetch the latest gold price from GoldAPI
def make_gapi_request():
    api_key = "goldapi-dcndtsm3bncbc1-io"  # Use your actual API key
    symbol = "XAU"
    curr = "INR"  # Change currency to INR
    date = ""  # Empty to get today's price

    url = f"https://www.goldapi.io/api/{symbol}/{curr}{date}"

    headers = {
        "x-access-token": api_key,
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # This will raise an error for 4xx/5xx responses

        result = response.json()  # Use .json() to parse the response as JSON
        return result.get('price', None)  # Extract the 'price' key, or None if not found
    except requests.exceptions.RequestException as e:
        print("Error:", str(e))
        return None

# Data reliability check function
def validate_data(df):
    if df.isnull().values.any():
        print("Warning: Data contains missing values.")
    if (df['INR_Price'] < 0).any():
        print("Warning: Data contains negative prices.")
    # Add more checks as needed for data consistency

# Fetch today's gold price from GoldAPI
def get_today_price():
    return make_gapi_request()  # Call the GoldAPI request to fetch today's price

# Establish a connection to the database
try:
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
    )
    print("Database connection established.")
except Exception as e:
    print("Failed to connect to the database.")
    print(e)
    exit()

# Create a cursor object to execute SQL queries
cur = conn.cursor()

# Retrieve data from the database
cur.execute("SELECT date, inr_price FROM gold_prices_inr ORDER BY date ASC;")
data = cur.fetchall()

# Convert the data to a DataFrame
df = pd.DataFrame(data, columns=["Date", "INR_Price"])

# Ensure the 'Date' column is in datetime format
df['Date'] = pd.to_datetime(df['Date'])

# Validate data for reliability
validate_data(df)

# Close the database connection
cur.close()
conn.close()

# Weekly price (taking the last price of the week)
df['Week'] = df['Date'].dt.to_period('W').dt.start_time
df_weekly = df.groupby('Week')['INR_Price'].last().reset_index()

# Monthly price (taking the last price of the month)
df['Month'] = df['Date'].dt.to_period('M').dt.start_time
df_monthly = df.groupby('Month')['INR_Price'].last().reset_index()

# Quarterly price (taking the last price of the quarter)
df['Quarter'] = df['Date'].dt.to_period('Q').dt.start_time
df_quarterly = df.groupby('Quarter')['INR_Price'].last().reset_index()

# Yearly price (taking the last price of the year)
df['Year'] = df['Date'].dt.to_period('Y').dt.start_time
df_yearly = df.groupby('Year')['INR_Price'].last().reset_index()

# Route to display graphs and today's price
@app.route('/')
def index():
    # Fetch today's price using GoldAPI
    today_price = get_today_price()

    # Insert today's price into the database
    if today_price:
        today_price_in_grams = today_price / 31.1035  # Convert to price per gram
        try:
            # Check if the data for today's date already exists
            conn = psycopg2.connect(
                dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
            )
            cur = conn.cursor()
            cur.execute("SELECT date FROM gold_prices_inr WHERE date = CURRENT_DATE;")
            result = cur.fetchone()

            # If today's data exists, update it, else insert new data
            if result:
                cur.execute("UPDATE gold_prices_inr SET inr_price = %s WHERE date = CURRENT_DATE;", (today_price_in_grams,))
            else:
                cur.execute("INSERT INTO gold_prices_inr (date, inr_price) VALUES (CURRENT_DATE, %s);", (today_price_in_grams,))
            
            conn.commit()
            print(f"Today's price of ₹{today_price_in_grams} inserted/updated successfully into the database.")
        except Exception as e:
            print(f"Error inserting data into the database: {e}")
        finally:
            cur.close()
            conn.close()

    # Create Plotly graphs for each price variation
    graph_weekly = px.line(df_weekly, x='Week', y='INR_Price', title='Weekly Gold Prices (INR per gram)')
    graph_weekly.update_layout(
        width=1000, height=600,
        yaxis_title="Price (INR per gram)",
        xaxis_title="Week",
        title="Weekly Gold Prices (INR per gram)"
    )

    graph_monthly = px.line(df_monthly, x='Month', y='INR_Price', title='Monthly Gold Prices (INR per gram)')
    graph_monthly.update_layout(
        width=1000, height=600,
        yaxis_title="Price (INR per gram)",
        xaxis_title="Month",
        title="Monthly Gold Prices (INR per gram)"
    )

    graph_quarterly = px.line(df_quarterly, x='Quarter', y='INR_Price', title='Quarterly Gold Prices (INR per gram)')
    graph_quarterly.update_layout(
        width=1000, height=600,
        yaxis_title="Price (INR per gram)",
        xaxis_title="Quarter",
        title="Quarterly Gold Prices (INR per gram)"
    )

    graph_yearly = px.line(df_yearly, x='Year', y='INR_Price', title='Yearly Gold Prices (INR per gram)')
    graph_yearly.update_layout(
        width=1000, height=600,
        yaxis_title="Price (INR per gram)",
        xaxis_title="Year",
        title="Yearly Gold Prices (INR per gram)"
    )

    # Convert the graphs to JSON format for use in the template
    graph_weekly_json = json.dumps(graph_weekly, cls=plotly.utils.PlotlyJSONEncoder)
    graph_monthly_json = json.dumps(graph_monthly, cls=plotly.utils.PlotlyJSONEncoder)
    graph_quarterly_json = json.dumps(graph_quarterly, cls=plotly.utils.PlotlyJSONEncoder)
    graph_yearly_json = json.dumps(graph_yearly, cls=plotly.utils.PlotlyJSONEncoder)

    # Pass today's price to the template
    return render_template('index.html', 
                           graph_weekly_json=graph_weekly_json,
                           graph_monthly_json=graph_monthly_json,
                           graph_quarterly_json=graph_quarterly_json,
                           graph_yearly_json=graph_yearly_json,
                           today_price=today_price)

# Route for survey form
@app.route('/survey', methods=['GET', 'POST'])
def survey():
    if request.method == 'POST':
        # Handle survey submission logic
        response = request.form['response']
        # Save response to the database or log as needed
        flash("Thank you for your feedback!")
        return redirect('/')
    return render_template('survey.html')  # Render a form for survey input

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
