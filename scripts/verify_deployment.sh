#!/usr/bin/env bash
# -------------------------------------------------------------------
# CaseMate Deployment Verification Script
#
# Validates that backend and frontend are deployed and responding.
# Usage: ./scripts/verify_deployment.sh [backend_url] [frontend_url]
# -------------------------------------------------------------------

set -euo pipefail

BACKEND_URL="${1:-https://api.casematelaw.com}"
FRONTEND_URL="${2:-https://casematelaw.com}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASS=0
FAIL=0

check() {
    local name="$1"
    local url="$2"
    local expected="$3"

    printf "  %-40s " "$name"

    response=$(curl -s -o /tmp/casemate_check.txt -w "%{http_code}" --max-time 10 "$url" 2>/dev/null || echo "000")

    if [ "$response" = "$expected" ]; then
        printf "${GREEN}PASS${NC} (HTTP %s)\n" "$response"
        PASS=$((PASS + 1))
    else
        printf "${RED}FAIL${NC} (HTTP %s, expected %s)\n" "$response" "$expected"
        FAIL=$((FAIL + 1))
    fi
}

check_json() {
    local name="$1"
    local url="$2"
    local json_key="$3"
    local expected_value="$4"

    printf "  %-40s " "$name"

    body=$(curl -s --max-time 10 "$url" 2>/dev/null || echo "{}")
    actual=$(echo "$body" | python3 -c "import sys,json; print(json.load(sys.stdin).get('$json_key',''))" 2>/dev/null || echo "")

    if [ "$actual" = "$expected_value" ]; then
        printf "${GREEN}PASS${NC} (%s=%s)\n" "$json_key" "$actual"
        PASS=$((PASS + 1))
    else
        printf "${RED}FAIL${NC} (%s=%s, expected %s)\n" "$json_key" "$actual" "$expected_value"
        FAIL=$((FAIL + 1))
    fi
}

echo ""
echo "======================================"
echo " CaseMate Deployment Verification"
echo "======================================"
echo ""

echo "Backend: $BACKEND_URL"
echo "Frontend: $FRONTEND_URL"
echo ""

echo "--- Backend Health ---"
check "GET /health returns 200"          "$BACKEND_URL/health"    "200"
check_json "Health status is 'ok'"       "$BACKEND_URL/health"    "status"  "ok"
check_json "Version is 0.4.0"           "$BACKEND_URL/health"    "version" "0.4.0"

echo ""
echo "--- Backend API ---"
check "GET /api/rights/domains returns 200"  "$BACKEND_URL/api/rights/domains"  "200"
check "GET /api/rights/guides returns 200"   "$BACKEND_URL/api/rights/guides"   "200"
check "GET /api/workflows/templates returns 200" "$BACKEND_URL/api/workflows/templates" "200"

echo ""
echo "--- Frontend ---"
check "Frontend root returns 200"        "$FRONTEND_URL"          "200"
check "Auth page returns 200"            "$FRONTEND_URL/auth"     "200"

echo ""
echo "--- Security Headers ---"
printf "  %-40s " "X-Content-Type-Options present"
headers=$(curl -s -I --max-time 10 "$BACKEND_URL/health" 2>/dev/null || echo "")
if echo "$headers" | grep -qi "x-content-type-options"; then
    printf "${GREEN}PASS${NC}\n"
    PASS=$((PASS + 1))
else
    printf "${RED}FAIL${NC}\n"
    FAIL=$((FAIL + 1))
fi

printf "  %-40s " "X-Frame-Options present"
if echo "$headers" | grep -qi "x-frame-options"; then
    printf "${GREEN}PASS${NC}\n"
    PASS=$((PASS + 1))
else
    printf "${RED}FAIL${NC}\n"
    FAIL=$((FAIL + 1))
fi

echo ""
echo "======================================"
printf "Results: ${GREEN}%d passed${NC}, ${RED}%d failed${NC}\n" "$PASS" "$FAIL"
echo "======================================"
echo ""

if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
