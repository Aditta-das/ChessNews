import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chessnews_project.settings')  # 🔁 Replace with your actual project name
django.setup()

from news.models import Puzzle  # Uncomment and adjust based on your Django app

fen_file = "easy_puzzles.txt"  # Adjust path if needed

with open(fen_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

count = 0
for line in lines:
    if not line.strip():
        continue

    try:
        # Split line into title, puzzle image name, and fen
        parts = line.strip().split(maxsplit=2)
        if len(parts) != 3:
            print(f"Skipping malformed line: {line.strip()}")
            continue

        title, puzzle_name, fen = parts

        # Extract turn info from FEN
        fen_parts = fen.split(" ")
        if len(fen_parts) < 2:
            print(f"Skipping invalid FEN: {fen}")
            continue

        turn = fen_parts[1]  # 'w' or 'b'

        # Create Puzzle object (uncomment when using with Django)
        Puzzle.objects.create(
            title=title,
            fen=fen,
            turn=turn,
            solution="",
            difficulty="easy"  # change if needed
        )

        print(f"{title} - {puzzle_name} - {fen}")
        count += 1

    except Exception as e:
        print(f"Error processing line: {line.strip()}")
        print(f"Exception: {e}")
        continue

print(f"✅ Imported {count} puzzles from {fen_file}")
