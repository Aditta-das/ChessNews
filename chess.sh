#!/bin/bash

URL="https://app.chessvision.ai/predict"

# Temp files
JSON=$(mktemp --suffix=.json)
trap "rm -f ${JSON}" EXIT

# Input folder and output file
INPUT_FOLDER="extracted_images/medium"
OUTPUT_FEN="medium.txt"

# Reset output file
echo -n > "$OUTPUT_FEN"

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
    FEN="${FEN//_/ }"

    if [[ -z "$FEN" || "$FEN" == "null" ]]; then
        echo "[WARN] No valid FEN for $image_path" >&2
        return 1
    fi

    echo "$FEN"
    return 0
}

# ----------------------
# Process all images
# ----------------------
counter=1
shopt -s nullglob
for img in "$INPUT_FOLDER"/*.{png,jpg,jpeg,JPG,JPEG,PNG}; do
    echo "Processing $img ..."
    fen=$(get_fen_from_image "$img")
    if [ $? -eq 0 ]; then
        echo "medium-${counter} $(basename "$img") ${fen}" >> "$OUTPUT_FEN"
        ((counter++))
    else
        echo "[WARN] Skipping $img due to error"
    fi
done

echo "✅ Done. All FENs saved in $OUTPUT_FEN"
