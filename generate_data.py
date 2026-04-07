import random
import json

def generate_easy_fen():
    # 1. Initialize empty board
    board = [['' for _ in range(8)] for _ in range(8)]
    
    # 2. Place Kings (Mandatory: 2 pieces)
    positions = [(r, c) for r in range(8) for c in range(8)]
    random.shuffle(positions)
    
    wk_pos = positions.pop()
    bk_pos = positions.pop()
    board[wk_pos[0]][wk_pos[1]] = 'K'
    board[bk_pos[0]][bk_pos[1]] = 'k'

    # 3. Determine how many EXTRA pieces to add (1 to 4 extra to hit 3-6 total)
    extra_pieces_count = random.randint(1, 4)
    
    # Pool of pieces (excluding kings)
    piece_pool = ['P', 'R', 'N', 'B', 'Q', 'p', 'r', 'n', 'b', 'q']
    
    placed = 0
    while placed < extra_pieces_count:
        r, c = positions.pop()
        
        # Simple rule: No pawns on back ranks
        piece = random.choice(piece_pool)
        if piece.lower() == 'p' and (r == 0 or r == 7):
            continue
            
        board[r][c] = piece
        placed += 1

    # 4. Convert 2D array to FEN format
    fen_rows = []
    for row in board:
        empty = 0
        res = ""
        for cell in row:
            if cell == '':
                empty += 1
            else:
                if empty > 0:
                    res += str(empty)
                    empty = 0
                res += cell
        if empty > 0:
            res += str(empty)
        fen_rows.append(res)
    
    return "/".join(fen_rows) + " w - - 0 1"

# Generate 100 entries
data = []
for i in range(100):
    data.append({
        "fen": generate_easy_fen(),
        "difficulty": "easy",
        "game_name": f"Easy Memory Drill #{i+1}"
    })

# Save to JSON
with open('easy_positions.json', 'w') as f:
    json.dump(data, f, indent=4)

print("Generated 100 easy positions (3-6 pieces each) in easy_positions.json")