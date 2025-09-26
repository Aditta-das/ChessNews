from pdf2image import convert_from_path
from PIL import Image
import os

# --- CONFIG ---
PDF_PATH = "the-woodpecker-method.pdf"
OUTPUT_DIR = "extracted_puzzles/medium"
START_PAGE = 71 
END_PAGE = 196
DPI = 200

# Each box is (left, top, right, bottom)
CROP_BOXES = [
    (113, 242, 605, 710),    # Puzzle 1 (top-left)
    (116, 779, 560, 1244),   # Puzzle 2 (middle-left)
    (111, 1315, 563, 1776),  # Puzzle 3 (bottom-left)
    (733, 240, 1189, 709),   # Puzzle 4 (top-right)
    (734, 777, 1186, 1240),  # Puzzle 5 (middle-right)
    (741, 1313, 1188, 1773), # Puzzle 6 (bottom-right)
]

# --- SETUP ---
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- PROCESS EACH PAGE ---
for page_num in range(START_PAGE, END_PAGE + 1):
    print(f"📄 Processing page {page_num}...")

    try:
        pages = convert_from_path(PDF_PATH, dpi=DPI, first_page=page_num, last_page=page_num)
        page_img = pages[0]
    except Exception as e:
        print(f"❌ Failed to process page {page_num}: {e}")
        continue

    for i, box in enumerate(CROP_BOXES, start=1):
        puzzle_img = page_img.crop(box)
        filename = f"page{page_num:02}_puzzle{i:02}.png"
        puzzle_img.save(os.path.join(OUTPUT_DIR, filename))

print(f"✅ Done! Extracted puzzles from pages {START_PAGE} to {END_PAGE} into '{OUTPUT_DIR}/'")
