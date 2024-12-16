import psycopg2
import csv

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

# Path to your CSV file
csv_file_path = 'data/Prices.xlsx - Daily.csv'  # Replace with the correct path to your CSV file

# Open and read the CSV file
try:
    with open(csv_file_path, 'r') as file:
        reader = csv.reader(file)
        
        # Skip any initial non-data rows until you reach the data
        for _ in range(5):  # Adjust to skip known non-data rows
            next(reader)
        
        for row in reader:
            # Ensure the row has enough columns and contains data in the expected format
            if len(row) < 8 or not row[2].strip() or not row[7].strip():
                continue  # Skip incomplete or non-data rows
            
            try:
                # Extract date and INR price (assuming date is in column index 2 and INR is in index 7)
                date = row[2].strip()
                inr_price = row[7].replace(",", "").strip()  # Handle commas in numeric values

                # Skip rows where INR price is missing or invalid
                if not inr_price or inr_price == '#N/A':
                    continue

                # Convert INR price to float
                inr_price = float(inr_price)

                # Insert the data into the table
                cur.execute(
                    "INSERT INTO gold_prices_inr (date, inr_price) VALUES (%s, %s) ON CONFLICT (date) DO NOTHING;",
                    (date, inr_price)
                )

            except ValueError as e:
                print(f"Skipping row with invalid data: {row}")
                print(e)
            except Exception as e:
                print(f"Error inserting row: {row}")
                print(e)

    # Commit changes to the database
    conn.commit()
    print("Data inserted successfully.")

except Exception as e:
    print("Error reading CSV file.")
    print(e)

# Close the database connection
cur.close()
conn.close()
print("Database connection closed.")
