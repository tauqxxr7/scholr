# Scholr Live Notes Sample

Captured from the live production backend on 2026-05-21.

## Runtime proof

- Route: `POST /api/notes`
- Topic: `Operating system deadlock`
- Active provider: `openrouter`
- Selected model: `google/gemini-2.0-flash-lite-001`
- Fallback scaffold detected: `No`
- First token latency: `6663 ms`
- Full completion latency: `6673 ms`
- Stream completion integrity: `[DONE] received`

## Real streamed output excerpt

```md
## Overview

Deadlock is a critical problem in operating systems where two or more processes are blocked forever, each waiting for a resource held by another.

## Conditions for Deadlock

1. **Mutual Exclusion**
   - At least one resource must be held in a non-shareable mode.
2. **Hold and Wait**
   - A process is holding at least one resource and waiting to acquire additional resources held by other processes.
3. **No Preemption**
   - Resources cannot be forcibly taken away from a process; they must be released voluntarily.
```

## Why this matters

This sample shows that live Notes generation is returning structured academic formatting with headings and bullet hierarchy, not a fallback-only revision scaffold.
