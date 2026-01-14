#!/bin/bash
# API Testing Examples - v1 Data Endpoints
# 
# Usage:
#   1. Start the server: python -m uvicorn app.main:app --port 8001
#   2. Run these curl commands to test the API
#

BASE_URL="http://localhost:8001"
API_BASE="$BASE_URL/api/v1"

echo "=========================================="
echo "Stock Debate Advisor - API Test Examples"
echo "=========================================="
echo ""
echo "Base URL: $BASE_URL"
echo "API Prefix: $API_BASE"
echo ""

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

echo -e "${BLUE}=== UTILITY ENDPOINTS ===${NC}"
echo ""

echo -e "${GREEN}1. Health Check${NC}"
echo "curl $BASE_URL/health"
echo ""

echo -e "${GREEN}2. List All Stocks${NC}"
echo "curl $API_BASE/stocks/list | jq '.stocks[] | {symbol, name, sector}' | head -20"
echo ""

echo -e "${GREEN}3. Search Stocks (by name)${NC}"
echo "curl '$API_BASE/stocks/search?query=Bank' | jq"
echo ""

echo -e "${GREEN}4. Search Stocks (by symbol)${NC}"
echo "curl '$API_BASE/stocks/search?query=MB' | jq"
echo ""

# ============================================================================
# COMPANY INFO ENDPOINTS
# ============================================================================

echo -e "${BLUE}=== COMPANY INFO ===${NC}"
echo ""

echo -e "${GREEN}5. Get Company Info (ACB)${NC}"
echo "curl $API_BASE/company/ACB | jq"
echo ""

echo -e "${GREEN}6. Get Company Info (MBB.VN format)${NC}"
echo "curl $API_BASE/company/MBB.VN | jq '.data.info'"
echo ""

echo -e "${GREEN}7. Get Multiple Company Infos${NC}"
echo "for symbol in ACB MBB FPT VCB; do"
echo "  curl -s $API_BASE/company/\$symbol | jq '.data.info.name'"
echo "done"
echo ""

# ============================================================================
# FINANCIAL REPORTS ENDPOINTS
# ============================================================================

echo -e "${BLUE}=== FINANCIAL REPORTS ===${NC}"
echo ""

echo -e "${GREEN}8. Get All Financial Reports${NC}"
echo "curl $API_BASE/financials/ACB | jq '.data | {symbol, quarterly: .quarterly|keys, annual: .annual|keys}'"
echo ""

echo -e "${GREEN}9. Get Quarterly Reports (Latest 8)${NC}"
echo "curl $API_BASE/financials/quarterly/ACB | jq '.data.periods'"
echo ""

echo -e "${GREEN}10. Get Quarterly Reports (Latest 4)${NC}"
echo "curl '$API_BASE/financials/quarterly/MBB?limit=4' | jq '.data.periods'"
echo ""

echo -e "${GREEN}11. Get Annual Reports${NC}"
echo "curl $API_BASE/financials/annual/FPT | jq '.data.periods | keys'"
echo ""

echo -e "${GREEN}12. Get Latest Quarterly Earnings${NC}"
echo "curl '$API_BASE/financials/quarterly/ACB?limit=1' | jq '.data.periods[].revenue'"
echo ""

echo -e "${GREEN}13. Get Financial Metrics${NC}"
echo "curl $API_BASE/financials/metrics/VCB | jq '.data.metrics'"
echo ""

# ============================================================================
# DIVIDEND & SPLIT ENDPOINTS
# ============================================================================

echo -e "${BLUE}=== DIVIDENDS & SPLITS ===${NC}"
echo ""

echo -e "${GREEN}14. Get Dividend History${NC}"
echo "curl $API_BASE/dividends/ACB | jq '.data.dividends'"
echo ""

echo -e "${GREEN}15. Get Stock Split History${NC}"
echo "curl $API_BASE/splits/MBB | jq '.data.splits'"
echo ""

# ============================================================================
# PRICE DATA ENDPOINTS
# ============================================================================

echo -e "${BLUE}=== PRICE DATA ===${NC}"
echo ""

echo -e "${GREEN}16. Get All Price Data (249 days)${NC}"
echo "curl $API_BASE/prices/ACB | jq '.data | {symbol, interval, count: .price_count}'"
echo ""

echo -e "${GREEN}17. Get Recent Prices (Last 30 days)${NC}"
echo "curl '$API_BASE/prices/MBB?limit=30' | jq '.data.prices | .[0:3]'"
echo ""

echo -e "${GREEN}18. Get Latest Price${NC}"
echo "curl '$API_BASE/prices/FPT?limit=1' | jq '.data.prices[0]'"
echo ""

echo -e "${GREEN}19. Get Price Changes${NC}"
echo "curl '$API_BASE/prices/CTG?limit=10' | jq '.data.prices[] | {date, open, close, change_percent}'"
echo ""

# ============================================================================
# NEWS ENDPOINTS
# ============================================================================

echo -e "${BLUE}=== NEWS ===${NC}"
echo ""

echo -e "${GREEN}20. Get News (Available for MBB)${NC}"
echo "curl $API_BASE/news/MBB | jq '.data.news'"
echo ""

echo -e "${GREEN}21. News Not Available (Other Stocks)${NC}"
echo "curl $API_BASE/news/ACB 2>&1 | jq '.detail'"
echo ""

# ============================================================================
# COMBINED DATA ENDPOINTS
# ============================================================================

echo -e "${BLUE}=== COMBINED DATA ===${NC}"
echo ""

echo -e "${GREEN}22. Get Full Stock Data${NC}"
echo "curl $API_BASE/stock/ACB/full | jq '.symbol, .company_info.info | {name, sector, market_cap}'"
echo ""

echo -e "${GREEN}23. Save Full Stock Report to File${NC}"
echo "curl $API_BASE/stock/MBB/full > mbb_stock_report.json"
echo ""

# ============================================================================
# ADVANCED EXAMPLES
# ============================================================================

echo -e "${BLUE}=== ADVANCED EXAMPLES ===${NC}"
echo ""

echo -e "${GREEN}24. Compare Multiple Stocks' Metrics${NC}"
echo "for symbol in ACB MBB FPT; do"
echo "  echo \"\$symbol:\""
echo "  curl -s \$API_BASE/financials/metrics/\$symbol | jq '.data.metrics | {PE_ratio, dividend_yield}'"
echo "done"
echo ""

echo -e "${GREEN}25. Find Dividend Payers${NC}"
echo "for symbol in ACB MBB VCB; do"
echo "  count=\$(curl -s \$API_BASE/dividends/\$symbol | jq '.data.dividend_count')"
echo "  echo \"\$symbol: \$count dividends\""
echo "done"
echo ""

echo -e "${GREEN}26. Get Top Performing Stocks (by latest close price)${NC}"
echo "curl -s \$API_BASE/stocks/list | jq '.stocks | sort_by(-.market_cap) | .[0:5] | .[] | {symbol, market_cap}'"
echo ""

echo -e "${GREEN}27. Track 5-Day Price Trend${NC}"
echo "curl -s '$API_BASE/prices/MBB?limit=5' | jq '.data.prices | reverse | .[] | \"\\(.date): \\(.close) (\\(.change_percent)%)\"'"
echo ""

echo -e "${GREEN}28. Export Stock Data to JSON File${NC}"
echo "curl $API_BASE/stock/VCB/full | jq . > vcb_complete_data.json"
echo ""

echo -e "${GREEN}29. Get Stock List as CSV${NC}"
echo "curl -s \$API_BASE/stocks/list | jq -r '.stocks[] | \"\\(.symbol),\\(.name),\\(.sector)\"' > stocks.csv"
echo ""

echo -e "${GREEN}30. Pretty Print Company Info${NC}"
echo "curl $API_BASE/company/FPT | jq '.data.info | @json \"\\n\" | @csv'"
echo ""

# ============================================================================
# PERFORMANCE TESTING
# ============================================================================

echo -e "${BLUE}=== PERFORMANCE TESTING ===${NC}"
echo ""

echo -e "${GREEN}31. Measure Response Time${NC}"
echo "curl -w \"@- \" -o /dev/null -s \$API_BASE/company/ACB << 'EOF'"
echo "    time_namelookup:  %{time_namelookup}\\n"
echo "    time_connect:     %{time_connect}\\n"
echo "    time_appconnect:  %{time_appconnect}\\n"
echo "    time_pretransfer: %{time_pretransfer}\\n"
echo "    time_redirect:    %{time_redirect}\\n"
echo "    time_starttransfer: %{time_starttransfer}\\n"
echo "    ----------"
echo "    time_total:       %{time_total}\\n"
echo "EOF"
echo ""

echo -e "${GREEN}32. Concurrent Requests (Load Test)${NC}"
echo "seq 1 10 | xargs -I {} -P 5 curl -s \$API_BASE/prices/ACB > /dev/null"
echo "echo 'Completed 10 concurrent requests'"
echo ""

# ============================================================================
# DATA VALIDATION
# ============================================================================

echo -e "${BLUE}=== DATA VALIDATION ===${NC}"
echo ""

echo -e "${GREEN}33. Verify All 30 Stocks Exist${NC}"
echo "curl -s \$API_BASE/stocks/list | jq '.stocks | length' | grep -q 30 && echo 'OK: 30 stocks found' || echo 'ERROR: Not 30 stocks'"
echo ""

echo -e "${GREEN}34. Check Price Data Completeness${NC}"
echo "for symbol in ACB MBB FPT; do"
echo "  count=\$(curl -s \$API_BASE/prices/\$symbol | jq '.data.price_count')"
echo "  echo \"\$symbol has \$count price records\""
echo "done"
echo ""

echo -e "${GREEN}35. Verify Financial Data Present${NC}"
echo "curl -s \$API_BASE/financials/ACB | jq 'has(\"data\") and .data | has(\"quarterly\") and has(\"annual\") and has(\"metrics\")' | grep -q true && echo 'OK: Complete financial data' || echo 'ERROR: Missing sections'"
echo ""

# ============================================================================
# ERROR HANDLING
# ============================================================================

echo -e "${BLUE}=== ERROR HANDLING ===${NC}"
echo ""

echo -e "${GREEN}36. Test Invalid Symbol (404)${NC}"
echo "curl $API_BASE/company/INVALID"
echo ""

echo -e "${GREEN}37. Test Missing Query Parameter (400)${NC}"
echo "curl '$API_BASE/stocks/search?query='"
echo ""

echo -e "${GREEN}38. Test Invalid Limit Parameter${NC}"
echo "curl '$API_BASE/prices/ACB?limit=1000'"
echo ""

# ============================================================================
# PRACTICAL WORKFLOWS
# ============================================================================

echo -e "${BLUE}=== PRACTICAL WORKFLOWS ===${NC}"
echo ""

echo -e "${GREEN}39. Daily Watchlist Update${NC}"
echo "STOCKS=(ACB MBB FPT VCB TCB)"
echo "for symbol in \${STOCKS[@]}; do"
echo "  data=\$(curl -s '$API_BASE/prices/\$symbol?limit=1' | jq '.data.prices[0]')"
echo "  date=\$(echo \$data | jq -r '.date')"
echo "  close=\$(echo \$data | jq -r '.close')"
echo "  change=\$(echo \$data | jq -r '.change_percent')"
echo "  echo \"\$symbol (\$date): \$close (\$change%)\""
echo "done"
echo ""

echo -e "${GREEN}40. Investment Research Workflow${NC}"
echo "SYMBOL=MBB"
echo "echo 'Company: '\$(curl -s \$API_BASE/company/\$SYMBOL | jq -r '.data.info.name')"
echo "echo 'Metrics: '\$(curl -s \$API_BASE/financials/metrics/\$SYMBOL | jq '.data.metrics | {PE_ratio, ROE, dividend_yield}')"
echo "echo 'Latest Quarterly: '\$(curl -s \$API_BASE/financials/quarterly/\$SYMBOL | jq '.data.periods | keys | .[0]')"
echo "echo 'Recent Price: '\$(curl -s \$API_BASE/prices/\$SYMBOL?limit=1 | jq '.data.prices[0].close')"
echo ""

echo "=========================================="
echo "For full API documentation, see:"
echo "  - API_ENDPOINTS_V3.md"
echo "  - API_QUICK_REFERENCE.md"
echo "=========================================="
