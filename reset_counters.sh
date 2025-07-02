#!/bin/bash
echo "=== Resetting Hub Helper Analytics Counters ==="
echo

# Create data directory
echo "Creating data directory..."
sudo mkdir -p /app/data
sudo chown -R $USER:$USER /app/data

# Reset local analytics file
echo "Resetting local analytics..."
cat > /app/data/local_analytics.json << 'EOF'
{
  "github_count": 0,
  "dockerhub_count": 0
}
EOF

echo "✅ Local analytics reset successfully"

# Check current state
echo
echo "=== Current State ==="
echo "Local analytics:"
cat /app/data/local_analytics.json
echo

echo "Checking external API..."
curl -s "https://hub-backend.satrawi.cc/analytics/hub-helper" || echo "External API not accessible"

echo
echo "Checking Flask app endpoint..."
curl -s "http://localhost:5414/analytics/counters" || echo "Flask app not running or not accessible"

echo
echo "=== Reset Complete ==="
echo "✅ Local analytics have been reset to zero"
echo "⚠️  External API reset may need to be done manually"
echo "   The local file will serve as backup and the external API"
echo "   will start counting from its current state."
