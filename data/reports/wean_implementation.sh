#!/bin/bash

# WEAN_LOCAL_PCT Implementation Script
# Generated: 2025-11-06
# Recommended Setting: 85%

echo "🎯 WEAN_LOCAL_PCT Implementation"
echo "================================"

# Current setting
CURRENT_PCT=$(grep WEAN_LOCAL_PCT .env.local | cut -d'=' -f2)
echo "Current WEAN_LOCAL_PCT: $CURRENT_PCT"

# Recommended setting
RECOMMENDED_PCT=85
echo "Recommended WEAN_LOCAL_PCT: $RECOMMENDED_PCT"

# Backup current config
echo "📋 Creating backup..."
cp .env.local .env.local.backup.$(date +%Y%m%d_%H%M%S)

# Apply new setting
echo "⚙️ Applying new setting..."
sed -i "s/WEAN_LOCAL_PCT=$CURRENT_PCT/WEAN_LOCAL_PCT=$RECOMMENDED_PCT/" .env.local

# Verify change
NEW_PCT=$(grep WEAN_LOCAL_PCT .env.local | cut -d'=' -f2)
echo "✅ Updated WEAN_LOCAL_PCT: $NEW_PCT"

echo ""
echo "🚀 Makefile-safe export line:"
echo "export WEAN_LOCAL_PCT=$RECOMMENDED_PCT"

echo ""
echo "🛡️ Rollback Commands:"
echo "# Quick rollback to previous setting"
echo "export WEAN_LOCAL_PCT=$CURRENT_PCT"
echo "sed -i 's/WEAN_LOCAL_PCT=$RECOMMENDED_PCT/WEAN_LOCAL_PCT=$CURRENT_PCT/' .env.local"

echo ""
echo "# Emergency rollback to safe default"
echo "export WEAN_LOCAL_PCT=40"
echo "sed -i 's/WEAN_LOCAL_PCT=[0-9]*/WEAN_LOCAL_PCT=40/' .env.local"

echo ""
echo "📊 Monitoring Commands:"
echo "# Real-time success rate"
echo "watch -n 30 'awk -F, \"NR>1 {tot++; if(\$7==1) ok++} END {printf \\\"Success: %.1f%% (%d/%d)\\\\n\\\", ok/tot*100, ok, tot}' logs/wean.csv\""

echo ""
echo "# Provider performance"
echo "tail -20 logs/wean.csv | awk -F, '{sum[\$3]+=\$6; cnt[\$3]++; if(\$7==1) ok[\$3]++} END {for(p in sum) printf \"%s: %.1fms, %.0f%% success (%d reqs)\\\\n\", p, sum[p]/cnt[p], ok[p]/cnt[p]*100, cnt[p]}'"

echo ""
echo "🎯 Implementation complete! Monitor system performance for the next 72 hours."