# """
# Business logic for the daily puzzle feature.

# Uses ChessPuzzle / DailyPuzzle / ChessPuzzleSolve — independent of any
# pre-existing Puzzle model in the project.

# Requires `python-chess`:  pip install chess
# """
# import random

# import chess
# from django.utils import timezone

# from news.models import ChessPuzzle, DailyPuzzle, ChessPuzzleSolve

# SESSION_KEY_TMPL = "daily_puzzle_progress_{daily_puzzle_id}"


# # ---------------------------------------------------------------------------
# # Picking today's puzzle
# # ---------------------------------------------------------------------------

# def get_todays_daily_puzzle():
#     """
#     Returns today's DailyPuzzle instance (which has .puzzle -> ChessPuzzle),
#     auto-assigning + persisting one if nothing was scheduled for today.
#     Returns None if the ChessPuzzle pool is empty.
#     """
#     today = timezone.localdate()

#     existing = (
#         DailyPuzzle.objects.select_related("puzzle")
#         .filter(date=today)
#         .first()
#     )
#     if existing:
#         return existing

#     used_ids = DailyPuzzle.objects.values_list("puzzle_id", flat=True)
#     candidates = list(
#         ChessPuzzle.objects.exclude(id__in=used_ids).values_list("id", flat=True)
#     )
#     if not candidates:
#         # Whole pool has been used at least once — start recycling.
#         candidates = list(ChessPuzzle.objects.values_list("id", flat=True))
#     if not candidates:
#         return None

#     # Deterministic so concurrent requests today all land on the same puzzle.
#     rng = random.Random(today.toordinal())
#     chosen_id = rng.choice(candidates)

#     daily, _created = DailyPuzzle.objects.get_or_create(
#         date=today, defaults={"puzzle_id": chosen_id}
#     )
#     return daily


# # ---------------------------------------------------------------------------
# # Session progress helpers
# # ---------------------------------------------------------------------------

# def _session_key(daily_puzzle):
#     return SESSION_KEY_TMPL.format(daily_puzzle_id=daily_puzzle.id)


# def get_progress(request, daily_puzzle):
#     key = _session_key(daily_puzzle)
#     progress = request.session.get(key)
#     if progress is None:
#         progress = {
#             "index": 0,
#             "wrong_attempts": 0,
#             "started_at": timezone.now().isoformat(),
#         }
#         request.session[key] = progress
#     return progress


# def _save_progress(request, daily_puzzle, progress):
#     request.session[_session_key(daily_puzzle)] = progress
#     request.session.modified = True


# def _clear_progress(request, daily_puzzle):
#     request.session.pop(_session_key(daily_puzzle), None)
#     request.session.modified = True


# def _solution_moves(puzzle):
#     return puzzle.solution.split()


# def _board_after(puzzle, ply_count):
#     board = chess.Board(puzzle.fen)
#     for san in _solution_moves(puzzle)[:ply_count]:
#         board.push_san(san)
#     return board


# def has_already_solved(user, daily_puzzle):
#     if not user.is_authenticated:
#         return False
#     return ChessPuzzleSolve.objects.filter(user=user, daily_puzzle=daily_puzzle).exists()


# # ---------------------------------------------------------------------------
# # Move validation
# # ---------------------------------------------------------------------------

# class IllegalMoveError(Exception):
#     pass


# def submit_move(request, daily_puzzle, san):
#     """
#     Validates a single player move against the stored solution.
#     Returns {"correct": bool, "solved": bool, "fen": str, "wrong_attempts": int}.
#     Raises IllegalMoveError if `san` isn't a legal move in the position.
#     """
#     puzzle = daily_puzzle.puzzle
#     solution = _solution_moves(puzzle)
#     progress = get_progress(request, daily_puzzle)
#     index = progress["index"]

#     board = _board_after(puzzle, index)

#     try:
#         attempted_move = board.parse_san(san)
#     except ValueError:
#         raise IllegalMoveError("That's not a legal move in this position.")

#     if index >= len(solution):
#         return {"correct": True, "solved": True, "fen": board.fen(),
#                 "wrong_attempts": progress["wrong_attempts"]}

#     expected_move = board.parse_san(solution[index])

#     if attempted_move != expected_move:
#         progress["wrong_attempts"] += 1
#         _save_progress(request, daily_puzzle, progress)
#         return {
#             "correct": False,
#             "solved": False,
#             "fen": board.fen(),
#             "wrong_attempts": progress["wrong_attempts"],
#         }

#     board.push(attempted_move)
#     index += 1

#     # Auto-play the opponent's forced reply, if queued.
#     if index < len(solution):
#         opp_move = board.parse_san(solution[index])
#         board.push(opp_move)
#         index += 1

#     progress["index"] = index
#     solved = index >= len(solution)
#     _save_progress(request, daily_puzzle, progress)

#     if solved:
#         _record_solve(request, daily_puzzle, progress, gave_up=False)
#         _clear_progress(request, daily_puzzle)

#     return {
#         "correct": True,
#         "solved": solved,
#         "fen": board.fen(),
#         "wrong_attempts": progress["wrong_attempts"],
#     }


# # ---------------------------------------------------------------------------
# # Hints
# # ---------------------------------------------------------------------------

# def get_hint(request, daily_puzzle):
#     """
#     Returns a hint string, or None if the puzzle is already fully solved.
#     Uses the puzzle's custom `hint` text if set; otherwise reveals the SAN
#     of the next move the player needs to make.
#     """
#     puzzle = daily_puzzle.puzzle
#     solution = _solution_moves(puzzle)
#     progress = get_progress(request, daily_puzzle)
#     index = progress["index"]

#     if index >= len(solution):
#         return None

#     if puzzle.hint:
#         return puzzle.hint

#     return solution[index]


# # ---------------------------------------------------------------------------
# # Give up / reveal solution
# # ---------------------------------------------------------------------------

# def give_up(request, daily_puzzle):
#     """
#     Reveals the full solution and records the puzzle as solved
#     (made_mistake=True). Returns the list of SAN moves for client animation.
#     """
#     puzzle = daily_puzzle.puzzle
#     solution = _solution_moves(puzzle)
#     progress = get_progress(request, daily_puzzle)
#     progress["index"] = len(solution)
#     _record_solve(request, daily_puzzle, progress, gave_up=True)
#     _clear_progress(request, daily_puzzle)
#     return solution


# # ---------------------------------------------------------------------------
# # Recording completion
# # ---------------------------------------------------------------------------

# def _record_solve(request, daily_puzzle, progress, gave_up):
#     user = request.user
#     if not user.is_authenticated:
#         return

#     started_at = timezone.datetime.fromisoformat(progress["started_at"])
#     if timezone.is_naive(started_at):
#         started_at = timezone.make_aware(started_at)
#     time_taken = int((timezone.now() - started_at).total_seconds())

#     ChessPuzzleSolve.objects.get_or_create(
#         user=user,
#         daily_puzzle=daily_puzzle,
#         defaults={
#             "time_taken": time_taken,
#             "made_mistake": gave_up or progress["wrong_attempts"] > 0,
#             "wrong_attempts": progress["wrong_attempts"],
#         },
#     )