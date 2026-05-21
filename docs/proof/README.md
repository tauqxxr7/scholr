# Scholr Production Proof

This folder contains real production evidence captured from the live Scholr deployment.

## Direct live page screenshots

- `desktop-home-live.png`
- `desktop-research-live.png`
- `mobile-notes-live.png`
- `mobile-documents-live.png`

These are direct screenshots of the live Vercel frontend.

## Live proof panels

- `live-stream-proof.png`
- `provider-proof.png`
- `document-proof.png`

These are generated from real production payloads captured by:
- `backend/scripts/capture_live_proof.py`

They are not mockups. They are screenshot panels built from:
- live SSE output
- live provider diagnostics
- live document upload and answer responses

## Raw capture

- `live-proof.json`

This JSON file is the raw production capture used to generate the proof panels.
