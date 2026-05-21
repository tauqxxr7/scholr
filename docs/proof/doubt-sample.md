# Scholr Live Doubt Sample

Captured from the live production backend on 2026-05-21.

## Runtime proof

- Route: `POST /api/doubt`
- Question: `What is normalization in DBMS?`
- Subject: `DBMS`
- Active provider: `openrouter`
- Selected model: `google/gemini-2.0-flash-lite-001`
- Fallback scaffold detected: `No`
- First token latency: `6239 ms`
- Full completion latency: `6390 ms`
- Stream completion integrity: `[DONE] received`

## Real streamed output excerpt

```md
Okay, here's an explanation of normalization in DBMS:

## Simple Answer

Normalization is the process of organizing data in a database to reduce redundancy and improve data integrity.

## Why do we use it?

- To avoid storing the same data in multiple places
- To make updates safer and more consistent
- To reduce insertion, update, and deletion anomalies
```

## Why this matters

This sample proves that live Doubt generation is returning concise academic reasoning through the real AI path, with normal markdown structure and no broken UI artifacts.
