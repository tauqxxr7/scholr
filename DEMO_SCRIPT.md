# Scholr Demo Script

## 60-90 Second iOS-Led Walkthrough

This version matches the current strongest public proof path: the live mobile/iOS experience.

### 1. Problem

Open with:

"BTech students waste time jumping between search, notes, YouTube, and generic AI tools just to finish one academic task. Scholr compresses that into one focused academic intelligence flow."

### 2. Show the live product

Show:
- landing page on iPhone
- live URL
- clean mobile layout

Say:

"This is Scholr, a live academic intelligence and research assistance platform for BTech students."

### 3. Notes flow

Open `Notes`.

Prompt:
- `Operating System deadlock`

Say:

"Notes mode turns one topic into revision-ready structure instead of generic text dumping."

### 4. Doubt flow

Open `Doubt`.

Prompt:
- Subject: `DBMS`
- Question: `What is normalization and why do we use it?`

Say:

"Doubt mode is tuned for textbook-style explanation, stepwise reasoning, and exam clarity."

### 5. Research flow

Open `Research`.

Prompt:
- `Machine Learning for traffic prediction`

Say:

"Research mode frames subtopics, search directions, and project-worthy angles instead of just summarizing."

### 6. Fallback Academic Mode

If runtime mode is degraded, show the mode badge.

Say:

"When the external provider is quota-degraded, Scholr still works. It shifts into Fallback Academic Mode or Provider Recovering mode and keeps the student moving instead of failing empty."

### 7. Architecture / resilience proof

Show:
- `/health`
- `/health/provider`
- `/health/generate-test`
- provider status in README or architecture docs

Say:

"Under the hood, Scholr keeps SSE streaming, provider diagnostics, cache replay, recovery, and no-empty-output guarantees active."

### 8. Closing pitch

Close with:

"Scholr is not trying to be every education product at once. It is focused on one wedge first: reliable academic intelligence for BTech students across notes, doubt solving, and research direction."

## iOS Demo Flow Checklist

1. Open landing page on iPhone Safari.
2. Show responsive navigation.
3. Open Notes and submit one prompt.
4. Show the mode badge and streamed output.
5. Open Doubt and show another answer.
6. Mention fallback resilience if provider is degraded.
7. End on the live URLs or repo proof section.

## Desktop Companion Flow

1. Start on landing page hero.
2. Open Research.
3. Show structured output.
4. Mention provider recovery and cached response behavior.
5. End on architecture docs or production evidence.
