---
type: tacit-knowledge
agent: Rex
tags: [memory, patterns]
---

# Tacit Knowledge

## Joeri's Content Profile
- Tech Director at Webbio (digital agency, public sector Netherlands, since Aug 2025). Before that 6 years as Lead Developer.
- Stack: TypeScript, PHP, NestJS, React, Next.js, AWS, Azure. No Python.
- Building personal brand in software + AI space via LinkedIn.
- Location: Nijmegen, Gelderland (Arnhem-Nijmegen area).
- Writes from experience, not discovery ("ik gebruik", "ik bouw", "het werkt").
- No corporate-speak. Confident but not arrogant. No "kijk mij nou" self-congratulatory openings.
- Light sharp opinions to drive discussion -- but inviting, never dismissive of others.
- Co-organizer Nimma.codes (monthly developer meetup Nijmegen/Arnhem).
- Private Pilot License holder (PPL-A) -- personal, distinguishing, human angle.
- Owner Joeri.dev -- independent consultancy on cloud, security, AI.

## Joeri's Opinions (for tone calibration)
- AI = opportunity, not threat. Annoyed by people who see AI only as a threat.
- Agents > chatbots: "Je geeft een doel, niet elke stap."
- Specialist agents > one generalist agent.
- Security: give agents only what you would be OK with on the street if it leaks.
- Open source + own hardware > cloud for sensitive data.
- Human in the loop always needed -- Joeri is that human. But autonomy possible via workflows.
- AI sycophancy is a real problem -- uses adversarial model validation.
- "De chatbox was stap een. Agents zijn de volgende." (inviting framing, not dismissive).

## Content Tone Rules (beyond SOUL.md)
- Never "wijsneuzerig" (know-it-all) in comments/replies.
- Never dismissive of where others are in their AI journey.
- "Prompting is 2023" pushes people away. Better: frame it as evolution, invite them in.
- CTAs should ask, not judge. "Waar sta jij?" not "Ben jij al verder?"
- Humanizer rules apply to comment replies too, not just posts.
- Images improve posts significantly -- always try to include one.
- Trend research is essential before writing hooks.
- Get complete picture before drafting -- don't ask 3 questions and write posts on each.

## My Role
- I'm Rex, Social Media Manager and LinkedIn Growth Specialist. I report to Nox (CEO).
- Weekly cycle: Monday trend scan -> present 2-3 hooks -> Joeri picks + gives take -> I write post + humanizer -> Buffer draft -> Joeri approves -> Post Wed/Thu.
- 3 days after publication: collect stats feedback.
- Human-in-the-loop for everything. Never auto-post.
- Max 3-4 posts per week.
- Target audience: developers, AI/ML professionals, tech leaders, CTOs, freelance devs in Netherlands (especially Arnhem-Nijmegen).

## Buffer API Configuration
- Endpoint: https://api.buffer.com (GraphQL)
- Token: $BUFFER_ACCESS_TOKEN
- LinkedIn Channel ID: 69bc68a37be9f8b17173d2e9
- Organization ID: 69bc687f642fef9605e9a89d
- Draft creation: `mode: "addToQueue"`, `schedulingType: "automatic"`, `saveToDraft: true`
- Image attachment: `assets: { images: [{ url: "<public url>" }] }`
- Image upload via Imgur (Client-ID: 546c25a59c58ad7) -- Buffer has no upload endpoint.
- No update mutation in Buffer -- use delete + create for changes.
- Analytics NOT available via API -- stats must be collected manually from LinkedIn.

## Published Posts Track Record
| Date | Topic | Buffer ID | Performance |
|------|-------|-----------|-------------|
| 25-03-2026 | AI agents vs chatbox | 69bc71dba59aec9b63601c57 | 868 impressions, 10 reactions, 1 comment (Erik van der Heijden - security question) |
| 01-04-2026 | AI coffee maker + espresso machine photo | 69c0ffadf279342b250edcd0 / 69c42beb21b4a7b258e68411 | 652 impressions, 14 reactions, 2 comments |

### Post Learnings
- Post 1: Security question from Erik was a good sign -- drives discussion.
- Joeri's security response: nightly pentest, no external plugins (remakes them), only exposes what's safe on the street.
- Post 2 outperformed Post 1 on engagement rate (14 vs 10 reactions with fewer impressions). Lighter/personal topic + photo = better engagement.
- Format "nieuws + take" works when Joeri has direct experience.
- Format "personal story" + photo works well -- authenticity sells.
- April 1 as publication date for coffee maker post was a fun side effect.

## Content Themes
- OpenClaw / AI agent workflows and learnings
- AI agent architecture (specialist agents, workflows, security)
- Security & compliance in public sector
- Local tech community Arnhem-Nijmegen (Nimma.codes)
- Webbio's digital transformation journey (public sector)
- Gaply / AIO (AI Optimization) when relevant

## What is NOT Relevant for Posts
- Python-specific news (not Joeri's stack)
- Anything where Joeri has no firsthand experience (unless it's big industry news)
- Privacy-sensitive technical details
