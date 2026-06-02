#!/bin/bash
set -e

if [ -z "$GITHUB_TOKEN" ]; then
  echo "Set GITHUB_TOKEN before running this script."
  exit 1
fi

REPO="tauqxxr7/scholr"
DESCRIPTION="Free AI study tool for BTech students - research papers, notes, doubt solving, and PDF intelligence."
HOMEPAGE="https://scholr-coral.vercel.app"

curl -sS -X PATCH "https://api.github.com/repos/$REPO" \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -d "{\"description\":\"$DESCRIPTION\",\"homepage\":\"$HOMEPAGE\",\"has_projects\":true,\"has_wiki\":false}"

curl -sS -X PUT "https://api.github.com/repos/$REPO/topics" \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -d '{"names":["ai","edtech","fastapi","nextjs","btechstudents","india","gemini","openrouter","academic","studytool","researchassistant","machinelearning"]}'

echo "GitHub metadata updated for $REPO"
