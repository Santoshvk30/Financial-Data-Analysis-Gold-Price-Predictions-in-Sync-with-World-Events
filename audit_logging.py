# audit_logging.py
import psycopg2
from datetime import datetime

# Database connection parameters
DB_NAME = "gold_prices"
DB_USER = "postgres"  # Replace with your PostgreSQL username
DB_PASSWORD = "Chinnu@220412"  # Replace with your PostgreSQL password
DB_HOST = "localhost"
DB_PORT = "5432"

# Function to retrieve and display audit logs
def display_audit_logs():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
        )
        cur = conn.cursor()

        # Retrieve the audit logs
        cur.execute("SELECT log_id, action, details, timestamp FROM audit_log ORDER BY timestamp DESC;")
        logs = cur.fetchall()

        print("Audit Logs:")
        for log in logs:
            log_id, action, details, timestamp = log
            print(f"[{timestamp}] {action} - {details} (Log ID: {log_id})")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"Failed to retrieve audit logs: {e}")

if __name__ == "__main__":
    display_audit_logs()
