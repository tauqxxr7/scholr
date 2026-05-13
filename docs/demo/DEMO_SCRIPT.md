# Scholr Demo Recording Script

Use this script to record a clean 10 to 15 second walkthrough for recruiters.

## Goal

Show one complete student workflow from landing page to AI output without extra navigation noise.

Expected output file:

`docs/demo/scholr-walkthrough.gif`

## Recording Flow

1. Open the live app: `https://scholr-coral.vercel.app`
2. Start on the dashboard or landing page with the three modules visible.
3. Open one strong demo path:
   - `Notes`, or
   - `Doubt`
4. Paste a prepared input prompt.
5. Trigger generation.
6. Wait until the AI response area is clearly visible.
7. Scroll only if needed to show the final result or recent history.

## Recommended Demo Prompt

For Notes:

```text
Create revision notes on database normalization for a BTech student. Cover 1NF, 2NF, 3NF, BCNF, common anomalies, and one practical example.
```

For Doubt:

```text
Explain gradient descent in simple language for a BTech AI student. Include intuition, one example, and why the learning rate matters.
```

## Recording Tips

- Record at `1280x720`
- Keep the demo between `10` and `15` seconds
- Avoid cursor wandering
- Avoid switching tabs
- Use one successful flow only
- Let the final output stay visible for at least `2` seconds

## Suggested Sequence

1. Show landing or dashboard
2. Open module
3. Paste prompt
4. Click generate
5. Show response area
6. Briefly show learning history if already present

## Export Guidance

- Prefer MP4 first for quality
- Convert to GIF only for README embedding if needed
- Keep file size reasonable for GitHub rendering
