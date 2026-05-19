# Scholr Engineering Decisions

## Why Next.js + FastAPI

- Next.js gives a polished product shell, routing, metadata, and deploys cleanly on Vercel.
- FastAPI keeps backend code compact, readable, and easy to expose as typed API routes.
- This split keeps the frontend product experience strong while leaving the backend easy to reason about.

## Why Shared Module UI

Research, Notes, and Doubt use the same page shell because:

- UX stays consistent
- error/loading/copy/retry behavior stays aligned
- product polish improves faster when one shared surface is upgraded

## Why SSE Instead of Polling

- lower perceived latency
- cleaner streaming UX for long academic answers
- simpler than full websocket infrastructure for this MVP

## Why Short-TTL Cache Replay

- repeated academic prompts are common
- cache replay protects Gemini quota and improves responsiveness
- using the existing history table avoided extra infrastructure

Tradeoff:
- cache freshness is limited
- the 15-minute window is intentionally conservative

## Why In-Memory Rate Limiting

- low complexity
- zero new infrastructure
- enough to protect a Render-hosted MVP from obvious abuse

Tradeoff:
- not multi-instance safe
- should move to Redis or a platform-native control later

## Why Provider Validation + Runtime Fallback

Listing models at startup is not enough. A provider can look configured and still fail during real generation.

So Scholr now uses:

- startup generation probe
- categorized provider diagnostics
- runtime fallback to safe supported models

This is the minimum product-grade reliability layer for a live AI workflow.

## Why Not Add Auth Yet

Auth adds complexity to:

- state handling
- history ownership
- user management
- password or OAuth support
- privacy/legal obligations

The current wedge is academic usefulness, not account systems. Auth stays roadmap-only until validation proves retention.

## Why Render + Vercel For MVP

- cheapest practical hosted path
- easy monorepo split
- acceptable deployment speed for current stage

Future growth may justify Azure because Tauqeer has startup credits, but the MVP should not migrate before demand is proven.

