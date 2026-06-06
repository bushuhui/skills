#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Defaults
PROMPT=""
MODEL="gpt-image-2-beta"
SIZE="1:1"
RESOLUTION="1K"
N=1
QUALITY="medium"
IMAGE_URLS=()
OUTPUT="./generated.png"
DOWNLOAD=true

usage() {
  cat <<'EOF'
Usage: generate.sh --prompt "描述" [options]

Required:
  --prompt          图片描述（必填）

Options:
  --model           模型名称 (默认: gpt-image-2)
  --size            图片尺寸 (默认: 1:1)，支持 auto、1:1、16:9、9:16
  --resolution      分辨率 (默认: 1K)，支持 1K、2K、4K
  --n               生成数量 (默认: 1)，范围 1-10
  --quality         图片质量 (默认: medium)，支持 high、medium、low
  --image-url       原图 URL（可传多个）
  --output          输出文件路径 (默认: ./generated.png)
  --no-download     仅打印 URL，不下载
  --help            显示帮助
EOF
  exit 0
}

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --prompt) PROMPT="$2"; shift 2 ;;
    --model) MODEL="$2"; shift 2 ;;
    --size) SIZE="$2"; shift 2 ;;
    --resolution) RESOLUTION="$2"; shift 2 ;;
    --n) N="$2"; shift 2 ;;
    --quality) QUALITY="$2"; shift 2 ;;
    --image-url) IMAGE_URLS+=("$2"); shift 2 ;;
    --output) OUTPUT="$2"; shift 2 ;;
    --no-download) DOWNLOAD=false; shift ;;
    --help) usage ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

if [ -z "$PROMPT" ]; then
  echo "Error: --prompt is required"
  usage
fi

API_KEY="${AICODEWITH_API_KEY:-}"
if [ -z "$API_KEY" ]; then
  echo "Error: AICODEWITH_API_KEY environment variable is not set"
  exit 1
fi

BASE_URL="https://api.aicodewith.com"
WEBDAV_BASE="https://pub.adv-ci.com"
WEBDAV_DIR="pi-pinter"

# Upload local image to webdav, return public URL
upload_to_webdav() {
  local local_file="$1"
  if [ ! -f "$local_file" ]; then
    echo "Error: local file not found: $local_file" >&2
    return 1
  fi

  local filename
  filename="$(basename "$local_file")"
  # Generate unique name to avoid collision
  local unique_name
  unique_name="$(date +%s%N)_${filename}"
  local remote_path="${WEBDAV_DIR}/${unique_name}"
  local public_url="${WEBDAV_BASE}/${remote_path}"

  # Ensure directory exists
  curl -s -o /dev/null -X MKCOL "${WEBDAV_BASE}/${WEBDAV_DIR}/"

  # Upload file
  local http_code
  http_code=$(curl -s -o /dev/null -w "%{http_code}" -X PUT -T "$local_file" "${WEBDAV_BASE}/${remote_path}")

  if [[ "$http_code" =~ ^2[0-9][0-9]$ ]]; then
    echo "$public_url"
    return 0
  else
    echo "Error: upload failed with HTTP $http_code" >&2
    return 1
  fi
}

# Process image sources: local files -> upload to webdav, URLs -> pass through
process_image_sources() {
  local urls=()
  for src in "${IMAGE_URLS[@]}"; do
    if [[ -f "$src" ]]; then
      # Local file, upload to webdav
      echo "  Uploading local file: $src" >&2
      local url
      url=$(upload_to_webdav "$src")
      if [ $? -eq 0 ]; then
        urls+=("$url")
        echo "  Uploaded to: $url" >&2
      else
        return 1
      fi
    elif [[ "$src" =~ ^https?:// ]]; then
      # Already a URL
      urls+=("$src")
    else
      echo "Warning: not a valid URL or local file, skipping: $src" >&2
    fi
  done
  # Output as JSON array
  if [ ${#urls[@]} -eq 0 ]; then
    echo "[]"
  else
    printf '%s\n' "${urls[@]}" | jq -R . | jq -s .
  fi
}

# Build JSON body - gpt-image-2-beta doesn't support quality/resolution
if [ ${#IMAGE_URLS[@]} -gt 0 ]; then
  image_urls_json=$(process_image_sources)
  if [ $? -ne 0 ]; then
    exit 1
  fi
else
  image_urls_json="[]"
fi

if [[ "$MODEL" == *"beta"* ]]; then
  # beta model: no quality, no resolution
  BODY=$(jq -n \
    --arg model "$MODEL" \
    --arg prompt "$PROMPT" \
    --arg size "$SIZE" \
    --argjson n "$N" \
    --argjson image_urls "$image_urls_json" \
    '{
      model: $model,
      prompt: $prompt,
      size: $size,
      n: $n,
      image_urls: $image_urls
    }')
  echo "Creating image generation task..."
  echo "  Model: $MODEL"
  echo "  Prompt: $PROMPT"
  echo "  Size: $SIZE"
  echo "  Count: $N"
else
  BODY=$(jq -n \
    --arg model "$MODEL" \
    --arg prompt "$PROMPT" \
    --arg size "$SIZE" \
    --arg resolution "$RESOLUTION" \
    --argjson n "$N" \
    --arg quality "$QUALITY" \
    --argjson image_urls "$image_urls_json" \
    '{
      model: $model,
      prompt: $prompt,
      size: $size,
      resolution: $resolution,
      n: $n,
      quality: $quality,
      image_urls: $image_urls
    }')
  echo "Creating image generation task..."
  echo "  Model: $MODEL"
  echo "  Prompt: $PROMPT"
  echo "  Size: $SIZE"
  echo "  Resolution: $RESOLUTION"
  echo "  Count: $N"
  echo "  Quality: $QUALITY"
fi

# Create task
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${BASE_URL}/v1/images/generations" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_KEY}" \
  -d "$BODY")

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
RESP_BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" != "200" ] && [ "$HTTP_CODE" != "201" ]; then
  echo "Error: API request failed with HTTP $HTTP_CODE"
  echo "$RESP_BODY" | jq . 2>/dev/null || echo "$RESP_BODY"
  exit 1
fi

TASK_ID=$(echo "$RESP_BODY" | jq -r '.id // empty')
if [ -z "$TASK_ID" ]; then
  echo "Error: Failed to get task ID from response"
  echo "$RESP_BODY"
  exit 1
fi

echo "Task created: $TASK_ID"
echo "Polling for completion (interval: 5s)..."

# Poll task status
while true; do
  sleep 5

  TASK_RESP=$(curl -s -w "\n%{http_code}" -X GET "${BASE_URL}/v1/tasks/${TASK_ID}" \
    -H "Authorization: Bearer ${API_KEY}")

  TASK_HTTP=$(echo "$TASK_RESP" | tail -1)
  TASK_BODY=$(echo "$TASK_RESP" | sed '$d')

  if [ "$TASK_HTTP" != "200" ]; then
    echo "Error: Task query failed with HTTP $TASK_HTTP"
    echo "$TASK_BODY" | jq . 2>/dev/null || echo "$TASK_BODY"
    exit 1
  fi

  STATUS=$(echo "$TASK_BODY" | jq -r '.status // "unknown"')
  PROGRESS=$(echo "$TASK_BODY" | jq -r '.progress // 0')

  if [ "$STATUS" = "completed" ]; then
    echo "Task completed!"

    IMAGE_COUNT=$(echo "$TASK_BODY" | jq '.result_data | length')
    echo "Generated $IMAGE_COUNT image(s):"

    for i in $(seq 0 $((IMAGE_COUNT - 1))); do
      IMG_URL=$(echo "$TASK_BODY" | jq -r ".result_data[$i].url")
      INDEX=$((i + 1))
      echo "  [$INDEX] $IMG_URL"

      if [ "$DOWNLOAD" = true ]; then
        if [ "$IMAGE_COUNT" -eq 1 ]; then
          OUT_FILE="$OUTPUT"
        else
          EXT="${OUTPUT##*.}"
          BASE="${OUTPUT%.*}"
          OUT_FILE="${BASE}_${INDEX}.${EXT}"
        fi
        echo "  Downloading to $OUT_FILE..."

        # Download to temp file first to detect compression
        TMP_FILE="${OUT_FILE}.tmp"
        curl -s -L --max-time 120 -o "$TMP_FILE" "$IMG_URL"

        # Detect and decompress gzip if needed
        if file "$TMP_FILE" | grep -q "gzip compressed"; then
          echo "  Detected gzip compression, decompressing..."
          gzip -d -c "$TMP_FILE" > "$OUT_FILE"
          rm -f "$TMP_FILE"
        else
          mv "$TMP_FILE" "$OUT_FILE"
        fi

        echo "  Saved: $OUT_FILE ($(ls -lh "$OUT_FILE" | awk '{print $5}'))"
      fi
    done
    break

  elif [ "$STATUS" = "failed" ]; then
    ERROR_MSG=$(echo "$TASK_BODY" | jq -r '.error // "Unknown error"')
    echo "Task failed: $ERROR_MSG"
    exit 1
  fi

  echo "  Status: $STATUS, Progress: ${PROGRESS}%"
done
