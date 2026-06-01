import os
import csv
import psycopg2

OLD_DB_URL = "postgresql://neondb_owner:npg_IyqR7e3lrNuP@ep-jolly-forest-ahoqlpl3-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"

try:
    print("Connecting to old database...")
    conn = psycopg2.connect(OLD_DB_URL)
    cur = conn.cursor()
    print("Connected! Fetching data...")
    cur.execute("SELECT slug, monitoring_url, source_type, last_scraped_hash FROM public_gallery")
    rows = cur.fetchall()
    
    with open("fresh_monitoring_backup.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["slug", "monitoring_url", "source_type", "last_scraped_hash"])
        for row in rows:
            writer.writerow(row)
            
    print(f"Success! Exported {len(rows)} rows to fresh_monitoring_backup.csv")
    cur.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
