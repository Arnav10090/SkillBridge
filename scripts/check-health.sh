#!/usr/bin/env bash
# =============================================================================
# scripts/check-health.sh
# SkillBridge — Backend Health Check Script
#
# Usage:
#   BACKEND_URL=https://your-service.onrender.com bash scripts/check-health.sh
#   # or export BACKEND_URL first, then:
#   bash scripts/check-health.sh
#
# Exit codes:
#   0  — backend is healthy (HTTP 200, status == "ok")
#   1  — backend returned non-200 or unexpected body
#   2  — connection error / timeout
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
HEALTH_ENDPOINT="${BACKEND_URL}/api/health"
TIMEOUT_SECONDS=15

# ---------------------------------------------------------------------------
# Helper colours
# ---------------------------------------------------------------------------
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'   # No Colour

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  SkillBridge — Backend Health Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Endpoint : ${HEALTH_ENDPOINT}"
echo "  Timeout  : ${TIMEOUT_SECONDS}s"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ---------------------------------------------------------------------------
# Send request
# ---------------------------------------------------------------------------
HTTP_RESPONSE=$(
  curl \
    --silent \
    --max-time "${TIMEOUT_SECONDS}" \
    --write-out "\n%{http_code}" \
    --request GET \
    "${HEALTH_ENDPOINT}" \
  2>/dev/null
) || {
  echo -e "${RED}✗ Connection failed.${NC}"
  echo "  Could not reach: ${HEALTH_ENDPOINT}"
  echo "  Check that BACKEND_URL is correct and the service is deployed."
  exit 2
}

# Split body and HTTP status code (last line)
HTTP_BODY=$(echo "${HTTP_RESPONSE}" | head -n -1)
HTTP_CODE=$(echo "${HTTP_RESPONSE}" | tail -n 1)

echo "  HTTP Status : ${HTTP_CODE}"
echo "  Response    : ${HTTP_BODY}"
echo ""

# ---------------------------------------------------------------------------
# Evaluate result
# ---------------------------------------------------------------------------
if [ "${HTTP_CODE}" -ne 200 ]; then
  echo -e "${RED}✗ UNHEALTHY — expected HTTP 200, got ${HTTP_CODE}${NC}"
  exit 1
fi

# Optionally validate the JSON body contains "status":"ok"
if echo "${HTTP_BODY}" | grep -q '"status".*"ok"'; then
  echo -e "${GREEN}✓ HEALTHY — backend is awake and responding correctly.${NC}"
  exit 0
else
  echo -e "${YELLOW}⚠ WARNING — HTTP 200 but response body does not contain status:ok${NC}"
  echo "  Raw body: ${HTTP_BODY}"
  exit 1
fi
