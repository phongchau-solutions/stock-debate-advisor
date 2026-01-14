#!/bin/bash
# Example event for testing Lambda functions locally

cat > /tmp/debate-event.json <<'EOF'
{
  "httpMethod": "POST",
  "body": "{\"symbol\": \"MBB\", \"question\": \"Is this a good stock to buy?\", \"userId\": \"user123\"}",
  "headers": {
    "Content-Type": "application/json"
  }
}
EOF

cat > /tmp/data-event.json <<'EOF'
{
  "httpMethod": "GET",
  "pathParameters": {
    "symbol": "MBB"
  },
  "headers": {
    "Content-Type": "application/json"
  }
}
EOF

echo "✓ Created test events in /tmp/"
echo ""
echo "Test debate lambda locally:"
echo "  sam local invoke DebateOrchestratorFunction -e /tmp/debate-event.json"
echo ""
echo "Test data lambda locally:"
echo "  sam local invoke DataLoaderFunction -e /tmp/data-event.json"
