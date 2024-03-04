import json
import sqlite3

def convert_to_json(db_file, table_name, output_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Select all rows from the specified table
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()

    # Get column names
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [col[1] for col in cursor.fetchall()]

    # Convert rows to dictionaries
    data = []
    for row in rows:
        row_dict = dict(zip(columns, row))
        data.append(row_dict)

    # Serialize data to JSON
    json_data = json.dumps(data, indent=4)

    # Write JSON data to file
    with open(output_file, 'w') as f:
        f.write(json_data)

    conn.close()

# Convert 'names' table to JSON
convert_to_json('supervin.db', 'names', 'names.json')

# Convert 'prices' table to JSON
convert_to_json('supervin.db', 'prices', 'prices.json')