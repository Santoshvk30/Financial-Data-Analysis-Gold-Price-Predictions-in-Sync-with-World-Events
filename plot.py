import psycopg2
import matplotlib.pyplot as plt

# Database connection parameters
DB_NAME = "gold_prices"
DB_USER = "postgres"  # Replace with your PostgreSQL username
DB_PASSWORD = "Chinnu@220412"  # Replace with your PostgreSQL password
DB_HOST = "localhost"  # Or your DB host
DB_PORT = "5432"  # Default PostgreSQL port

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

# Fetch data from the gold_prices_inr table
cur.execute("SELECT date, inr_price FROM gold_prices_inr ORDER BY date ASC;")
data = cur.fetchall()

# Close the database connection
cur.close()
conn.close()

# Extract the dates and prices for plotting
dates = [row[0] for row in data]
prices = [row[1] for row in data]
print(dates)
print(prices)

# Plotting the data
plt.figure(figsize=(10, 6))
plt.plot(dates, prices, label="Gold Price (per gram)", color='gold')
plt.title("Gold Prices Over Time (Per Gram)")
plt.xlabel("Date")
plt.ylabel("Price (INR)")
plt.xticks(rotation=45)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig('gold_prices_plot.png')  # Save the plot to a file
print("Plot saved as 'gold_prices_plot.png'")
