# Save as chess_api.py

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from PIL import Image
import io
import numpy as np
import uvicorn

app = FastAPI()

# Map class index to piece symbol in FEN
# 0=empty, 1=wP,2=wN,3=wB,4=wR,5=wQ,6=wK, 7=bP,8=bN,9=bB,10=bR,11=bQ,12=bK
piece_classes = [' ', 'P', 'N', 'B', 'R', 'Q', 'K', 'p', 'n', 'b', 'r', 'q', 'k']

def dummy_piece_classifier(square_img: Image.Image) -> int:
    # Dummy classifier: Always return empty square (0)
    # Replace this function with your ML model inference
    return 0

def image_to_fen(image: Image.Image) -> str:
    # Resize the image to 800x800 for uniform slicing (assuming square chessboard)
    image = image.convert('RGB')
    board_size = 800
    image = image.resize((board_size, board_size))

    square_size = board_size // 8

    pieces = []
    for rank in range(8):
        rank_pieces = []
        for file in range(8):
            left = file * square_size
            top = rank * square_size
            right = left + square_size
            bottom = top + square_size
            square_img = image.crop((left, top, right, bottom))

            piece_idx = dummy_piece_classifier(square_img)
            rank_pieces.append(piece_classes[piece_idx])
        pieces.append(rank_pieces)

    # Convert to FEN string
    # FEN ranks go from 8 (top) to 1 (bottom), so we reverse the pieces list
    fen_rows = []
    for rank_pieces in pieces:
        fen_row = ''
        empty_count = 0
        for p in rank_pieces:
            if p == ' ':
                empty_count += 1
            else:
                if empty_count > 0:
                    fen_row += str(empty_count)
                    empty_count = 0
                fen_row += p
        if empty_count > 0:
            fen_row += str(empty_count)
        fen_rows.append(fen_row)
    fen_rows.reverse()  # because image rank 0 is top = rank 8 in chess

    fen_position = '/'.join(fen_rows)

    # For simplicity, add standard FEN suffix
    fen = fen_position + " w KQkq - 0 1"  # default active color, castling, etc.

    return fen

@app.post("/chess-to-fen/")
async def chess_to_fen(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes))

        fen = image_to_fen(image)

        return JSONResponse(content={"fen": fen})
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})


if __name__ == "__main__":
    uvicorn.run("fapi:app", host="127.0.0.2", port=5000, reload=True)
