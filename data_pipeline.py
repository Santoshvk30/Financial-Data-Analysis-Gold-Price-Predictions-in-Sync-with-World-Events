import requests
import psycopg2
from datetime import datetime
from elasticsearch import Elasticsearch

# Database connection parameters
DB_NAME = "gold_prices"
DB_USER = "postgres"  # Replace with your PostgreSQL username
DB_PASSWORD = "Chinnu@220412"  # Replace with your PostgreSQL password
DB_HOST = "localhost"
DB_PORT = "5432"
es = Elasticsearch([{'host': 'localhost', 'port': 9200}])  # Adjust if necessary

# Function to fetch the latest gold price from GoldAPI
def fetch_gold_price():
    api_key = "goldapi-dcndtsm3bncbc1-io"  # Replace with your actual API key
    symbol = "XAU"
    curr = "INR"
    url = f"https://www.goldapi.io/api/{symbol}/{curr}"

    headers = {
        "x-access-token": api_key,
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        result = response.json()
        return result.get('price', None)
    except requests.exceptions.RequestException as e:
        log_audit('ERROR', f"Failed to fetch gold price: {e}")
        return None

# Function to log audit information
def log_audit(action, details):
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
        )
        cur = conn.cursor()
        cur.execute("INSERT INTO audit_log (action, details) VALUES (%s, %s);", (action, details))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Failed to log audit entry: {e}")

# Function to index the gold price data in Elasticsearch
def index_gold_price(price, date):
    document = {
        'price': price,
        'date': date,
    }
    # Indexing the data into Elasticsearch
    es.index(index='gold_prices', body=document)

# Function to search for the gold price
def search_gold_price(query):
    response = es.search(
        index="gold_prices",
        body={
            "query": {
                "match": {
                    "price": query
                }
            }
        }
    )
    return response['hits']['hits']
# Insert fetched gold price into the database
# Modify insert_gold_price to also index into Elasticsearch
def insert_gold_price(price):
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
        )
        cur = conn.cursor()
        today_date = datetime.now().date()

        cur.execute("SELECT date FROM gold_prices_inr WHERE date = %s;", (today_date,))
        result = cur.fetchone()

        if result:
            cur.execute("UPDATE gold_prices_inr SET inr_price = %s WHERE date = %s;", (price, today_date))
            log_audit('UPDATE', f"Updated gold price for {today_date}: ₹{price}")
        else:
            cur.execute("INSERT INTO gold_prices_inr (date, inr_price) VALUES (%s, %s);", (today_date, price))
            log_audit('INSERT', f"Inserted new gold price for {today_date}: ₹{price}")

        conn.commit()
        cur.close()
        conn.close()

        # Also index the data in Elasticsearch
        index_gold_price(price, today_date)

    except Exception as e:
        log_audit('ERROR', f"Failed to insert gold price into the database: {e}")
# Main function to run the data pipeline
def main():
    print("Starting gold price data pipeline...")

    price = fetch_gold_price()
    if price:
        print(f"Fetched gold price: ₹{price} per ounce")
        price_per_gram = price / 31.1035  # Convert price per ounce to price per gram
        insert_gold_price(price_per_gram)
        print(f"Inserted/Updated gold price: ₹{price_per_gram} per gram")
    else:
        print("No price data available to insert.")

if __name__ == "__main__":
    main()
