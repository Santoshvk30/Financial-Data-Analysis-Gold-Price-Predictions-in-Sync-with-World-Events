-- database_setup.sql
CREATE DATABASE gold_prices;

\c gold_prices

-- Create a table for storing gold price data in INR
CREATE TABLE gold_prices_inr (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    inr_price NUMERIC(10, 2) NOT NULL CHECK (inr_price > 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create an audit log table
CREATE TABLE audit_log (
    log_id SERIAL PRIMARY KEY,
    action VARCHAR(50) NOT NULL,
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create an index on the date column for faster queries
CREATE INDEX idx_date ON gold_prices_inr (date);
