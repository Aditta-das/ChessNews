import random

import ijson

from django.core.management.base import BaseCommand
from django.db import transaction

from news.models import ChessPuzzle


class Command(BaseCommand):

    help = "Import chess puzzles without loading the whole JSON into RAM"

    # ========================================================
    # CONFIG
    # ========================================================

    TARGET = 120

    MEDIUM_PERCENT = 0.60

    JSON_FILE = "/home/aditta/Downloads/chesspgn/puzzles_converted.json"

    # ========================================================
    # HANDLE
    # ========================================================

    def handle(self, *args, **options):

        self.stdout.write("Starting...")
        self.stdout.flush()

        self.stdout.write(
            f"Loading {self.JSON_FILE}..."
        )
        self.stdout.flush()

        # ====================================================
        # TARGET
        # ====================================================

        medium_target = int(
            self.TARGET * self.MEDIUM_PERCENT
        )

        hard_target = (
            self.TARGET - medium_target
        )

        self.stdout.write(
            f"Target: {self.TARGET}"
        )

        self.stdout.write(
            f"Medium: {medium_target}"
        )

        self.stdout.write(
            f"Hard: {hard_target}"
        )

        self.stdout.flush()

        # ====================================================
        # STREAM JSON
        # ====================================================

        medium = []
        hard = []

        total_read = 0

        self.stdout.write(
            "Reading JSON one puzzle at a time..."
        )
        self.stdout.flush()

        try:

            with open(
                self.JSON_FILE,
                "rb"
            ) as f:

                for puzzle in ijson.items(
                    f,
                    "item"
                ):

                    total_read += 1

                    if total_read % 100000 == 0:

                        self.stdout.write(
                            f"Read {total_read:,} puzzles..."
                        )

                        self.stdout.flush()

                    rating = puzzle.get("rating")

                    if rating is None:
                        continue

                    try:

                        rating = int(rating)

                    except (ValueError, TypeError):

                        continue

                    # ----------------------------------------
                    # Medium
                    # ----------------------------------------

                    if 1400 <= rating < 1800:

                        medium.append(puzzle)

                    # ----------------------------------------
                    # Hard
                    # ----------------------------------------

                    elif rating >= 1800:

                        hard.append(puzzle)

                    # ----------------------------------------
                    # We already have enough
                    # ----------------------------------------

                    if (
                        len(medium) >= medium_target
                        and
                        len(hard) >= hard_target
                    ):

                        break

        except Exception as e:

            self.stdout.write(
                self.style.ERROR(
                    f"ERROR while reading JSON: {e}"
                )
            )

            return

        # ====================================================
        # RESULTS
        # ====================================================

        self.stdout.write("")
        self.stdout.write(
            f"Read: {total_read:,} puzzles"
        )

        self.stdout.write(
            f"Medium found: {len(medium)}"
        )

        self.stdout.write(
            f"Hard found: {len(hard)}"
        )

        self.stdout.flush()

        # ====================================================
        # CHECK
        # ====================================================

        if len(medium) < medium_target:

            self.stdout.write(
                self.style.ERROR(
                    f"Not enough Medium puzzles. "
                    f"Need {medium_target}, "
                    f"found {len(medium)}."
                )
            )

            return

        if len(hard) < hard_target:

            self.stdout.write(
                self.style.ERROR(
                    f"Not enough Hard puzzles. "
                    f"Need {hard_target}, "
                    f"found {len(hard)}."
                )
            )

            return

        # ====================================================
        # SELECT
        # ====================================================

        selected = (
            random.sample(
                medium,
                medium_target
            )
            +
            random.sample(
                hard,
                hard_target
            )
        )

        random.shuffle(selected)

        self.stdout.write("")
        self.stdout.write(
            f"Selected {len(selected)} puzzles."
        )

        # ====================================================
        # PREPARE OBJECTS
        # ====================================================

        objects = []

        for number, puzzle in enumerate(
            selected,
            start=1
        ):

            fen = str(
                puzzle.get("fen", "")
            ).strip()

            solution = str(
                puzzle.get("san", "")
            ).strip()

            if not fen or not solution:

                continue

            parts = fen.split()

            if len(parts) != 6:

                continue

            turn = parts[1]

            if turn not in ("w", "b"):

                continue

            rating = int(
                puzzle["rating"]
            )

            # ----------------------------------------------
            # Difficulty
            # ----------------------------------------------

            if rating < 1800:

                difficulty = "medium"

            else:

                difficulty = "hard"


            # ----------------------------------------------
            # Object
            # ----------------------------------------------

            objects.append(
                ChessPuzzle(
                    title=f"Daily Puzzles {number}",
                    fen=fen,
                    turn=turn,
                    solution=solution,
                    hint="",
                    difficulty=difficulty,
                )
            )

        self.stdout.write(
            f"Prepared {len(objects)} puzzles."
        )

        self.stdout.flush()

        # ====================================================
        # INSERT
        # ====================================================

        if not objects:

            self.stdout.write(
                self.style.ERROR(
                    "No valid puzzles found."
                )
            )

            return

        self.stdout.write(
            "Inserting into database..."
        )

        self.stdout.flush()

        try:

            with transaction.atomic():

                ChessPuzzle.objects.bulk_create(
                    objects,
                    batch_size=100
                )

        except Exception as e:

            self.stdout.write(
                self.style.ERROR(
                    f"DATABASE ERROR: {e}"
                )
            )

            return

        # ====================================================
        # DONE
        # ====================================================

        total = ChessPuzzle.objects.count()

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                f"SUCCESS! Inserted {len(objects)} puzzles."
            )
        )

        self.stdout.write(
            f"Total ChessPuzzle rows: {total}"
        )
