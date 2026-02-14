from stockfish import Stockfish
import chess

stockfish = Stockfish(
    path="/home/aditta/Downloads/stockfish-ubuntu-x86-64-avx2/stockfish/stockfish-ubuntu-x86-64-avx2",
    depth=16,
    parameters={"Threads": 2, "Minimum Thinking Time": 2, "Hash": 32}
)

def analyze_fen(fen):
    try:
        stockfish.set_fen_position(fen)
        
        # Get evaluation with timeout protection
        evaluation = stockfish.get_evaluation()
        uci_move = stockfish.get_best_move()
        
        san_move = None
        if uci_move:
            board = chess.Board(fen)
            move = chess.Move.from_uci(uci_move)
            if move in board.legal_moves:
                san_move = board.san(move)
        
        return {
            "evaluation": evaluation,
            "best_move_uci": uci_move,
            "best_move_san": san_move
        }
    except Exception as e:
        return {
            "error": str(e),
            "evaluation": {"type": "cp", "value": 0},
            "best_move_uci": None,
            "best_move_san": None
        }