import threading
import requests
import chess

from stockfish import Stockfish


STOCKFISH_PATH = (
    "/home/aditta/Downloads/"
    "stockfish-ubuntu-x86-64-avx2/stockfish/"
    "stockfish-ubuntu-x86-64-avx2"
)


# =========================================================
# STOCKFISH STATE
# =========================================================

stockfish = None
stockfish_lock = threading.Lock()
stockfish_init_lock = threading.Lock()


# =========================================================
# CREATE STOCKFISH LAZILY
# =========================================================

def get_stockfish():
    """
    Create Stockfish only when it is actually needed.

    If Stockfish cannot be initialized, return None.
    This allows the Lichess API fallback to work.
    """

    global stockfish

    if stockfish is not None:
        return stockfish

    with stockfish_init_lock:

        # Another request may have initialized it
        # while we were waiting for the lock.
        if stockfish is not None:
            return stockfish

        try:

            stockfish = Stockfish(
                path=STOCKFISH_PATH,
                depth=11,
                parameters={
                    "Threads": 2,
                    "Hash": 64,
                    "Minimum Thinking Time": 0,
                }
            )

            return stockfish

        except Exception as e:

            print(
                "Stockfish initialization failed:",
                str(e)
            )

            stockfish = None

            return None


# =========================================================
# LICHESS CLOUD EVALUATION FALLBACK
# =========================================================

def analyze_fen_via_lichess(fen):
    """
    Analyze a FEN using the free Lichess Cloud Evaluation API.

    Returns the same format as local Stockfish.
    """

    try:

        response = requests.get(
            "https://lichess.org/api/cloud-eval",
            params={
                "fen": fen,
                "multiPv": 1,
            },
            timeout=5
        )

        if response.status_code != 200:

            return {
                "error": (
                    "Lichess API returned HTTP "
                    f"{response.status_code}"
                ),
                "evaluation": {
                    "type": "cp",
                    "value": 0
                },
                "best_move_uci": None,
                "best_move_san": None,
            }


        data = response.json()

        pvs = data.get("pvs") or []

        if not pvs:

            return {
                "error": "No cloud evaluation available",
                "evaluation": {
                    "type": "cp",
                    "value": 0
                },
                "best_move_uci": None,
                "best_move_san": None,
            }


        pv = pvs[0]


        # =================================================
        # EVALUATION
        # =================================================

        mate = pv.get("mate")

        cp = pv.get("cp")


        if mate is not None:

            evaluation = {
                "type": "mate",
                "value": mate
            }

        else:

            evaluation = {
                "type": "cp",
                "value": cp if cp is not None else 0
            }


        # =================================================
        # BEST MOVE
        # =================================================

        moves_string = pv.get("moves", "")

        best_move_uci = (
            moves_string.split()[0]
            if moves_string
            else None
        )


        best_move_san = None


        if best_move_uci:

            try:

                board = chess.Board(fen)

                move = chess.Move.from_uci(
                    best_move_uci
                )

                if move in board.legal_moves:

                    best_move_san = board.san(move)

            except Exception as e:

                print(
                    "Lichess SAN conversion failed:",
                    str(e)
                )


        return {
            "evaluation": evaluation,
            "best_move_uci": best_move_uci,
            "best_move_san": best_move_san,
            "source": "lichess",
        }


    except requests.RequestException as e:

        print(
            "Lichess API request failed:",
            str(e)
        )

    except Exception as e:

        print(
            "Lichess API analysis failed:",
            str(e)
        )


    # =====================================================
    # ULTIMATE FALLBACK
    # =====================================================

    return {
        "error": "Both Stockfish and Lichess analysis failed",
        "evaluation": {
            "type": "cp",
            "value": 0
        },
        "best_move_uci": None,
        "best_move_san": None,
    }


# =========================================================
# SINGLE POSITION ANALYSIS
# =========================================================

def analyze_fen(fen, include_best_move=True):

    # Validate FEN first
    try:

        board = chess.Board(fen)

    except Exception as e:

        return {
            "error": f"Invalid FEN: {str(e)}",
            "evaluation": {
                "type": "cp",
                "value": 0
            },
            "best_move_uci": None,
            "best_move_san": None,
        }


    # =====================================================
    # TRY LOCAL STOCKFISH
    # =====================================================

    engine = get_stockfish()


    if engine is not None:

        try:

            with stockfish_lock:

                engine.set_fen_position(fen)

                evaluation = engine.get_evaluation()


                best_move_uci = None
                best_move_san = None


                if include_best_move:

                    best_move_uci = (
                        engine.get_best_move()
                    )


                    if best_move_uci:

                        try:

                            move = chess.Move.from_uci(
                                best_move_uci
                            )

                            if move in board.legal_moves:

                                best_move_san = board.san(
                                    move
                                )

                        except Exception as e:

                            print(
                                "Stockfish SAN conversion failed:",
                                str(e)
                            )


                return {
                    "evaluation": evaluation,
                    "best_move_uci": best_move_uci,
                    "best_move_san": best_move_san,
                    "source": "stockfish",
                }


        except Exception as e:

            print(
                "Stockfish analysis failed:",
                str(e)
            )

            # IMPORTANT:
            # Disable the broken engine so future requests
            # immediately use Lichess instead of repeatedly
            # trying a broken process.

            global stockfish

            stockfish = None


    # =====================================================
    # STOCKFISH FAILED
    # USE LICHESS
    # =====================================================

    print(
        "Using Lichess Cloud Evaluation fallback."
    )


    result = analyze_fen_via_lichess(fen)


    # If caller does not need best move,
    # remove it from the response.

    if not include_best_move:

        result["best_move_uci"] = None
        result["best_move_san"] = None


    return result


# =========================================================
# FULL GAME ANALYSIS
# =========================================================

def analyze_fens(fens):

    results = []


    for fen in fens:

        result = analyze_fen(
            fen,
            include_best_move=False
        )


        results.append({
            "evaluation": result.get(
                "evaluation",
                {
                    "type": "cp",
                    "value": 0
                }
            ),

            "source": result.get(
                "source",
                "unknown"
            )
        })


    return results


# =========================================================
# CLASSIFICATION HELPERS
# =========================================================

MATE_SCORE = 100000

PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0,
}


def _score_to_cp(evaluation):
    """Collapse an evaluation dict into a single comparable number.
    Mate scores are pushed far outside the normal cp range so
    comparisons/thresholds still behave sensibly."""

    if not evaluation:
        return 0

    if evaluation.get("type") == "mate":
        mate = evaluation["value"]
        return MATE_SCORE - abs(mate) if mate > 0 else -(MATE_SCORE - abs(mate))

    return evaluation.get("value", 0)


def _flip_eval(evaluation):
    """Evaluations coming out of analyze_fen are relative to whoever
    is to move in that FEN. To compare two consecutive positions from
    a single player's perspective, the second one needs flipping."""

    if not evaluation:
        return evaluation

    if evaluation.get("type") == "mate":
        return {"type": "mate", "value": -evaluation["value"]}

    return {"type": "cp", "value": -evaluation.get("value", 0)}


def _material_for_color(board, color):

    total = 0

    for piece_type, value in PIECE_VALUES.items():

        total += value * len(board.pieces(piece_type, color))

    return total


# =========================================================
# TOP MOVES (for "was this the best move / only good move")
# =========================================================

def get_top_moves(fen, multipv=3, depth=11):
    """Return up to `multipv` candidate moves with evaluations,
    best first, from the perspective of the side to move."""

    engine = get_stockfish()

    if engine is not None:

        try:

            with stockfish_lock:

                engine.set_fen_position(fen)
                engine.set_depth(depth)

                raw = engine.get_top_moves(multipv)

                results = []

                for m in raw:

                    if m.get("Mate") is not None:
                        ev = {"type": "mate", "value": m["Mate"]}
                    else:
                        ev = {"type": "cp", "value": m.get("Centipawn", 0)}

                    results.append({
                        "move": m.get("Move"),
                        "evaluation": ev,
                    })

                if results:
                    return results

        except Exception as e:

            print("get_top_moves (stockfish) failed:", str(e))

            global stockfish
            stockfish = None

    # Fallback: Lichess cloud eval also supports multiPv
    return get_top_moves_via_lichess(fen, multipv)


def get_top_moves_via_lichess(fen, multipv=3):

    try:

        response = requests.get(
            "https://lichess.org/api/cloud-eval",
            params={"fen": fen, "multiPv": multipv},
            timeout=5
        )

        if response.status_code != 200:
            return []

        data = response.json()
        pvs = data.get("pvs") or []

        results = []

        for pv in pvs:

            mate = pv.get("mate")
            cp = pv.get("cp")

            ev = (
                {"type": "mate", "value": mate}
                if mate is not None
                else {"type": "cp", "value": cp if cp is not None else 0}
            )

            moves_string = pv.get("moves", "")
            move_uci = moves_string.split()[0] if moves_string else None

            results.append({"move": move_uci, "evaluation": ev})

        return results

    except Exception as e:

        print("get_top_moves (lichess) failed:", str(e))
        return []


# =========================================================
# SINGLE-MOVE CLASSIFICATION
# =========================================================

def classify_move(fen_before, played_move_uci, eval_before, eval_after, top_moves):
    """
    eval_before: evaluation dict at fen_before, from the MOVER's perspective
    eval_after:  evaluation dict after the move, from the MOVER's perspective
    top_moves:   result of get_top_moves(fen_before), best move first

    Returns one of:
    brilliant, great, best, excellent, good, inaccuracy, mistake, blunder, miss
    """

    board = chess.Board(fen_before)
    mover_color = board.turn

    cp_before = _score_to_cp(eval_before)
    cp_after = _score_to_cp(eval_after)

    cp_loss = max(0, cp_before - cp_after)

    best_uci = top_moves[0]["move"] if top_moves else None
    is_best = played_move_uci == best_uci

    best_cp = _score_to_cp(top_moves[0]["evaluation"]) if top_moves else cp_before
    second_cp = (
        _score_to_cp(top_moves[1]["evaluation"])
        if len(top_moves) > 1
        else None
    )

    # "Only good move" = a big gap between 1st and 2nd choice
    only_good_move = second_cp is not None and (best_cp - second_cp) >= 150

    # ---------------------------------------------------
    # MISS: position was winning, and this move throws
    # most of it away (even if not the single worst move).
    # ---------------------------------------------------
    was_winning = cp_before >= 300 or (
        eval_before and eval_before.get("type") == "mate" and eval_before["value"] > 0
    )

    if was_winning and cp_loss >= 200 and not is_best:
        return "miss"

    # ---------------------------------------------------
    # BRILLIANT: the best move, voluntarily gives up
    # material, and the mover is still fine afterwards.
    # ---------------------------------------------------
    try:

        move = chess.Move.from_uci(played_move_uci)

        material_before = _material_for_color(board, mover_color)

        board_after = board.copy()
        board_after.push(move)

        material_after = _material_for_color(board_after, mover_color)

        gave_up_material = material_after < material_before

        if is_best and gave_up_material and cp_after >= -50:
            return "brilliant"

    except Exception:
        pass

    # ---------------------------------------------------
    # GREAT: the best move, and it was the only move that
    # kept the position from swinging badly.
    # ---------------------------------------------------
    if is_best and only_good_move and cp_loss <= 20:
        return "great"

    if is_best:
        return "best"

    # ---------------------------------------------------
    # Standard centipawn-loss buckets
    # ---------------------------------------------------
    if cp_loss <= 20:
        return "excellent"
    if cp_loss <= 50:
        return "good"
    if cp_loss <= 100:
        return "inaccuracy"
    if cp_loss <= 300:
        return "mistake"

    return "blunder"


# =========================================================
# FULL GAME CLASSIFICATION
# =========================================================

def analyze_game_with_classification(fens, moves_uci):
    """
    fens:      [pos0, pos1, ..., posN]  (N+1 positions)
    moves_uci: [move1, ..., moveN]      (N moves), moves_uci[i] goes
               from fens[i] to fens[i+1]

    Returns a list of length N+1: classifications[0] is always None
    (no move led to the starting position), classifications[i] is the
    label for moves_uci[i-1].
    """

    position_evals = analyze_fens(fens)  # cheap, single-line eval per position

    classifications = [None]

    for i, move_uci in enumerate(moves_uci):

        fen_before = fens[i]

        eval_before = position_evals[i]["evaluation"]           # already mover-relative
        eval_after = _flip_eval(position_evals[i + 1]["evaluation"])

        top_moves = get_top_moves(fen_before, multipv=3)

        label = classify_move(
            fen_before,
            move_uci,
            eval_before,
            eval_after,
            top_moves,
        )

        classifications.append(label)

    return classifications