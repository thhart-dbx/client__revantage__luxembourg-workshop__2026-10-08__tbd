#!/usr/bin/env bash
# Demo 11 failure fixture: a late GL batch from a Luxembourg system with European decimal commas
# ("1.850,75"). The amounts don't parse, so silver's amount_parsed expectation (FAIL UPDATE) stops the run.
#   scripts/d11_bad_batch.sh inject <profile> <catalog> <schema>   copy the file into the raw volume
#   scripts/d11_bad_batch.sh remove <profile> <catalog> <schema>   delete it again (then run a full refresh)
set -euo pipefail
action=$1 profile=$2 catalog=$3 schema=$4
dest="dbfs:/Volumes/$catalog/$schema/raw/gl_transactions_late_batch_lux.csv"
here="$(cd "$(dirname "$0")/.." && pwd)"
case "$action" in
  inject) databricks fs cp "$here/reference/d11_bad_batch/gl_transactions_late_batch_lux.csv" "$dest" -p "$profile" --overwrite ;;
  remove) databricks fs rm "$dest" -p "$profile" ;;
  *) echo "usage: $0 inject|remove <profile> <catalog> <schema>" >&2; exit 2 ;;
esac
databricks fs ls "dbfs:/Volumes/$catalog/$schema/raw/" -p "$profile"
