#!/bin/bash

URL="https://app.chessvision.ai/predict"

# Temp files
PNG=$(mktemp --suffix=.png)
JSON=$(mktemp --suffix=.json)
trap "rm -f ${PNG} ${JSON}" EXIT

# Output fen file
OUTPUT_FEN="fen_medium.txt"

# Function: send image to API and get fen
function get_fen_from_image() {
    local image_path="$1"

    # Convert image to jpeg base64
    JPEG_BASE64=$(convert "$image_path" jpeg:- | base64)

    # Create JSON payload
    cat <<EOF > "$JSON"
{
  "board_orientation": "predict",
  "cropped": true,
  "predict_turn": true,
  "image": "data:image/jpeg;base64,${JPEG_BASE64}"
}
EOF

    # Call API
    RESPONSE=$(curl --silent --data "@${JSON}" ${URL})
    if [ "$?" != "0" ]; then
        echo "[ERROR] curl failed for $image_path" >&2
        return 1
    fi

    # Extract fen
    FEN=$(echo "${RESPONSE}" | jq -r '.result')
    # Replace underscores with spaces in FEN
    FEN="${FEN//_/ }"

    if [[ -z "$FEN" || "$FEN" == "null" ]]; then
        echo "[WARN] No valid FEN for $image_path" >&2
        return 1
    fi

    echo "$FEN"
    return 0
}

# ----------------------
# Mode 1: Folder mode
# ----------------------
if [ -n "$1" ] && [ -d "$1" ]; then
    folder="$1"
    echo "Processing folder: $folder"
    echo -n > "$OUTPUT_FEN"  # empty fen.txt

    shopt -s nullglob

    for img in "$folder"/*.{png,jpg,jpeg,JPG,JPEG,PNG}; do
        echo "Processing $img ..."
        fen=$(get_fen_from_image "$img")
        if [ $? -eq 0 ]; then
            # Save: filename_without_path<tab>fen
	    echo "$(basename "$img")	${fen}" >> "$OUTPUT_FEN"
        else
            echo "[WARN] Skipping $img due to error"
        fi
    done
    echo "Done. All FENs saved in $OUTPUT_FEN"
    exit 0
fi

# ----------------------
# Mode 2: Screenshot mode (default)
# ----------------------

# Check screenshot tool
if command -v gnome-screenshot >/dev/null; then
    gnome-screenshot -a -f "${PNG}"
elif command -v flameshot >/dev/null; then
    flameshot gui --raw > "${PNG}"
elif command -v import >/dev/null; then
    import "${PNG}"
else
    echo "[ERROR] No screenshot tool found (gnome-screenshot, flameshot, or import)" >&2
    exit 1
fi

if [ "$(file -b --mime-type "${PNG}")" == "image/x-empty" ]; then
  echo "No screenshot taken, exiting."
  exit 1
fi

fen=$(get_fen_from_image "$PNG")
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to get FEN from screenshot" >&2
    exit 1
fi

echo "FEN from screenshot:"
echo "$fen"
