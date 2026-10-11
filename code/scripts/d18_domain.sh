#!/usr/bin/env bash
# Demo 18 starting state: governed tag + Discover domain "Revantage Workshop".
# Usage: code/scripts/d18_domain.sh <profile> [--teardown]
# Needs account/workspace admin (MANAGE DISCOVER). Afterwards, in the UI: Discover → Revantage Workshop →
# Publish; ⋮ → Manage Domains → Permissions → grant MANAGE on the domain to the participants' group
# (so they can create Pages); Add to domain: the ref_mv_* metric views and gold_property_quarterly.
# Not runnable on the FEVM account (governed-tag limit reached); run it in the Revantage workspace.
set -euo pipefail
P=${1:?profile}; TAG="Revantage Workshop"
if [[ "${2:-}" == "--teardown" ]]; then
  ID=$(databricks api get /api/2.0/domains -p "$P" | python3 -c "import json,sys; print(next((d['domain_id'] for d in json.load(sys.stdin).get('domains',[]) if d['tag_key']=='$TAG'),''))")
  [[ -n "$ID" ]] && databricks api delete "/api/2.0/domains/$ID" -p "$P" && echo "deleted domain $ID"
  databricks tag-policies delete-tag-policy "$TAG" -p "$P" && echo "deleted tag policy '$TAG'"
  exit 0
fi
databricks tag-policies create-tag-policy -p "$P" --json "{\"tag_key\":\"$TAG\",\"description\":\"Domain tag for the Revantage Luxembourg workshop (Demo 18). Delete after the workshop.\"}"
databricks api post /api/2.0/domains -p "$P" --json "{\"tag_key\":\"$TAG\",\"subtitle\":\"Property portfolio: P&L, leases, tenants\",\"description\":\"Revantage workshop domain: certified gold data, the governed metric views (net profit, target attainment, QoQ growth) and the business definitions (Pages) that Genie uses.\",\"icon\":{\"name\":\"CITY\",\"color\":\"#1B3139\"}}"
