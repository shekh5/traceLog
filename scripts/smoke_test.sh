#!/usr/bin/env bash
set -euo pipefail

patient_base_url="${1:-${PATIENT_BASE_URL:-}}"
dashboard_base_url="${2:-${DASHBOARD_BASE_URL:-}}"

if [[ -z "$patient_base_url" || -z "$dashboard_base_url" ]]; then
  echo "usage: smoke_test.sh PATIENT_BASE_URL DASHBOARD_BASE_URL" >&2
  exit 2
fi

patient_base_url="${patient_base_url%/}"
dashboard_base_url="${dashboard_base_url%/}"

curl --fail --silent --show-error --retry 5 --retry-all-errors \
  --max-time 20 "$patient_base_url/healthz" >/dev/null
curl --fail --silent --show-error --retry 5 --retry-all-errors \
  --max-time 20 "$dashboard_base_url/healthz" >/dev/null

echo "TraceLog smoke check passed: Patient and dashboard are healthy."
