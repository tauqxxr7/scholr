# Scholr Live Research Sample

Captured from the live production backend on 2026-05-21.

## Runtime proof

- Route: `POST /api/research`
- Topic: `DBMS normalization`
- Active provider: `openrouter`
- Selected model: `google/gemini-2.0-flash-lite-001`
- Fallback scaffold detected: `No`
- First token latency: `7883 ms`
- Full completion latency: `7904 ms`
- Stream completion integrity: `[DONE] received`

## Real streamed output excerpt

```md
## 5 Key Research Papers on DBMS Normalization

Here are five influential and relevant papers related to DBMS normalization, along with summaries of their key ideas:

### 1. “A Relational Model of Data for Large Shared Data Banks” by E. F. Codd (1970)

- **Key Idea:** This seminal paper introduced the relational model, which is the foundation for normalization. Codd argued that data should be organized into tables (relations) to reduce redundancy and improve data integrity.
- **Impact:** It laid the groundwork for the development of normalization forms by highlighting the problems of data anomalies in non-relational structures.
```

## Why this matters

This sample is preserved as real production proof that Scholr returned true AI-generated research output through the OpenRouter failover path rather than the deterministic fallback scaffold.
