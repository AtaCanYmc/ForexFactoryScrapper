#!/usr/bin/env bash
# scripts/curl_examples.sh
# Simple curl examples for ForexFactoryScrapper endpoints.
# Usage:
#   HOST=http://localhost:5000 ./scripts/curl_examples.sh
#   or
#   ./scripts/curl_examples.sh (defaults to http://localhost:5000)

set -euo pipefail

HOST="${HOST:-http://localhost:5000}"

# Helper: perform a GET request and show response + HTTP status
do_get() {
  local path="$1"
  echo
  echo "================================================================"
  echo "GET ${HOST}${path}"
  echo "----------------------------------------------------------------"
  # -sS : silent but show errors
  # -w prints HTTP status on a trailing line
  curl -sS "${HOST}${path}" -w "\nHTTP_STATUS:%{http_code}\n"
}

# Examples
# 1) hello
 do_get "/api/hello"

# 2) health
 do_get "/api/health"

# 3) forex daily — missing parameters
 do_get "/api/forex/daily"

# 4) forex daily — invalid (non-integer) parameters
 do_get "/api/forex/daily?day=aa&month=bb&year=cc"

# 5) forex daily — out of range
 do_get "/api/forex/daily?day=99&month=99&year=3000"

# 6) forex daily — success example
 # Change the date below if you want a different test date
 do_get "/api/forex/daily?day=1&month=1&year=2020"

# End
echo
echo "Done. To use a different host: HOST=http://0.0.0.0:5000 ./scripts/curl_examples.sh"
