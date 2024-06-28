import sqlite3
import csv
import random
import time
from datetime import datetime, timedelta

# Database and CSV file names
db_name = "database/aniket_company_sales.db"
csv_file = "aniket_company_sales.csv"

# Product information
products = [
    ("001", "T-shirt", "Clothing", 19.99),
    ("002", "Jeans", "Clothing", 49.99),
    ("003", "Sneakers", "Footwear", 79.99),
    ("004", "Watch", "Accessories", 129.99),
    ("005", "Backpack", "Accessories", 39.99),
    ("006", "Dress", "Clothing", 69.99),
    ("007", "Sunglasses", "Accessories", 24.99),
    ("008", "Socks", "Clothing", 9.99),
    ("009", "Laptop Bag", "Accessories", 59.99),
    ("010", "Running Shoes", "Footwear", 89.99),
]

def create_connection():
    return sqlite3.connect(db_name)


def add_random_sale(conn):
    cursor = conn.cursor()

    # Generate random sale data
    date = (datetime.now() + timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d")
    product = random.choice(products)
    quantity = random.randint(1, 5)
    total_price = round(product[3] * quantity, 2)

    # Insert new sale into the database
    cursor.execute("""
    INSERT INTO aniket_company_sales (date, product_id, product_name, category, quantity, unit_price, total_price)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (date, product[0], product[1], product[2], quantity, product[3], total_price))

    conn.commit()
    print(f"Added new sale: {date}, {product[1]}, Quantity: {quantity}, Total: ${total_price}")


def main():
    conn = create_connection()

    while True:
        add_random_sale(conn)
        time.sleep(60)  # Wait for 1 minute


if __name__ == "__main__":
    main()