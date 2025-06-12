import os
import psycopg2
import pandas as pd
from psycopg2 import sql

# Set PostgreSQL connection details
DB_NAME = "bank_reviews"
DB_USER = "postgres"
DB_PASSWORD = "newpassword"  
DB_HOST = "localhost"
DB_PORT = "5432"

# Create DB connection
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
cur = conn.cursor()

# 1. Create banks table
cur.execute("""
CREATE TABLE IF NOT EXISTS banks (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);
""")

# 2. Create reviews table
cur.execute("""
CREATE TABLE IF NOT EXISTS reviews (
    id SERIAL PRIMARY KEY,
    bank_id INTEGER REFERENCES banks(id),
    review TEXT,
    rating INTEGER,
    date DATE,
    source TEXT,
    review_length INTEGER,
    sentiment_label TEXT,
    sentiment_score REAL,
    keywords TEXT,
    themes TEXT
);
""")
conn.commit()

# 3. Load and insert data from CSV files
CLEANED_DIR = "data/analysis"
for filename in os.listdir(CLEANED_DIR):
    if filename.endswith(".csv"):
        file_path = os.path.join(CLEANED_DIR, filename)
        print(f"Inserting from: {filename}")
        df = pd.read_csv(file_path)

        # Extract bank name from the filename
        bank_name = filename.split("_")[1].capitalize()

        # Insert bank if not exists and get bank_id
        cur.execute("INSERT INTO banks (name) VALUES (%s) ON CONFLICT (name) DO NOTHING;", (bank_name,))
        conn.commit()
        cur.execute("SELECT id FROM banks WHERE name = %s;", (bank_name,))
        bank_id = cur.fetchone()[0]

        for _, row in df.iterrows():
            cur.execute("""
                INSERT INTO reviews (
                    bank_id, review, rating, date, source,
                    review_length, sentiment_label, sentiment_score,
                    keywords, themes
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                bank_id,
                row['review'],
                int(row['rating']) if not pd.isna(row['rating']) else None,
                row['date'] if not pd.isna(row['date']) else None,
                row['source'],
                int(row['review_length']) if not pd.isna(row['review_length']) else None,
                row['sentiment_label'],
                float(row['sentiment_score']) if not pd.isna(row['sentiment_score']) else None,
                row['keywords'],
                row['themes']
            ))

        conn.commit()
        print(f"Inserted {len(df)} rows from {filename}")

# Close connection
cur.close()
conn.close()
print("✅ Done inserting cleaned data into PostgreSQL.")
