# Scholr Demo Script

## 60–90 Second Walkthrough

### 1. Problem setup

Open with:

"BTech students usually bounce between YouTube, PDFs, notes apps, and generic AI chats just to solve one academic task. Scholr compresses that into one academic intelligence workflow."

### 2. Show the live app

Show:
- landing page
- live URL
- one-line product pitch

Say:

"This is Scholr, a live academic intelligence and research assistance platform for BTech students."

### 3. Notes flow

Open `Notes`.

Prompt:
- `Operating System deadlock`

Say:

"Instead of a generic answer, Scholr structures revision notes for exam prep, viva, and fast recall."

### 4. Doubt flow

Open `Doubt`.

Prompt:
- Subject: `DBMS`
- Question: `What is normalization and why do we use it?`

Say:

"For confusion-heavy topics, Scholr turns the question into a readable, step-by-step explanation."

### 5. Research flow

Open `Research`.

Prompt:
- `Machine Learning for traffic prediction`

Say:

"Research mode is not just summarization. It frames subtopics, paper directions, and project-worthy angles."

### 6. Fallback Academic Mode

Show a runtime mode badge if the provider is degraded.

Say:

"Even when the external model is quota-degraded, Scholr doesn’t collapse into a blank error. It shifts into Fallback Academic Mode and still gives useful academic structure."

### 7. Architecture / resilience proof

Show:
- `/health`
- `/health/provider`
- `/health/generate-test`
- repo docs

Say:

"Under the hood, Scholr has SSE streaming, provider validation, background recovery, cache replay, rate limiting, and structured fallback behavior."

### 8. Closing pitch

Close with:

"Scholr is not trying to be every education product. It is focused on one wedge first: useful academic intelligence for BTech students across research, notes, and doubt solving."

## Mobile Demo Flow

1. Open landing page on iPhone or Android.
2. Open Notes.
3. Submit a prompt.
4. Show that output appears immediately and the runtime badge explains the mode.
5. Switch to Doubt.
6. End on the fact that mobile remains usable even during provider degradation.

## Desktop Demo Flow

1. Start on landing page hero.
2. Open Research.
3. Show streaming output.
4. Mention cache and fallback behavior.
5. Open Dashboard or Notes.
6. End on architecture docs or provider health.
