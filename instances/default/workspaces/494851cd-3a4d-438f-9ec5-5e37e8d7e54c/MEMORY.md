---
type: tacit-knowledge
agent: Sage
tags: [memory, patterns]
---

# Tacit Knowledge

## Team

- Nox (CEO, 23bc3620) -- manager, strategic direction, delegates
- Mitch (CTO, 467192bf) -- builds systems, Opus model, architecture + code
- Tommy (Designer/QA, 7d8b001d) -- UI/UX, reviews, Opus model
- Rex (CMO, 8db8080d) -- LinkedIn/social, Dutch content, Sonnet model
- Oscar (CFO, d1e84034) -- financials, GoCardless/ING, Sonnet model

## Joeri's Preferences

- Short, direct, no filler. Dutch directness.
- Expects autonomy: agents should proactively find and create work from goals.
- Hates idle agents with no work when goals exist.
- Quality bar: Linear/Vercel level with personality.

## Delivery Feedback Loop (JOEA-18)

I am the coordinator of the delivery loop. Every task must tie to a company goal.

```
Goals → Me (plan & assign) → Mitch (build) → Tommy (QA) → Me (goal validation) → Done
```

- I create goal-aligned tasks and assign to Mitch with clear acceptance criteria
- Mitch builds, then sets `in_review` and reassigns to Tommy
- Tommy reviews: pass → reassigns to me, fail → reassigns to Mitch
- I validate goal alignment and mark `done` (or send back if off-track)
- Only escalate to Nox for CEO-level strategic decisions
- Joeri only gets involved for required input or explicit approval

## Company Context

- joeri.dev: Joeri's personal company, side consulting + websites for friends/family
- Also CTO at Webbio (web dev agency, public sector)
- OpenClaw was the predecessor system, being migrated to Paperclip
- Key integrations: Picnic (groceries), Buffer (LinkedIn), Tempo (hours), GoCardless (bank), Discord
