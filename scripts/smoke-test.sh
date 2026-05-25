#!/bin/bash
set -e
BASE="${1:-https://scholr-k9sj.onrender.com}"
echo "Smoke testing $BASE"

check() {
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE$1")
  if [ "$STATUS" = "200" ]; then
    echo "✅ $1 → $STATUS"
  else
    echo "❌ $1 → $STATUS"
    FAILED=1
  fi
}

FAILED=0
check "/health"
check "/health/routes"
check "/api/metrics"
check "/api/history"
check "/api/search?q=machine+learning"
check "/api/evidence"

VERSION=$(curl -s "$BASE/health" | python3 -c "import sys,json; print(json.load(sys.stdin).get('version','unknown'))")
echo "Backend version: $VERSION"

if [ "$FAILED" = "1" ]; then
  echo "Some checks failed"
  exit 1
fi
echo "All checks passed"
