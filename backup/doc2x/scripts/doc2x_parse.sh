#!/usr/bin/env bash
# doc2x_parse.sh - Parse PDF or image to Markdown via Doc2X API v2
#
# Usage:
#   doc2x_parse.sh <input_file> [output_dir]
#
# Environment:
#   DOC2X_KEY  - API key (required)
#
# Supports: .pdf, .jpg, .jpeg, .png
# Output: Markdown file + images extracted from the document

set -euo pipefail

BASE_URL="https://v2.doc2x.noedgeai.com"
POLL_INTERVAL=5
MAX_POLLS=180  # 15 min max

die() { echo "ERROR: $*" >&2; exit 1; }

[[ -z "${DOC2X_KEY:-}" ]] && die "DOC2X_KEY not set"
[[ $# -lt 1 ]] && die "Usage: doc2x_parse.sh <input_file> [output_dir]"

INPUT_FILE="$1"
[[ -f "$INPUT_FILE" ]] || die "File not found: $INPUT_FILE"

FILENAME=$(basename "$INPUT_FILE")
EXT="${FILENAME##*.}"
EXT_LOWER=$(echo "$EXT" | tr '[:upper:]' '[:lower:]')
BASENAME="${FILENAME%.*}"

# Determine output directory
if [[ -n "${2:-}" ]]; then
    OUTPUT_DIR="$2"
else
    YYYYMM=$(date +%Y%m)
    OUTPUT_DIR="/home/bushuhui/data-all/note/resources/${YYYYMM}/${BASENAME}"
fi
mkdir -p "$OUTPUT_DIR"

AUTH_HEADER="Authorization: Bearer ${DOC2X_KEY}"

echo "=== Doc2X Parse ==="
echo "Input:  $INPUT_FILE"
echo "Output: $OUTPUT_DIR"
echo "Type:   $EXT_LOWER"

# ─── PDF workflow (async: preupload → PUT → poll status → export md → poll export → download zip) ───
parse_pdf() {
    echo "--- Step 1: Preupload ---"
    PREUPLOAD=$(curl -sS -X POST "${BASE_URL}/api/v2/parse/preupload" \
        -H "$AUTH_HEADER")
    
    CODE=$(echo "$PREUPLOAD" | jq -r '.code')
    [[ "$CODE" == "success" ]] || die "Preupload failed: $PREUPLOAD"
    
    UPLOAD_URL=$(echo "$PREUPLOAD" | jq -r '.data.url')
    UID_VAL=$(echo "$PREUPLOAD" | jq -r '.data.uid')
    echo "UID: $UID_VAL"

    echo "--- Step 2: Upload file ---"
    HTTP_CODE=$(curl -sS -o /dev/null -w "%{http_code}" -X PUT "$UPLOAD_URL" \
        -H "Content-Type: application/pdf" \
        --data-binary "@${INPUT_FILE}")
    [[ "$HTTP_CODE" == "200" ]] || die "Upload failed with HTTP $HTTP_CODE"
    echo "Upload OK"

    echo "--- Step 3: Poll parse status ---"
    for i in $(seq 1 $MAX_POLLS); do
        STATUS_RESP=$(curl -sS "${BASE_URL}/api/v2/parse/status?uid=${UID_VAL}" \
            -H "$AUTH_HEADER")
        STATUS=$(echo "$STATUS_RESP" | jq -r '.data.status // .code')
        
        if [[ "$STATUS" == "success" ]]; then
            echo "Parse complete!"
            # Save raw result
            echo "$STATUS_RESP" | jq '.data.result' > "$OUTPUT_DIR/parse_result.json"
            break
        elif [[ "$STATUS" == "processing" || "$STATUS" == "pending" ]]; then
            PROGRESS=$(echo "$STATUS_RESP" | jq -r '.data.progress // "?"')
            echo "  [$i/$MAX_POLLS] Status: $STATUS (progress: $PROGRESS) ..."
            sleep $POLL_INTERVAL
        else
            die "Parse failed: $STATUS_RESP"
        fi
        
        [[ $i -eq $MAX_POLLS ]] && die "Parse timed out after $((MAX_POLLS * POLL_INTERVAL))s"
    done

    echo "--- Step 4: Export as Markdown ---"
    EXPORT_RESP=$(curl -sS -X POST "${BASE_URL}/api/v2/convert/parse" \
        -H "$AUTH_HEADER" \
        -H "Content-Type: application/json" \
        -d "{\"uid\":\"${UID_VAL}\",\"to\":\"md\",\"formula_mode\":\"normal\",\"filename\":\"${BASENAME}\"}")
    
    EXPORT_CODE=$(echo "$EXPORT_RESP" | jq -r '.code')
    [[ "$EXPORT_CODE" == "success" ]] || die "Export request failed: $EXPORT_RESP"
    echo "Export triggered"

    echo "--- Step 5: Poll export result ---"
    for i in $(seq 1 $MAX_POLLS); do
        RESULT_RESP=$(curl -sS "${BASE_URL}/api/v2/convert/parse/result?uid=${UID_VAL}" \
            -H "$AUTH_HEADER")
        R_STATUS=$(echo "$RESULT_RESP" | jq -r '.data.status // .code')
        
        if [[ "$R_STATUS" == "success" ]]; then
            DOWNLOAD_URL=$(echo "$RESULT_RESP" | jq -r '.data.url' | sed 's/\\u0026/\&/g')
            echo "Export complete!"
            break
        elif [[ "$R_STATUS" == "processing" ]]; then
            echo "  [$i] Exporting..."
            sleep 3
        else
            die "Export failed: $RESULT_RESP"
        fi
        
        [[ $i -eq $MAX_POLLS ]] && die "Export timed out"
    done

    echo "--- Step 6: Download result ---"
    ZIP_FILE="$OUTPUT_DIR/${BASENAME}_doc2x.zip"
    curl -sS -L -o "$ZIP_FILE" "$DOWNLOAD_URL"
    echo "Downloaded: $ZIP_FILE"

    echo "--- Step 7: Extract ---"
    unzip -o "$ZIP_FILE" -d "$OUTPUT_DIR/"
    rm -f "$ZIP_FILE"
    
    # Move images to images/ subfolder if not already there
    if [[ -d "$OUTPUT_DIR/images" ]]; then
        echo "Images extracted to $OUTPUT_DIR/images/"
    fi
    
    # Find the markdown file
    MD_FILE=$(find "$OUTPUT_DIR" -maxdepth 2 -name "*.md" -type f | head -1)
    if [[ -n "$MD_FILE" ]]; then
        echo "Markdown: $MD_FILE"
    fi
    
    echo "=== Done ==="
    echo "OUTPUT_DIR=$OUTPUT_DIR"
}

# ─── Image workflow (sync API, simpler) ───
parse_image() {
    echo "--- Uploading image (sync API) ---"
    RESP=$(curl -sS -X POST "${BASE_URL}/api/v2/parse/img/layout" \
        -H "$AUTH_HEADER" \
        --data-binary "@${INPUT_FILE}")
    
    CODE=$(echo "$RESP" | jq -r '.code')
    [[ "$CODE" == "success" ]] || die "Image parse failed: $RESP"
    
    # Extract markdown from result
    MD_CONTENT=$(echo "$RESP" | jq -r '.data.result.pages[0].md // empty')
    [[ -n "$MD_CONTENT" ]] || die "No markdown content in response"
    
    # Save markdown
    echo "$MD_CONTENT" > "$OUTPUT_DIR/${BASENAME}.md"
    echo "Markdown saved: $OUTPUT_DIR/${BASENAME}.md"
    
    # Extract images from convert_zip (base64 encoded zip)
    CONVERT_ZIP=$(echo "$RESP" | jq -r '.data.convert_zip // empty')
    if [[ -n "$CONVERT_ZIP" && "$CONVERT_ZIP" != "null" ]]; then
        echo "--- Extracting embedded images ---"
        mkdir -p "$OUTPUT_DIR/images"
        echo "$CONVERT_ZIP" | base64 -d > "$OUTPUT_DIR/_tmp_images.zip"
        unzip -o "$OUTPUT_DIR/_tmp_images.zip" -d "$OUTPUT_DIR/images/" 2>/dev/null || true
        rm -f "$OUTPUT_DIR/_tmp_images.zip"
        echo "Images extracted to $OUTPUT_DIR/images/"
        
        # Update image paths in markdown to use local paths
        if [[ -d "$OUTPUT_DIR/images" ]]; then
            # Replace image src references to point to local images/ directory
            cd "$OUTPUT_DIR"
            for img in images/*; do
                img_name=$(basename "$img")
                sed -i "s|src=\"${img_name}\"|src=\"images/${img_name}\"|g" "${BASENAME}.md" 2>/dev/null || true
            done
        fi
    fi
    
    # Save raw response for reference
    echo "$RESP" | jq '.' > "$OUTPUT_DIR/parse_result.json"
    
    echo "=== Done ==="
    echo "OUTPUT_DIR=$OUTPUT_DIR"
}

# ─── Dispatch ───
case "$EXT_LOWER" in
    pdf)
        parse_pdf
        ;;
    jpg|jpeg|png)
        parse_image
        ;;
    *)
        die "Unsupported file type: $EXT_LOWER (supported: pdf, jpg, jpeg, png)"
        ;;
esac
