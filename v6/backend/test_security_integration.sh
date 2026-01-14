#!/bin/bash

# Backend API Security Integration Test Script
# Tests all secured endpoints with authentication and validation

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_URL="${API_URL:-http://localhost:8000}"
TEST_EMAIL="testuser@example.com"
TEST_PASSWORD="password123"
TIMEOUT=10

# Test results
PASSED=0
FAILED=0

# Functions
print_header() {
  echo -e "\n${BLUE}========================================${NC}"
  echo -e "${BLUE}$1${NC}"
  echo -e "${BLUE}========================================${NC}\n"
}

print_test() {
  echo -e "${YELLOW}Testing: $1${NC}"
}

print_pass() {
  echo -e "${GREEN}✓ PASS${NC}: $1"
  ((PASSED++))
}

print_fail() {
  echo -e "${RED}✗ FAIL${NC}: $1"
  ((FAILED++))
}

print_summary() {
  echo -e "\n${BLUE}========================================${NC}"
  echo -e "${BLUE}Test Summary${NC}"
  echo -e "${BLUE}========================================${NC}"
  echo -e "Passed: ${GREEN}$PASSED${NC}"
  echo -e "Failed: ${RED}$FAILED${NC}"
  echo -e "Total:  $((PASSED + FAILED))"
  echo ""
}

# Test: Backend Health
test_health() {
  print_test "Backend Health"
  
  RESPONSE=$(curl -s -w "\n%{http_code}" "$API_URL/health")
  HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
  
  if [ "$HTTP_CODE" = "200" ]; then
    print_pass "Backend is running"
  else
    print_fail "Backend health check failed (HTTP $HTTP_CODE)"
  fi
}

# Test: Login (Create JWT Token)
test_login() {
  print_test "User Login"
  
  RESPONSE=$(curl -s -X POST "$API_URL/api/v1/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"email\": \"$TEST_EMAIL\", \"password\": \"$TEST_PASSWORD\"}" \
    -w "\n%{http_code}")
  
  HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
  BODY=$(echo "$RESPONSE" | sed '$d')
  
  if [ "$HTTP_CODE" = "200" ]; then
    TOKEN=$(echo "$BODY" | jq -r '.data.token' 2>/dev/null)
    if [ ! -z "$TOKEN" ] && [ "$TOKEN" != "null" ]; then
      echo "TOKEN=$TOKEN" > /tmp/token.sh
      print_pass "User login successful"
    else
      print_fail "Login returned invalid token"
    fi
  else
    print_fail "Login failed (HTTP $HTTP_CODE)"
  fi
}

# Test: Verify Token
test_verify_token() {
  print_test "Token Verification"
  
  source /tmp/token.sh 2>/dev/null || { print_fail "No token available"; return; }
  
  HTTP_CODE=$(curl -s -w "%{http_code}" -o /dev/null \
    -H "Authorization: Bearer $TOKEN" \
    "$API_URL/api/v1/auth/verify")
  
  if [ "$HTTP_CODE" = "200" ]; then
    print_pass "Token verification successful"
  else
    print_fail "Token verification failed (HTTP $HTTP_CODE)"
  fi
}

# Test: Invalid Token
test_invalid_token() {
  print_test "Invalid Token Handling"
  
  HTTP_CODE=$(curl -s -w "%{http_code}" -o /dev/null \
    -H "Authorization: Bearer invalid_token_here" \
    "$API_URL/api/v1/companies/ACB")
  
  if [ "$HTTP_CODE" = "403" ]; then
    print_pass "Invalid token correctly rejected"
  else
    print_fail "Invalid token not rejected properly (HTTP $HTTP_CODE)"
  fi
}

# Test: Missing Authentication Header
test_missing_auth() {
  print_test "Missing Authentication Header"
  
  HTTP_CODE=$(curl -s -w "%{http_code}" -o /dev/null \
    "$API_URL/api/v1/companies/ACB")
  
  # Should still work - optional authentication
  if [ "$HTTP_CODE" = "200" ]; then
    print_pass "Request works without authentication (optional auth)"
  else
    print_fail "Request failed without authentication (HTTP $HTTP_CODE)"
  fi
}

# Test: Get Company Info
test_get_company() {
  print_test "Get Company Information"
  
  source /tmp/token.sh 2>/dev/null
  
  RESPONSE=$(curl -s -w "\n%{http_code}" \
    -H "Authorization: Bearer $TOKEN" \
    "$API_URL/api/v1/companies/ACB")
  
  HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
  BODY=$(echo "$RESPONSE" | sed '$d')
  
  if [ "$HTTP_CODE" = "200" ]; then
    SUCCESS=$(echo "$BODY" | jq -r '.success' 2>/dev/null)
    if [ "$SUCCESS" = "true" ]; then
      print_pass "Company data retrieved successfully"
    else
      print_fail "Company data request returned success=false"
    fi
  else
    print_fail "Get company failed (HTTP $HTTP_CODE)"
  fi
}

# Test: Invalid Symbol
test_invalid_symbol() {
  print_test "Invalid Symbol Validation"
  
  source /tmp/token.sh 2>/dev/null
  
  HTTP_CODE=$(curl -s -w "%{http_code}" -o /dev/null \
    -H "Authorization: Bearer $TOKEN" \
    "$API_URL/api/v1/companies/INVALID_SYMBOL_HERE")
  
  if [ "$HTTP_CODE" = "400" ]; then
    print_pass "Invalid symbol correctly rejected (HTTP 400)"
  else
    print_fail "Invalid symbol not validated (HTTP $HTTP_CODE)"
  fi
}

# Test: Valid Symbol Variations
test_symbol_variations() {
  print_test "Stock Symbol Variations"
  
  source /tmp/token.sh 2>/dev/null
  
  # Test ACB (short form)
  HTTP1=$(curl -s -w "%{http_code}" -o /dev/null \
    -H "Authorization: Bearer $TOKEN" \
    "$API_URL/api/v1/companies/ACB")
  
  # Test ACB.VN (full form)
  HTTP2=$(curl -s -w "%{http_code}" -o /dev/null \
    -H "Authorization: Bearer $TOKEN" \
    "$API_URL/api/v1/companies/ACB.VN")
  
  if [ "$HTTP1" = "200" ] && [ "$HTTP2" = "200" ]; then
    print_pass "Both symbol formats accepted (ACB and ACB.VN)"
  else
    print_fail "Symbol format handling failed (HTTP $HTTP1, $HTTP2)"
  fi
}

# Test: Get Multiple Companies
test_multiple_companies() {
  print_test "Get Multiple Companies"
  
  source /tmp/token.sh 2>/dev/null
  
  RESPONSE=$(curl -s -w "\n%{http_code}" \
    -H "Authorization: Bearer $TOKEN" \
    "$API_URL/api/v1/companies?symbols=ACB,MBB,VCB")
  
  HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
  
  if [ "$HTTP_CODE" = "200" ]; then
    print_pass "Multiple companies retrieved successfully"
  else
    print_fail "Get multiple companies failed (HTTP $HTTP_CODE)"
  fi
}

# Test: Search Companies
test_search() {
  print_test "Search Companies"
  
  source /tmp/token.sh 2>/dev/null
  
  RESPONSE=$(curl -s -w "\n%{http_code}" \
    -H "Authorization: Bearer $TOKEN" \
    "$API_URL/api/v1/companies/search/query?query=Bank&limit=5")
  
  HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
  
  if [ "$HTTP_CODE" = "200" ]; then
    print_pass "Company search successful"
  else
    print_fail "Company search failed (HTTP $HTTP_CODE)"
  fi
}

# Test: Invalid Search Query
test_invalid_search() {
  print_test "Invalid Search Query Validation"
  
  source /tmp/token.sh 2>/dev/null
  
  # Query too short (< 2 chars)
  HTTP_CODE=$(curl -s -w "%{http_code}" -o /dev/null \
    -H "Authorization: Bearer $TOKEN" \
    "$API_URL/api/v1/companies/search/query?query=A")
  
  if [ "$HTTP_CODE" = "400" ]; then
    print_pass "Short query correctly rejected"
  else
    print_fail "Short query validation failed (HTTP $HTTP_CODE)"
  fi
}

# Test: Get Financials
test_get_financials() {
  print_test "Get Financial Data"
  
  source /tmp/token.sh 2>/dev/null
  
  RESPONSE=$(curl -s -w "\n%{http_code}" \
    -H "Authorization: Bearer $TOKEN" \
    "$API_URL/api/v1/financials/ACB")
  
  HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
  
  if [ "$HTTP_CODE" = "200" ]; then
    print_pass "Financial data retrieved successfully"
  else
    print_fail "Get financials failed (HTTP $HTTP_CODE)"
  fi
}

# Test: Get Quarterly Reports
test_quarterly_reports() {
  print_test "Get Quarterly Reports"
  
  source /tmp/token.sh 2>/dev/null
  
  RESPONSE=$(curl -s -w "\n%{http_code}" \
    -H "Authorization: Bearer $TOKEN" \
    "$API_URL/api/v1/financials/ACB/quarterly?limit=4")
  
  HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
  
  if [ "$HTTP_CODE" = "200" ]; then
    print_pass "Quarterly reports retrieved successfully"
  else
    print_fail "Get quarterly reports failed (HTTP $HTTP_CODE)"
  fi
}

# Test: Get Prices
test_get_prices() {
  print_test "Get OHLC Prices"
  
  source /tmp/token.sh 2>/dev/null
  
  RESPONSE=$(curl -s -w "\n%{http_code}" \
    -H "Authorization: Bearer $TOKEN" \
    "$API_URL/api/v1/financials/ACB/prices?limit=10")
  
  HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
  
  if [ "$HTTP_CODE" = "200" ]; then
    print_pass "Price data retrieved successfully"
  else
    print_fail "Get prices failed (HTTP $HTTP_CODE)"
  fi
}

# Test: Invalid Limit
test_invalid_limit() {
  print_test "Invalid Limit Validation"
  
  source /tmp/token.sh 2>/dev/null
  
  # Limit > 100
  HTTP_CODE=$(curl -s -w "%{http_code}" -o /dev/null \
    -H "Authorization: Bearer $TOKEN" \
    "$API_URL/api/v1/financials/ACB/prices?limit=999")
  
  if [ "$HTTP_CODE" = "400" ]; then
    print_pass "Excessive limit correctly rejected"
  else
    print_fail "Limit validation failed (HTTP $HTTP_CODE)"
  fi
}

# Test: Get List of All Stocks
test_list_all() {
  print_test "List All Stocks"
  
  source /tmp/token.sh 2>/dev/null
  
  RESPONSE=$(curl -s -w "\n%{http_code}" \
    -H "Authorization: Bearer $TOKEN" \
    "$API_URL/api/v1/companies/list/all")
  
  HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
  BODY=$(echo "$RESPONSE" | sed '$d')
  
  if [ "$HTTP_CODE" = "200" ]; then
    COUNT=$(echo "$BODY" | jq '.data | length' 2>/dev/null)
    if [ "$COUNT" -ge 30 ]; then
      print_pass "All 30+ stocks retrieved successfully"
    else
      print_fail "Stock list incomplete (only $COUNT stocks)"
    fi
  else
    print_fail "List all stocks failed (HTTP $HTTP_CODE)"
  fi
}

# Test: Rate Limit Headers
test_rate_limit_headers() {
  print_test "Rate Limit Response Headers"
  
  source /tmp/token.sh 2>/dev/null
  
  RESPONSE=$(curl -s -i -H "Authorization: Bearer $TOKEN" \
    "$API_URL/api/v1/companies/ACB" 2>&1)
  
  if echo "$RESPONSE" | grep -q "X-RateLimit-Limit"; then
    print_pass "Rate limit headers present"
  else
    print_fail "Rate limit headers missing"
  fi
}

# Test: CORS Headers
test_cors_headers() {
  print_test "CORS Headers Configuration"
  
  RESPONSE=$(curl -s -i -X OPTIONS \
    -H "Origin: http://localhost:3000" \
    -H "Access-Control-Request-Method: GET" \
    "$API_URL/api/v1/companies/ACB" 2>&1)
  
  if echo "$RESPONSE" | grep -q "Access-Control-Allow-Origin"; then
    print_pass "CORS headers configured"
  else
    print_fail "CORS headers missing"
  fi
}

# Test: Register New User
test_register() {
  print_test "User Registration"
  
  UNIQUE_EMAIL="testuser$(date +%s)@example.com"
  
  RESPONSE=$(curl -s -X POST "$API_URL/api/v1/auth/register" \
    -H "Content-Type: application/json" \
    -d "{\"email\": \"$UNIQUE_EMAIL\", \"password\": \"password123\", \"name\": \"Test User\"}" \
    -w "\n%{http_code}")
  
  HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
  
  if [ "$HTTP_CODE" = "201" ]; then
    print_pass "User registration successful"
  else
    print_fail "User registration failed (HTTP $HTTP_CODE)"
  fi
}

# Main test execution
main() {
  print_header "Backend API Security Integration Tests"
  echo "API URL: $API_URL"
  echo "Test Email: $TEST_EMAIL"
  echo ""
  
  # Health Check
  test_health
  
  # Authentication Tests
  print_header "Authentication Tests"
  test_login
  test_verify_token
  test_invalid_token
  test_register
  
  # Data Access Tests
  print_header "Data Access Tests"
  test_missing_auth
  test_get_company
  test_multiple_companies
  test_symbol_variations
  test_get_financials
  test_quarterly_reports
  test_get_prices
  test_list_all
  
  # Validation Tests
  print_header "Input Validation Tests"
  test_invalid_symbol
  test_invalid_search
  test_search
  test_invalid_limit
  
  # Security Headers Tests
  print_header "Security Headers Tests"
  test_rate_limit_headers
  test_cors_headers
  
  # Summary
  print_summary
  
  # Exit with appropriate code
  if [ $FAILED -eq 0 ]; then
    exit 0
  else
    exit 1
  fi
}

# Run tests
main
