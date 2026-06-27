import json
from django.core.management.base import BaseCommand
from news.models import Puzzle

class Command(BaseCommand):
    help = "Import puzzles from JSON"

    def handle(self, *args, **kwargs):
        with open("/home/aditta/Desktop/ChessNews/data_updated.json", "r") as f:
            data = json.load(f)

        puzzles = []

        for item in data:
            fen = item["fen"]

            puzzles.append(
                Puzzle(
                    title=f"Puzzle {item['title']}",
                    fen=fen,
                    turn=fen.split()[1],
                    solution=item["solve"],
                    difficulty=item["type"]
                )
            )

        Puzzle.objects.bulk_create(puzzles)

        self.stdout.write(
            self.style.SUCCESS(f"Imported {len(puzzles)} puzzles")
        )