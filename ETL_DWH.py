
import os
from dotenv import load_dotenv
import psycopg2
import pandas as pd

load_dotenv()

source_conn = psycopg2.connect(os.getenv("SOURCE_DB"))
source_cursor = source_conn.cursor()

dwh_conn = psycopg2.connect(os.getenv("DWH_DB"))
dwh_cursor = dwh_conn.cursor()

source_cursor.execute("""
    SELECT id, CONCAT(first_name, ' ', last_name), email, date_joined
    FROM users_customuser
""")
for row in source_cursor.fetchall():
    dwh_cursor.execute("""
        INSERT INTO dim_customer (customer_id, name, email, date_joined)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (customer_id) DO NOTHING
    """, row)

source_cursor.execute("""
    SELECT id, name, price, category
    FROM products_product
""")
for row in source_cursor.fetchall():
    dwh_cursor.execute("""
        INSERT INTO dim_product (product_id, name, price, category)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (product_id) DO NOTHING
    """, row)
  
source_cursor.execute("""
    SELECT id, user_id, product_id, quantity, total_price, status, created_at
    FROM orders_order
""")
for row in source_cursor.fetchall():
    dwh_cursor.execute("""
        INSERT INTO fact_order (order_id, customer_id, product_id, quantity, total, status, order_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (order_id) DO NOTHING
    """, row)

dwh_conn.commit()

source_cursor.close()
source_conn.close()
dwh_cursor.close()
dwh_conn.close()

print("ETL completado correctamente")
