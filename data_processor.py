import sqlite3
import csv
from collections import defaultdict

def main():
    # Connect to SQLite database
    conn = sqlite3.connect('shipdata.db')
    cursor = conn.cursor()

    # Create tables
    create_tables(cursor)
    
    # Process spreadsheets
    process_spreadsheet_0(cursor)
    process_spreadsheets_1_and_2(cursor)
    
    # Commit and close
    conn.commit()
    conn.close()
    print("Data processing complete!")

def create_tables(cursor):
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS shipping_data_0 (
        origin_warehouse TEXT,
        destination_store TEXT,
        product TEXT,
        on_time INTEGER,
        product_quantity INTEGER
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS shipments (
        shipment_identifier TEXT PRIMARY KEY,
        origin_warehouse TEXT,
        destination_store TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS shipment_products (
        shipment_identifier TEXT,
        product TEXT,
        on_time INTEGER,
        product_quantity INTEGER,
        FOREIGN KEY (shipment_identifier) REFERENCES shipments(shipment_identifier)
    )
    ''')

def process_spreadsheet_0(cursor):
    with open('shipping_data_0.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            cursor.execute('''
                INSERT INTO shipping_data_0 
                VALUES (?, ?, ?, ?, ?)
            ''', (
                row['origin_warehouse'],
                row['destination_store'],
                row['product'],
                1 if row['on_time'] == 'YES' else 0,
                int(row['product_quantity'])
            )

def process_spreadsheets_1_and_2(cursor):
    # Load shipment metadata from spreadsheet 2
    shipment_info = {}
    with open('shipping_data_2.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            shipment_id = row['shipment_identifier']
            shipment_info[shipment_id] = (row['origin_warehouse'], row['destination_store'])
            cursor.execute('''
                INSERT OR IGNORE INTO shipments 
                VALUES (?, ?, ?)
            ''', (shipment_id, *shipment_info[shipment_id]))

    # Process products from spreadsheet 1
    with open('shipping_data_1.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            shipment_id = row['shipment_identifier']
            cursor.execute('''
                INSERT INTO shipment_products 
                VALUES (?, ?, ?, ?)
            ''', (
                shipment_id,
                row['product'],
                1 if row['on_time'] == 'YES' else 0,
                int(row['product_quantity'])
            )

if __name__ == '__main__':
    main()
