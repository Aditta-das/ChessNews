import sqlite3

conn = sqlite3.connect('/home/aditta/Desktop/ChessNews/db.sqlite3')
cursor = conn.cursor()
cursor.execute("SELECT * FROM news_uploadedgame")
tables = cursor.fetchall()
print(tables)
