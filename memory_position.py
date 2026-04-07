import sqlite3
import json

# connect to DB
conn = sqlite3.connect('/home/aditta/Desktop/ChessNews/db.sqlite3')
cursor = conn.cursor()

# load JSON file
with open('easy_positions.json', 'r') as f:
    data = json.load(f)

# prepare rows
rows = [
    (
        item["fen"],
        item["difficulty"],
        item.get("game_name")  # safe if missing
    )
    for item in data
]

# insert
cursor.executemany("""
    INSERT INTO news_memoryposition (fen, difficulty, game_name)
    VALUES (?, ?, ?)
""", rows)

# save
conn.commit()
conn.close()

print("✅ Bulk insert successful!")