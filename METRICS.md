# Scholr Metrics

This document tracks measurable product and runtime proof without inventing data.

## Live surfaces

- Frontend: [https://scholr-coral.vercel.app](https://scholr-coral.vercel.app)
- Backend health: [https://scholr-k9sj.onrender.com/health](https://scholr-k9sj.onrender.com/health)
- Provider health: [https://scholr-k9sj.onrender.com/health/provider](https://scholr-k9sj.onrender.com/health/provider)
- Generation smoke test: [https://scholr-k9sj.onrender.com/health/generate-test](https://scholr-k9sj.onrender.com/health/generate-test)

## Product metrics to collect

- student sessions per day
- module opens per day
- generation started count
- generation completed count
- generation failed count
- fallback activation rate
- cache hit rate
- first token latency
- provider recovery success count
- repeat usage within 7 days

## Validation metrics to collect

- 10 students tested
- 5 return for a second session
- 3 use more than one module
- 2 explicitly say it saves time
- 1 says they would pay

## Known current limitation

- external Gemini quota and provider-model availability still affect whether requests run in true AI Mode or resilience-backed fallback mode
