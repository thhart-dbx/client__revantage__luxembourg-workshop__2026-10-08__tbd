#!/usr/bin/env bash
# Demo 13: AI Gateway & Monitoring
# Enable AI Gateway usage tracking on a pay-per-token Claude endpoint
# Saves the endpoint's original config, then enables usage tracking, the inference table,
# and optional rate limits.
#   apply:    [BUNDLE_TARGET=revantage DATABRICKS_CONFIG_PROFILE=<p>] code/ai-gateway/apply_ai_gateway.sh
#   teardown: code/ai-gateway/apply_ai_gateway.sh --teardown (restores the saved original config)
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE/.."

# Extract catalog and schema from bundle config
TARGET="${BUNDLE_TARGET:-dev}"
VARS=$(databricks bundle validate -t "$TARGET" -o json 2>/dev/null | python3 -c 'import sys,json; v=json.load(sys.stdin)["variables"]; print(v["catalog"]["value"], v["schema"]["value"])')
read -r CATALOG SCHEMA <<<"$VARS"

PROFILE="${DATABRICKS_CONFIG_PROFILE:-fevm-thhart-october-2026}"
ENDPOINT="${AI_GATEWAY_ENDPOINT:-databricks-claude-sonnet-4-6}"
ORIGINAL="$HERE/original_ai_gateway_${ENDPOINT}.json"

if [[ "${1:-}" == "--teardown" ]]; then
  if [[ -f "$ORIGINAL" ]]; then
    databricks serving-endpoints put-ai-gateway "$ENDPOINT" --json @"$ORIGINAL" -p "$PROFILE" >/dev/null
    echo "Restored original AI Gateway config on $ENDPOINT"
  else
    echo "No original config saved for $ENDPOINT; skipping restoration"
  fi
  exit 0
fi

# Save the original config if it doesn't exist
if [[ ! -f "$ORIGINAL" ]]; then
  databricks serving-endpoints get "$ENDPOINT" -p "$PROFILE" -o json 2>/dev/null \
    | python3 -c 'import sys,json; print(json.dumps(json.load(sys.stdin).get("ai_gateway") or {}))' > "$ORIGINAL"
  echo "Saved original AI Gateway config to $ORIGINAL"
fi

# Apply the AI Gateway config with usage tracking
echo "Enabling AI Gateway usage tracking on $ENDPOINT..."
databricks serving-endpoints put-ai-gateway "$ENDPOINT" -p "$PROFILE" --json "{
  \"usage_tracking_config\": {\"enabled\": true},
  \"inference_table_config\": {\"enabled\": true, \"catalog_name\": \"$CATALOG\", \"schema_name\": \"$SCHEMA\", \"table_name_prefix\": \"ref_d13\"}
}" -o json | python3 -c 'import sys,json; print(json.dumps(json.load(sys.stdin), indent=2))'

echo "AI Gateway enabled with inference table: $CATALOG.$SCHEMA.ref_d13_*"
echo "Note: Usage may take 1-2 hours to appear in system.ai_gateway tables"
