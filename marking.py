# import json

# # Load JSON file
# with open("data.json", "r") as f:
#     puzzles = json.load(f)

# # Add type field based on puzzle_no
# for puzzle in puzzles:
#     no = puzzle["puzzle_no"]

#     if 1 <= no <= 222:
#         puzzle["type"] = "easy"
#     elif 223 <= no <= 984:
#         puzzle["type"] = "medium"
#     else:
#         puzzle["type"] = "hard"

# # Save updated JSON
# with open("data_updated.json", "w") as f:
#     json.dump(puzzles, f, indent=4)

# print("Updated JSON saved to puzzles_updated.json")


import json

# Load files
with open("data_updated.json", "r", encoding="utf-8") as f:
    puzzles = json.load(f)

with open("titles.json", "r", encoding="utf-8") as f:
    titles = json.load(f)

# Add titles to puzzles
for puzzle, title_data in zip(puzzles, titles):
    puzzle["title"] = title_data["title"]

# Save updated file
with open("data_updated.json", "w", encoding="utf-8") as f:
    json.dump(puzzles, f, indent=4, ensure_ascii=False)

print("Titles added successfully.")