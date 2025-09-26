import os
import django
from django.db import connection

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chessnews_project.settings')  # Replace with your project
django.setup()

def reset_sqlite_sequence(table_name):
    with connection.cursor() as cursor:
        # Get current max ID
        cursor.execute(f"SELECT MAX(id) FROM {table_name}")
        max_id = cursor.fetchone()[0] or 0

        # Update sqlite_sequence table
        cursor.execute(f"""
            INSERT OR REPLACE INTO sqlite_sequence(name, seq)
            VALUES ('{table_name}', {max_id});
        """)

    print(f"✅ ID sequence for table '{table_name}' reset. Next ID will be {max_id + 1}")

# Reset sequence for news_puzzle
reset_sqlite_sequence("news_puzzle")
